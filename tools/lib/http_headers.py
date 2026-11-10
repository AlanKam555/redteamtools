"""Read-only review of HTTP security headers on one authorised URL.

The checks follow the public guidance in the OWASP HTTP Headers Cheat Sheet
and the OWASP Secure Headers Project. They are heuristics: a missing header
is a hardening gap, and a present header can still be a weak policy.
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

from lib import __version__
from lib.banner import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, fail, require_authorized, validate_timeout

USER_AGENT = f"redteamtools-header-checker/{__version__} (authorised defensive check)"
PROBE_ORIGIN = "https://authorised-header-check.invalid"
MAX_REDIRECTS = 3
MAX_URL_LENGTH = 2048
BODY_CAP = 4096
MAX_HEADER_NAMES = 64
MAX_HEADER_CHARS = 8192

GOOD_REFERRER = {
    "no-referrer",
    "same-origin",
    "strict-origin",
    "strict-origin-when-cross-origin",
}


@dataclass
class Check:
    name: str
    status: str  # pass, warn, fail, info
    detail: str


@dataclass
class FetchResult:
    requested_url: str
    final_url: str
    status: int
    hops: list[str]
    headers: dict[str, list[str]]


def validate_url(raw: str) -> str:
    """Return a stripped http(s) URL, or raise ``ValueError``.

    Credentials, other schemes, missing hosts, control characters, over-long
    URLs, and ports outside 1-65535 are rejected before any connection.
    """
    if not isinstance(raw, str):
        raise ValueError("URL must be a string")
    candidate = raw.strip()
    if not candidate:
        raise ValueError("URL is empty")
    if len(candidate) > MAX_URL_LENGTH:
        raise ValueError(f"URL exceeds {MAX_URL_LENGTH} characters")
    if any(ord(char) < 32 for char in candidate):
        raise ValueError("URL contains control characters")
    parts = urllib.parse.urlsplit(candidate)
    if parts.scheme not in {"http", "https"}:
        raise ValueError("only http and https URLs are accepted")
    if parts.username or parts.password:
        raise ValueError("URLs with embedded credentials are rejected")
    if parts.hostname is None or parts.hostname == "":
        raise ValueError("URL is missing a host")
    # urlsplit decodes the host; reject whitespace that survived parsing.
    if any(char.isspace() for char in parts.hostname):
        raise ValueError("URL host contains whitespace")
    try:
        port = parts.port
    except ValueError as exc:
        raise ValueError("URL port is not valid") from exc
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("URL port must be between 1 and 65535")
    return candidate


def _normalise(headers: Mapping[str, str | Sequence[str]]) -> tuple[dict[str, list[str]], bool]:
    """Fold header names and cap size so one response cannot dominate the process.

    The boolean is true when a name or a value was dropped or shortened.
    """
    normalised: dict[str, list[str]] = {}
    limited = False
    for key, value in headers.items():
        if len(normalised) >= MAX_HEADER_NAMES and key.lower() not in normalised:
            limited = True
            continue
        values = [value] if isinstance(value, str) else list(value)
        bucket = normalised.setdefault(key.lower(), [])
        for item in values:
            text = str(item)
            if len(text) > MAX_HEADER_CHARS:
                limited = True
                text = text[:MAX_HEADER_CHARS]
            bucket.append(text)
    return normalised, limited


def _first(headers: Mapping[str, Sequence[str]], name: str) -> str | None:
    values = headers.get(name.lower())
    if not values:
        return None
    return values[0]


def _joined(headers: Mapping[str, Sequence[str]], name: str) -> str | None:
    values = headers.get(name.lower())
    if not values:
        return None
    return " ".join(values)


def _parse_directives(policy: str) -> dict[str, str]:
    directives: dict[str, str] = {}
    for part in policy.split(";"):
        item = part.strip()
        if not item:
            continue
        name, _, value = item.partition(" ")
        directives[name.lower()] = value.strip()
    return directives


def _enforcing_frame_ancestors(policy: str | None) -> bool:
    """True when CSP ``frame-ancestors`` is present and is not a wildcard source.

    Whitespace around the wildcard is collapsed. A directive of ``*``, or any
    source token that itself contains ``*``, does not count as a framing control.
    """
    if not policy:
        return False
    directives = _parse_directives(policy)
    if "frame-ancestors" not in directives:
        return False
    tokens = directives["frame-ancestors"].split()
    if not tokens:
        return False
    return not any("*" in token for token in tokens)


def _hsts_max_age(value: str) -> int | None:
    for part in value.split(";"):
        item = part.strip()
        if item.lower().startswith("max-age="):
            raw = item.split("=", 1)[1].strip().strip('"')
            if raw.isdigit():
                return int(raw)
            return None
    return None


def _cookie_assessments(set_cookies: Sequence[str]) -> list[Check]:
    checks: list[Check] = []
    for raw in set_cookies:
        pieces = [part.strip() for part in raw.split(";") if part.strip()]
        if not pieces or "=" not in pieces[0]:
            checks.append(Check("set-cookie", "info", "A Set-Cookie header could not be parsed safely."))
            continue
        name = pieces[0].split("=", 1)[0].strip()
        # Never record the cookie value. It may be a session token.
        flags = {part.split("=", 1)[0].strip().lower() for part in pieces[1:]}
        samesite = ""
        for part in pieces[1:]:
            key, sep, value = part.partition("=")
            if sep and key.strip().lower() == "samesite":
                samesite = value.strip().lower()
        problems: list[str] = []
        if "secure" not in flags:
            problems.append("Secure is absent")
        if "httponly" not in flags:
            problems.append("HttpOnly is absent")
        if not samesite:
            problems.append("SameSite is absent")
        elif samesite == "none" and "secure" not in flags:
            problems.append("SameSite=None requires Secure")
        if problems:
            status = "fail" if "SameSite=None requires Secure" in problems else "warn"
            checks.append(
                Check(
                    f"cookie:{name}",
                    status,
                    f"Cookie {name!r} flag review: {', '.join(problems)}.",
                )
            )
        else:
            checks.append(
                Check(
                    f"cookie:{name}",
                    "pass",
                    f"Cookie {name!r} sets Secure, HttpOnly, and SameSite.",
                )
            )
    return checks


def evaluate_headers(
    headers: Mapping[str, str | Sequence[str]],
    *,
    scheme: str,
    hops: Sequence[str] | None = None,
) -> list[Check]:
    """Return header findings for an already-collected response.

    `headers` maps header names to one value or a list of values. The function
    does not perform network I/O, which keeps the policy review testable.
    """
    data, limited = _normalise(headers)
    checks: list[Check] = []
    if limited:
        checks.append(
            Check(
                "header-limits",
                "info",
                f"Header review was capped at {MAX_HEADER_NAMES} names and "
                f"{MAX_HEADER_CHARS} characters per value.",
            )
        )
    scheme = scheme.lower()

    if scheme != "https":
        checks.append(
            Check(
                "transport",
                "fail",
                "The URL was requested over cleartext HTTP. Session cookies and "
                "authorization headers can be read on the path. Serve the site over "
                "HTTPS and redirect cleartext visitors before any sensitive exchange.",
            )
        )
    else:
        checks.append(Check("transport", "pass", "The final URL uses HTTPS."))

    hsts = _first(data, "strict-transport-security")
    if scheme != "https":
        checks.append(
            Check(
                "strict-transport-security",
                "info",
                "HSTS is ignored on cleartext responses. Enable it on the HTTPS response.",
            )
        )
    elif not hsts:
        checks.append(
            Check(
                "strict-transport-security",
                "fail",
                "Strict-Transport-Security is absent. Browsers will still accept a "
                "downgrade to HTTP until the user has seen HSTS.",
            )
        )
    else:
        max_age = _hsts_max_age(hsts)
        lowered = hsts.lower()
        notes: list[str] = []
        status = "pass"
        if max_age is None:
            status = "fail"
            notes.append("max-age is missing or not an integer")
        elif max_age < 15552000:
            status = "warn"
            notes.append(f"max-age={max_age} is under 180 days")
        if "includesubdomains" not in lowered:
            status = "warn" if status == "pass" else status
            notes.append("includeSubDomains is absent")
        detail = "HSTS is present."
        if notes:
            detail = "HSTS review: " + "; ".join(notes) + f". Raw value: {hsts[:180]}"
        checks.append(Check("strict-transport-security", status, detail))

    csp = _joined(data, "content-security-policy")
    report_only = _joined(data, "content-security-policy-report-only")
    if not csp and report_only:
        checks.append(
            Check(
                "content-security-policy",
                "warn",
                "Only a report-only Content-Security-Policy is present, so the browser is not enforcing it.",
            )
        )
    elif not csp:
        checks.append(
            Check(
                "content-security-policy",
                "warn",
                "Content-Security-Policy is absent. Output encoding remains the primary XSS control; "
                "CSP is the containment layer around a missed encoding.",
            )
        )
    else:
        directives = _parse_directives(csp)
        script = directives.get("script-src", directives.get("default-src", ""))
        issues: list[str] = []
        if "script-src" not in directives and "default-src" not in directives:
            issues.append("neither script-src nor default-src is set")
        token_text = script.lower()
        if "'unsafe-inline'" in token_text:
            issues.append("script policy allows 'unsafe-inline'")
        if "'unsafe-eval'" in token_text:
            issues.append("script policy allows 'unsafe-eval'")
        if "*" in script.split():
            issues.append("script policy uses a wildcard source")
        frame_ancestors = directives.get("frame-ancestors", "")
        if frame_ancestors and "*" in frame_ancestors.split():
            issues.append("frame-ancestors is a wildcard")
        status = "warn" if issues else "pass"
        detail = (
            "CSP is present and the script policy does not use the common weakeners this check looks for."
            if not issues
            else "CSP heuristic review: " + "; ".join(issues) + ". Confirm the policy in a browser."
        )
        checks.append(Check("content-security-policy", status, detail))

    nosniff = _first(data, "x-content-type-options")
    if nosniff and nosniff.strip().lower() == "nosniff":
        checks.append(Check("x-content-type-options", "pass", "X-Content-Type-Options is nosniff."))
    else:
        checks.append(
            Check(
                "x-content-type-options",
                "fail",
                "X-Content-Type-Options: nosniff is absent. Browsers may MIME-sniff a response into an executable type.",
            )
        )

    frame = (_first(data, "x-frame-options") or "").strip().upper()
    frame_ok = frame in {"DENY", "SAMEORIGIN"}
    ancestors_ok = _enforcing_frame_ancestors(csp)
    if frame_ok or ancestors_ok:
        checks.append(
            Check(
                "clickjacking-control",
                "pass",
                "A framing control is present (X-Frame-Options DENY/SAMEORIGIN and/or CSP frame-ancestors).",
            )
        )
    elif frame.startswith("ALLOW-FROM"):
        checks.append(
            Check(
                "clickjacking-control",
                "warn",
                "X-Frame-Options uses obsolete ALLOW-FROM syntax. Prefer CSP frame-ancestors.",
            )
        )
    else:
        checks.append(
            Check(
                "clickjacking-control",
                "fail",
                "Neither X-Frame-Options DENY/SAMEORIGIN nor CSP frame-ancestors is present.",
            )
        )

    referrer = (_first(data, "referrer-policy") or "").strip().lower()
    if referrer in GOOD_REFERRER:
        checks.append(Check("referrer-policy", "pass", f"Referrer-Policy is {referrer}."))
    elif not referrer:
        checks.append(
            Check(
                "referrer-policy",
                "warn",
                "Referrer-Policy is absent. Browsers will use their default, which can leak path and query data.",
            )
        )
    else:
        checks.append(
            Check(
                "referrer-policy",
                "warn",
                f"Referrer-Policy {referrer!r} is outside the strict set this check treats as appropriate.",
            )
        )

    if _first(data, "permissions-policy") or _first(data, "feature-policy"):
        checks.append(Check("permissions-policy", "pass", "A permissions policy header is present."))
    else:
        checks.append(
            Check(
                "permissions-policy",
                "info",
                "Permissions-Policy is absent. Add it when the application does not need powerful features "
                "(camera, microphone, geolocation, payment).",
            )
        )

    if _first(data, "cross-origin-opener-policy"):
        checks.append(Check("cross-origin-opener-policy", "info", "Cross-Origin-Opener-Policy is present."))
    else:
        checks.append(
            Check(
                "cross-origin-opener-policy",
                "info",
                "Cross-Origin-Opener-Policy is absent. same-origin isolates the browsing context from cross-origin openers.",
            )
        )

    acao = _first(data, "access-control-allow-origin")
    credentials = (_first(data, "access-control-allow-credentials") or "").strip().lower()
    if acao:
        reflected = acao.rstrip("/") == PROBE_ORIGIN
        if reflected and credentials == "true":
            checks.append(
                Check(
                    "cors",
                    "fail",
                    "Access-Control-Allow-Origin reflected the probe Origin and "
                    "Access-Control-Allow-Credentials is true. Review whether arbitrary sites "
                    "can make authenticated cross-origin reads.",
                )
            )
        elif acao.strip() == "*" and credentials == "true":
            checks.append(
                Check(
                    "cors",
                    "warn",
                    "Access-Control-Allow-Origin is * together with credentials. Browsers reject this combination; "
                    "the server configuration is still inconsistent.",
                )
            )
        elif acao.strip() == "*":
            checks.append(
                Check(
                    "cors",
                    "info",
                    "Access-Control-Allow-Origin is *. Any site can read the response from a non-credentialed request.",
                )
            )
        else:
            checks.append(Check("cors", "info", "A specific Access-Control-Allow-Origin value is present."))

    xss_protection = _first(data, "x-xss-protection")
    if xss_protection is not None:
        checks.append(
            Check(
                "x-xss-protection",
                "info",
                "X-XSS-Protection is deprecated. Keep output encoding and CSP; do not rely on this header.",
            )
        )

    for disclosure_name in ("server", "x-powered-by", "x-aspnet-version"):
        value = _first(data, disclosure_name)
        if value:
            checks.append(
                Check(
                    disclosure_name,
                    "info",
                    f"{disclosure_name} discloses {value[:80]!r}. Version banners help inventory and also help attackers; "
                    "remove detail you do not need.",
                )
            )

    checks.extend(_cookie_assessments(data.get("set-cookie", [])))

    if hops:
        hosts = []
        for hop in hops:
            host = urllib.parse.urlsplit(hop).hostname
            if host:
                hosts.append(host.lower())
        if len(set(hosts)) > 1:
            checks.append(
                Check(
                    "redirect-host",
                    "info",
                    "The request followed a redirect onto a different host: " + " -> ".join(hops),
                )
            )
    return checks


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(  # noqa: ANN201
        self,
        req: urllib.request.Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> urllib.request.Request | None:
        # Returning None lets another handler continue. Raising keeps the
        # redirect response so the caller can record the hop itself.
        # ``headers`` is an email.message.Message at runtime; HTTPError accepts it.
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)  # type: ignore[arg-type]


def fetch(url: str, *, timeout: float) -> FetchResult:
    """Perform one GET and up to MAX_REDIRECTS same-scheme redirects."""
    validate_url(url)
    context = ssl.create_default_context()
    opener = urllib.request.build_opener(
        urllib.request.HTTPHandler(),
        urllib.request.HTTPSHandler(context=context),
        _NoRedirect(),
    )
    current = url
    hops = [current]
    response = None
    for _ in range(MAX_REDIRECTS + 1):
        request = urllib.request.Request(
            current,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
                "Origin": PROBE_ORIGIN,
            },
            method="GET",
        )
        try:
            response = opener.open(request, timeout=timeout)
            break
        except urllib.error.HTTPError as exc:
            location = exc.headers.get("Location") if exc.headers else None
            if exc.code in {301, 302, 303, 307, 308} and location and len(hops) <= MAX_REDIRECTS:
                current = urllib.parse.urljoin(exc.geturl(), location)
                validate_url(current)
                hops.append(current)
                exc.close()
                continue
            response = exc
            break
    if response is None:
        raise OSError("no response received")
    try:
        # Security headers are on the status line. Cap the body so a large file
        # cannot be pulled into the process.
        response.read(BODY_CAP)
        header_map: dict[str, list[str]] = {}
        seen: set[str] = set()
        for key in response.headers:
            folded = key.lower()
            if folded in seen:
                continue
            seen.add(folded)
            header_map[key] = list(response.headers.get_all(key) or [])
        return FetchResult(
            requested_url=url,
            final_url=response.geturl(),
            status=getattr(response, "status", None) or response.getcode(),
            hops=hops,
            headers=header_map,
        )
    finally:
        response.close()


def _summary(checks: Sequence[Check]) -> dict[str, int]:
    counts = {"pass": 0, "warn": 0, "fail": 0, "info": 0}
    for check in checks:
        counts[check.status] = counts.get(check.status, 0) + 1
    return counts


def format_text(result: FetchResult, checks: Sequence[Check]) -> str:
    lines = [
        f"Requested: {result.requested_url}",
        f"Final:     {result.final_url}",
        f"Status:    {result.status}",
        "Hops:      " + " -> ".join(result.hops),
        "",
    ]
    for check in checks:
        lines.append(f"[{check.status.upper():4}] {check.name}: {check.detail}")
    counts = _summary(checks)
    lines.append("")
    lines.append(
        "Summary: "
        + ", ".join(f"{count} {name}" for name, count in counts.items())
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="security_header_checker",
        description=(
            "Fetch one authorised URL and review common HTTP security headers. "
            "Sends a single GET plus at most three redirects. Does not crawl, "
            "authenticate, or send attack payloads."
        ),
        epilog=(
            "Authorised use only. Pass --authorized only when you have permission "
            "to request the named URL. There is no default host.\n"
            "Exit status: 0 when no fail-level result was found, 1 when a fail-level "
            "gap was found, 2 when the arguments were refused or the request could not run.\n"
            "Guidance: https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--url", help="http(s) URL you are authorised to request")
    parser.add_argument(
        "--authorized",
        action="store_true",
        help="Attest that you are authorised to request this URL",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10,
        help="Socket timeout in seconds (1-30, default 10)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default text)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Review one URL. Exits 2 before any connection when the flag or URL is refused."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.url is None:
        parser.print_help(sys.stderr)
        print("error: missing --url", file=sys.stderr)
        return EXIT_USAGE
    # Authorisation is checked before URL use so a refused run never connects.
    require_authorized(args.authorized)
    try:
        timeout = validate_timeout(args.timeout)
        target = validate_url(args.url)
    except ValueError as exc:
        fail(str(exc))
    print(f"Target: {target}", file=sys.stderr)
    print("Authorisation flag: accepted. Sending one read-only GET.", file=sys.stderr)
    try:
        fetched = fetch(target, timeout=timeout)
    except ValueError as exc:
        fail(str(exc))
    except urllib.error.URLError as exc:
        fail(f"request failed: {exc.reason}")
    except OSError as exc:
        fail(f"request failed: {exc}")
    scheme = urllib.parse.urlsplit(fetched.final_url).scheme
    checks = evaluate_headers(fetched.headers, scheme=scheme, hops=fetched.hops)
    if args.format == "json":
        payload = {
            "requested_url": fetched.requested_url,
            "final_url": fetched.final_url,
            "status": fetched.status,
            "hops": fetched.hops,
            "checks": [asdict(check) for check in checks],
            "summary": _summary(checks),
        }
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_text(fetched, checks))
    return EXIT_FINDINGS if any(check.status == "fail" for check in checks) else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())

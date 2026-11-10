"""Read-only TLS and certificate review for one authorised host.

The probe opens a handful of handshakes to the host and port the operator
names. It reports negotiated protocol, cipher, certificate lifetime, and
whether the system trust store accepts the chain. It does not enumerate
ciphers by brute force and it does not send application-layer attacks.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import datetime as dt
import hashlib
import ipaddress
import json
import re
import socket
import ssl
import sys
import warnings
from collections.abc import Iterator, Sequence
from dataclasses import asdict, dataclass

from lib.banner import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, fail, require_authorized, validate_timeout

_HOSTNAME = re.compile(r"\A(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\Z")
WEAK_CIPHER_TOKENS = ("RC4", "NULL", "EXPORT", "DES-CBC", "3DES", "MD5", "ANON", "RC2", "IDEA")


@dataclass
class Check:
    name: str
    status: str
    detail: str


def validate_host(raw: str) -> str:
    """Return a DNS name or IP address, or raise ``ValueError``.

    A bracketed IPv6 address such as ``[::1]`` is accepted and returned
    without the brackets. Schemes, paths, ports, and whitespace are rejected.
    There is no default host.
    """
    if not isinstance(raw, str):
        raise ValueError("host must be a string")
    host = raw.strip().rstrip(".")
    if host.startswith("[") and host.endswith("]"):
        inner = host[1:-1]
        try:
            ipaddress.ip_address(inner)
        except ValueError as exc:
            raise ValueError("host is not a valid DNS name or IP address") from exc
        return inner
    if not host or len(host) > 253:
        raise ValueError("host is empty or longer than 253 characters")
    if any(ord(char) < 33 for char in host):
        raise ValueError("host contains whitespace or control characters")
    try:
        ipaddress.ip_address(host)
        return host
    except ValueError:
        pass
    try:
        ascii_host = host.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("host is not valid IDNA") from exc
    if not _HOSTNAME.fullmatch(ascii_host):
        raise ValueError("host is not a valid DNS name or IP address")
    return host


def validate_port(raw: int) -> int:
    """Return ``raw`` when it is a TCP port from 1 to 65535."""
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ValueError("port must be an integer")
    if not 1 <= raw <= 65535:
        raise ValueError("port must be between 1 and 65535")
    return raw


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def cipher_assessment(cipher_name: str | None) -> Check:
    """Classify one negotiated cipher name. This does not probe the server."""
    if not cipher_name:
        return Check("cipher", "warn", "No cipher was negotiated.")
    upper = cipher_name.upper()
    if any(token in upper for token in WEAK_CIPHER_TOKENS) or upper.endswith("_SHA"):
        # AES-GCM-SHA256 / SHA384 names contain SHA but do not end with _SHA.
        if any(token in upper for token in ("RC4", "NULL", "EXPORT", "3DES", "MD5", "ANON", "RC2", "IDEA")) or "DES-CBC" in upper:
            return Check("cipher", "fail", f"Negotiated cipher {cipher_name} is obsolete.")
        if upper.endswith("_SHA"):
            return Check(
                "cipher",
                "warn",
                f"Negotiated cipher {cipher_name} uses HMAC-SHA1. Prefer an AEAD suite.",
            )
    if "CBC" in upper:
        return Check(
            "cipher",
            "warn",
            f"Negotiated cipher {cipher_name} is CBC rather than an AEAD mode.",
        )
    return Check("cipher", "pass", f"Negotiated cipher {cipher_name}.")


def protocol_assessment(version: str | None) -> Check:
    """Classify one negotiated protocol name. TLS 1.2 and 1.3 pass."""
    if version in {"TLSv1.3"}:
        return Check("protocol", "pass", "Negotiated TLS 1.3.")
    if version in {"TLSv1.2"}:
        return Check("protocol", "pass", "Negotiated TLS 1.2.")
    if version in {"TLSv1", "TLSv1.0", "TLSv1.1"}:
        return Check("protocol", "fail", f"Negotiated obsolete protocol {version}.")
    if not version:
        return Check("protocol", "fail", "No TLS protocol was negotiated.")
    return Check("protocol", "warn", f"Negotiated unrecognised protocol {version}.")


def certificate_window(
    not_before: dt.datetime, not_after: dt.datetime, now: dt.datetime
) -> list[Check]:
    """Classify a certificate validity window relative to ``now``."""
    checks = []
    if not_before > now:
        checks.append(Check("certificate-validity", "fail", "Certificate is not valid yet."))
    elif not_after < now:
        checks.append(
            Check(
                "certificate-validity",
                "fail",
                f"Certificate expired at {not_after.isoformat()}.",
            )
        )
    elif not_after < now + dt.timedelta(days=30):
        checks.append(
            Check(
                "certificate-validity",
                "warn",
                f"Certificate expires within 30 days ({not_after.date().isoformat()}).",
            )
        )
    else:
        checks.append(
            Check(
                "certificate-validity",
                "pass",
                f"Certificate is valid until {not_after.date().isoformat()}.",
            )
        )
    return checks


def parse_cert_time(value: str) -> dt.datetime:
    """Parse the timestamp format returned by ssl.SSLSocket.getpeercert."""
    parsed = dt.datetime.strptime(value, "%b %d %H:%M:%S %Y %Z")
    return parsed.replace(tzinfo=dt.timezone.utc)


def _read_length(data: bytes, index: int) -> tuple[int, int]:
    if index >= len(data):
        raise ValueError("truncated ASN.1 length")
    first = data[index]
    index += 1
    if first < 0x80:
        return first, index
    count = first & 0x7F
    if count == 0 or count > 3 or index + count > len(data):
        raise ValueError("unsupported ASN.1 length")
    length = int.from_bytes(data[index : index + count], "big")
    return length, index + count


def _iter_tlv(data: bytes, start: int, end: int) -> Iterator[tuple[int, int, int]]:
    index = start
    while index < end:
        tag = data[index]
        index += 1
        length, index = _read_length(data, index)
        value_end = index + length
        if value_end > end:
            raise ValueError("ASN.1 value exceeds buffer")
        yield tag, index, value_end
        index = value_end


def extract_validity(der: bytes) -> tuple[dt.datetime, dt.datetime] | None:
    """Return notBefore and notAfter when the certificate parses cleanly.

    The first two ASN.1 Time values inside a certificate are the validity
    window. The function returns None rather than guessing when the encoding
    is not the shape it understands.
    """
    try:
        outer = list(_iter_tlv(der, 0, len(der)))
        if not outer or outer[0][0] != 0x30:
            return None
        times: list[dt.datetime] = []

        def walk(start: int, end: int, depth: int) -> None:
            if depth > 8 or len(times) >= 2:
                return
            for tag, value_start, value_end in _iter_tlv(der, start, end):
                if tag in {0x17, 0x18}:
                    raw = der[value_start:value_end]
                    times.append(_decode_time(tag, raw))
                    if len(times) >= 2:
                        return
                elif tag in {0x30, 0x31} or tag & 0xE0 == 0xA0:
                    walk(value_start, value_end, depth + 1)
                    if len(times) >= 2:
                        return

        walk(outer[0][1], outer[0][2], 0)
    except (ValueError, UnicodeError, IndexError):
        return None
    if len(times) < 2:
        return None
    return times[0], times[1]


def _decode_time(tag: int, raw: bytes) -> dt.datetime:
    text = raw.decode("ascii")
    if tag == 0x17:  # UTCTime, YYMMDDHHMMSSZ
        year = int(text[0:2])
        year += 2000 if year < 50 else 1900
        parsed = dt.datetime(
            year,
            int(text[2:4]),
            int(text[4:6]),
            int(text[6:8]),
            int(text[8:10]),
            int(text[10:12]),
            tzinfo=dt.timezone.utc,
        )
        return parsed
    # GeneralizedTime YYYYMMDDHHMMSSZ
    return dt.datetime.strptime(text[:14], "%Y%m%d%H%M%S").replace(tzinfo=dt.timezone.utc)


def pem_to_der(pem: str) -> bytes:
    body = "".join(line for line in pem.splitlines() if not line.startswith("-----"))
    try:
        return base64.b64decode(body, validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("certificate PEM is not valid base64") from exc


def fingerprint(der: bytes) -> str:
    digest = hashlib.sha256(der).hexdigest()
    return ":".join(digest[index : index + 2] for index in range(0, len(digest), 2))


def _server_hostname(host: str) -> str | None:
    return None if _is_ip(host) else host


def _handshake(
    host: str,
    port: int,
    timeout: float,
    *,
    minimum: ssl.TLSVersion | None = None,
    maximum: ssl.TLSVersion | None = None,
    verify: bool = True,
    cadata: str | None = None,
) -> tuple[ssl.SSLSocket, socket.socket]:
    if verify and cadata is None:
        context = ssl.create_default_context()
        if _is_ip(host):
            # An address is not a DNS name. Chain validation still runs;
            # name binding is reported separately.
            context.check_hostname = False
    else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if verify:
            context.check_hostname = not _is_ip(host)
            context.verify_mode = ssl.CERT_REQUIRED
            if cadata:
                context.load_verify_locations(cadata=cadata)
        else:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
    if minimum is not None or maximum is not None:
        # Probing TLS 1.0/1.1 trips a deprecation warning. The probe exists
        # to detect servers that still accept those protocols.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            if minimum is not None:
                context.minimum_version = minimum
            if maximum is not None:
                context.maximum_version = maximum
    if not verify:
        # Older protocol probes need a cipher list the default security level may hide.
        # A stack that rejects the list is reported by the handshake, not by this call.
        with contextlib.suppress(ssl.SSLError):
            context.set_ciphers("ALL:@SECLEVEL=0")
    sock = socket.create_connection((host, port), timeout=timeout)
    try:
        tls = context.wrap_socket(sock, server_hostname=_server_hostname(host))
    except Exception:
        sock.close()
        raise
    return tls, sock


def legacy_probe(host: str, port: int, timeout: float, version: ssl.TLSVersion) -> Check:
    label = {ssl.TLSVersion.TLSv1: "TLS 1.0", ssl.TLSVersion.TLSv1_1: "TLS 1.1"}[version]
    try:
        tls, _sock = _handshake(
            host,
            port,
            timeout,
            minimum=version,
            maximum=version,
            verify=False,
        )
    except (ssl.SSLError, ValueError) as exc:
        text = str(exc)
        if (
            "NO_PROTOCOLS_AVAILABLE" in text
            or "unsupported protocol" in text.lower()
            or "disabled" in text.lower()
        ):
            return Check(
                f"legacy-{label.replace(' ', '-').lower()}",
                "info",
                f"{label} probe was inconclusive because the local TLS stack refused to offer it ({text[:180]}).",
            )
        return Check(
            f"legacy-{label.replace(' ', '-').lower()}",
            "pass",
            f"The server did not complete a {label} handshake.",
        )
    except OSError as exc:
        return Check(
            f"legacy-{label.replace(' ', '-').lower()}",
            "warn",
            f"{label} probe could not connect: {exc}",
        )
    else:
        try:
            negotiated = tls.version()
        finally:
            tls.close()
        return Check(
            f"legacy-{label.replace(' ', '-').lower()}",
            "fail",
            f"The server accepted a {label} handshake ({negotiated}). Disable TLS 1.0 and 1.1.",
        )


def assess(host: str, port: int, timeout: float, *, now: dt.datetime | None = None) -> list[Check]:
    """Connect to one host and return configuration findings."""
    host = validate_host(host)
    port = validate_port(port)
    now = now or dt.datetime.now(dt.timezone.utc)
    checks: list[Check] = []

    try:
        pem = ssl.get_server_certificate((host, port), timeout=timeout)
        der = pem_to_der(pem)
    except (OSError, ValueError, ssl.SSLError) as exc:
        return [Check("handshake", "fail", f"Could not retrieve a certificate: {exc}")]

    checks.append(Check("certificate-fingerprint", "info", f"SHA-256 {fingerprint(der)}"))
    validity = extract_validity(der)
    if validity:
        checks.extend(certificate_window(validity[0], validity[1], now))
    else:
        checks.append(
            Check(
                "certificate-validity",
                "warn",
                "A certificate was presented but its validity dates could not be parsed.",
            )
        )

    if _is_ip(host):
        checks.append(
            Check(
                "name-check",
                "info",
                "The target is an IP address, so the certificate was not matched to a DNS name. "
                "Connect by the in-scope hostname when you need that binding checked.",
            )
        )

    try:
        tls, _sock = _handshake(host, port, timeout, verify=True)
    except ssl.SSLError as exc:
        checks.append(
            Check(
                "trust",
                "fail",
                "System trust verification failed: " + str(exc).splitlines()[0][:300],
            )
        )
        # Still record what an unverified handshake negotiates, clearly labelled.
        try:
            tls, _sock = _handshake(host, port, timeout, verify=False)
        except (OSError, ssl.SSLError) as inner:
            checks.append(Check("protocol", "warn", f"Unverified handshake failed: {inner}"))
            tls = None
    except (OSError, ValueError) as exc:
        checks.append(Check("trust", "fail", f"Connection failed: {exc}"))
        tls = None
    else:
        checks.append(Check("trust", "pass", "The certificate chain is trusted by this system's CA store."))

    if tls is not None:
        try:
            checks.append(protocol_assessment(tls.version()))
            cipher = tls.cipher()
            checks.append(cipher_assessment(cipher[0] if cipher else None))
            peer = tls.getpeercert()
            if peer:
                sans = peer.get("subjectAltName") or []
                names = [value for kind, value in sans if kind in {"DNS", "IP Address"}]
                if names:
                    shown = ", ".join(names[:12])
                    extra = "" if len(names) <= 12 else f" (+{len(names) - 12} more)"
                    checks.append(Check("subject-alt-name", "info", shown + extra))
                subject = _dn(peer.get("subject"))
                issuer = _dn(peer.get("issuer"))
                if subject:
                    checks.append(Check("subject", "info", subject))
                if issuer:
                    checks.append(Check("issuer", "info", issuer))
                    if subject and subject == issuer:
                        checks.append(
                            Check(
                                "self-signed",
                                "warn",
                                "Subject and issuer are the same. Confirm this is an intended private CA or a lab certificate.",
                            )
                        )
        finally:
            tls.close()

    for version in (ssl.TLSVersion.TLSv1, ssl.TLSVersion.TLSv1_1):
        checks.append(legacy_probe(host, port, timeout, version))
    return checks


def _dn(pairs: Sequence[Sequence[tuple[str, str]]] | None) -> str:
    if not pairs:
        return ""
    parts = []
    for group in pairs:
        for key, value in group:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def format_text(host: str, port: int, checks: Sequence[Check]) -> str:
    lines = [f"Host: {host}", f"Port: {port}", ""]
    for check in checks:
        lines.append(f"[{check.status.upper():4}] {check.name}: {check.detail}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tls_config_checker",
        description=(
            "Review the TLS certificate and negotiated protocol of one authorised host. "
            "Opens a small number of handshakes and does not crawl or authenticate."
        ),
        epilog=(
            "Authorised use only. Pass --authorized only when you have permission "
            "to connect to the named host. There is no default host.\n"
            "Exit status: 0 when no fail-level result was found, 1 when a fail-level "
            "gap was found, 2 when the arguments were refused or the check could not run.\n"
            "Guidance: https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--host",
        help="DNS name or IP you are authorised to connect to (no scheme, no port)",
    )
    parser.add_argument("--port", type=int, default=443, help="TCP port (1-65535, default 443)")
    parser.add_argument(
        "--authorized",
        action="store_true",
        help="Attest that you are authorised to connect to this host",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10,
        help="Per-connection timeout in seconds (1-30, default 10)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default text)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Review one host. Exits 2 before any connection when the flag or host is refused."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.host is None:
        parser.print_help(sys.stderr)
        print("error: missing --host", file=sys.stderr)
        return EXIT_USAGE
    # Authorisation is checked before host use so a refused run never connects.
    require_authorized(args.authorized)
    try:
        timeout = validate_timeout(args.timeout)
        host = validate_host(args.host)
        port = validate_port(args.port)
    except ValueError as exc:
        fail(str(exc))
    print(f"Target: {host}:{port}", file=sys.stderr)
    print("Authorisation flag: accepted. Opening a few read-only TLS handshakes.", file=sys.stderr)
    try:
        checks = assess(host, port, timeout)
    except (OSError, ssl.SSLError, ValueError) as exc:
        fail(f"review failed: {exc}")
    if args.format == "json":
        json.dump(
            {"host": host, "port": port, "checks": [asdict(check) for check in checks]},
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        sys.stdout.write(format_text(host, port, checks))
    return EXIT_FINDINGS if any(check.status == "fail" for check in checks) else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())

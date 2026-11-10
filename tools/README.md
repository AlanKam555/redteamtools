# Defensive utilities

> Authorised use only. [Disclaimer](../DISCLAIMER.md) · [Security policy](../SECURITY.md) · [Repository index](../README.md) · [Licence](../LICENSE) · [Contributing](../CONTRIBUTING.md)

Four small programs for an authorised assessment. They are deliberately narrow.

| Program | What it does | Network |
| --- | --- | --- |
| `security_header_checker.py` | Reviews common HTTP security headers on one URL. | One GET, plus at most three redirects. |
| `tls_config_checker.py` | Reviews the certificate, trust, negotiated protocol, and whether TLS 1.0 or 1.1 is still accepted. | A handful of handshakes to one host and port. |
| `report_skeleton.py` | Writes a Markdown report draft under the current directory. | None. |
| `scope_roe_validator.py` | Checks a local rules-of-engagement file for required decisions and leftover placeholders. | None. |

Runtime dependencies: none. Python 3.10 or newer is enough. `requirements.txt` and the repository [pyproject.toml](../pyproject.toml) record that on purpose (`dependencies` is empty). Ruff is a development linter only. The tools do not import it. The package version is `1.1.0` (`tools/lib/__init__.py`).

## Authorised use

The two network tools print an authorised-use banner and exit unless you pass `--authorized`. Pass that flag only after you have permission to connect to the target you are about to name. There is no default host. A URL with an embedded username or password is rejected so secrets are not placed on a command line that ends up in a shell history.

```bash
python3 tools/security_header_checker.py --help
python3 tools/security_header_checker.py \
  --url https://app.example.com/ \
  --authorized \
  --format text

python3 tools/tls_config_checker.py \
  --host app.example.com \
  --port 443 \
  --authorized
```

Replace `app.example.com` with a host that is inside your rules of engagement. The examples above are placeholders.

| Exit status | Meaning |
| --- | --- |
| `0` | The check finished with no fail-level result, the report draft was written, or the rules file is complete enough to read. |
| `1` | The check finished and found a fail-level gap, or the rules file is not ready. |
| `2` | The arguments were refused, or the check could not run. A missing `--authorized` on a network tool is this status, and no connection is opened. |

The report generator does not use status `1`. A rules file that cannot be read (missing, wrong type, too large, not UTF-8) is status `2`, not `1`.

## What the header check looks at

The review follows the public recommendations in the [OWASP HTTP Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html) and the [Transport Layer Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html). It is a heuristic, not a proof that the application is safe.

- Cleartext HTTP is reported as a failure.
- HSTS on HTTPS is required, with a warning when `max-age` is short or `includeSubDomains` is missing.
- `X-Content-Type-Options: nosniff` is required.
- Clickjacking protection is required, either `X-Frame-Options` of `DENY` or `SAMEORIGIN`, or a CSP `frame-ancestors` directive.
- Content-Security-Policy is reported, including a warning when the script policy uses `'unsafe-inline'`, `'unsafe-eval'`, or a wildcard source.
- Referrer-Policy, Permissions-Policy, cookie flags, and a single CORS probe are reported.
- Cookie values are never printed. A `Set-Cookie` header is reduced to the cookie name and the flags.
- The request sends `Origin: https://authorised-header-check.invalid`. If the server reflects that origin and allows credentials, the check fails. One probe origin is enough to see a reflective configuration. The tool does not try a list of origins.

The response body is capped at a few kilobytes, and header scoring stops after 64 names and 8192 characters per value so one response cannot dominate the process. A redirect is followed only when the next URL still passes the same checks, including the ban on embedded credentials, and only up to three hops. The tool does not crawl, authenticate, or send a second request with a different path of its own. A wildcard `frame-ancestors` source, including one hidden by extra spaces, does not count as clickjacking protection.

## What the TLS check looks at

- Retrieves the presented certificate and prints its SHA-256 fingerprint.
- Reads the validity window from the certificate.
- Attempts a handshake verified against the system trust store.
- Records the negotiated protocol and cipher. Obsolete ciphers fail. CBC and HMAC-SHA1 suites warn. TLS 1.2 and 1.3 pass.
- Attempts one handshake each for TLS 1.0 and TLS 1.1. If the server completes either handshake, that is a failure. If the local OpenSSL build refuses to offer the old protocol, the result is reported as inconclusive rather than as a pass.
- When you pass an IP address, chain validation still runs, and the tool says that a DNS name was not checked. Prefer the in-scope hostname.

A self-signed certificate, an incomplete chain, an expired certificate, or a hostname mismatch fails the trust check. That is the configuration finding. The tool does not disable trust in order to hide the failure, and it does not offer a mode that "fixes" the connection.

Submitting the same host to a third-party grader such as [SSL Labs](https://www.ssllabs.com/projects/rating-guide/) or [Mozilla Observatory](https://observatory.mozilla.org/) is a separate decision: the hostname leaves your engagement. Do that only when the client has agreed.

## Report skeleton

```bash
python3 tools/report_skeleton.py \
  --client "Example Corp" \
  --engagement "External web assessment" \
  --start 2026-11-01 \
  --end 2026-11-08 \
  --author "Alan" \
  --output reports/example-draft.md
```

The output path has to stay inside the current working directory. An existing file is left alone unless you pass `--force`. Control characters in the names are rejected. The draft points at `templates/` for the long-form finding and executive-summary structure. It does not contact the client or the target.

## Rules-of-engagement checker

```bash
python3 tools/scope_roe_validator.py --file templates/examples/completed-rules-of-engagement.md
python3 tools/scope_roe_validator.py --file path/to/roe.md
python3 tools/scope_roe_validator.py --file path/to/roe.json
```

Markdown files need these second-level headings: Authorization, In-scope assets, Out of scope, Allowed methods, Prohibited activities, Schedule, Emergency contacts, Data handling, Acknowledgement. "Authorisation" is accepted as the same section. Empty sections, a scope of "none", and placeholders such as `TODO`, `TBD`, or `[Client legal name]` fail the check.

JSON files need the same decisions as fields. Dates are `YYYY-MM-DD`, and the window has to end on or after it starts. A passing result means the document is complete enough to read. It does not mean the engagement is lawful.

The blank template at `templates/rules-of-engagement.md` fails this check until the placeholders are replaced. That is intentional. The completed example passes.

## Tests

```bash
python3 -m unittest discover -s tools/tests -v
```

The tests cover header classification, URL rejection, a local HTTP redirect, TLS classification, certificate-date parsing, a TLS handshake to a local self-signed listener, report-path confinement, and the rules-of-engagement checks. They do not contact an external host.

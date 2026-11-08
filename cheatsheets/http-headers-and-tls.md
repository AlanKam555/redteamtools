# HTTP headers and TLS

These checks are defensive configuration review. They do not show that the application encodes output or authorizes objects. They show whether the browser and the transport are being asked to help.

The utilities in this repository do the review with one URL or one host, an authorisation flag, and no payload:

```bash
python3 tools/security_header_checker.py --url https://TARGET/ --authorized
python3 tools/tls_config_checker.py --host TARGET --port 443 --authorized
```

`TARGET` is a placeholder for an in-scope name. Both tools print an authorised-use banner and refuse embedded credentials in a URL. See [tools/README.md](../tools/README.md) for the exact checks and the exit codes.

## What a pass usually means

| Control | Pass looks like | Primary reference |
| --- | --- | --- |
| TLS version | 1.2 or 1.3, and 1.0/1.1 not accepted | [TLS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html) |
| Certificate | Trusted chain, correct name, not expired | same |
| HSTS | Present on HTTPS, long `max-age`, `includeSubDomains` when the whole zone is HTTPS | [HTTP Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html) |
| Content type | `X-Content-Type-Options: nosniff` | same |
| Framing | `X-Frame-Options` of `DENY` or `SAMEORIGIN`, or CSP `frame-ancestors` | same |
| CSP | A policy without `unsafe-inline` or `unsafe-eval` in script | [CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html) |
| Cookies | `Secure`, `HttpOnly`, and an explicit `SameSite` on the session | [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) |
| Referrer | A strict referrer policy | HTTP Headers Cheat Sheet |

A missing CSP is a containment gap, not an XSS proof. Say that in the finding so the client does not "fix" XSS by adding a header and leaving the encoder off.

## A manual equivalent

When you want to see the headers yourself:

```bash
curl -sS -D - -o /dev/null --max-redirs 0 https://TARGET/
```

`--max-redirs 0` shows the first response, which is often the redirect that should already be HTTPS. The header checker follows up to three redirects and lists the hops, because HSTS has to be on the HTTPS response, not on the cleartext redirect.

Do not send session cookies with `curl` while you are "just checking headers". You do not need them, and they end up in your shell history.

## Third-party graders

[SSL Labs' rating guide](https://www.ssllabs.com/projects/rating-guide/) and [Mozilla Observatory](https://observatory.mozilla.org/) grade a public hostname from their infrastructure. Submitting a name sends that name to a third party. Do it only when the client has agreed, and do not submit internal names.

## What to write down

- The final URL, the status, and the fail-level rows from the tool.
- Whether the check was against production or staging, and the date.
- Headers you intentionally accepted (a CSP that must allow a specific analytics host) and the person who accepted them.

## Official documentation

- OWASP HTTP Headers Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html>
- OWASP Transport Layer Security Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html>
- OWASP Content Security Policy Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html>

# Cheatsheets

> Authorised use only. [Disclaimer](../DISCLAIMER.md) · [Security policy](../SECURITY.md) · [Repository index](../README.md) · [Licence](../LICENSE) · [Contributing](../CONTRIBUTING.md)

Short usage notes for tools that show up in authorised assessments. Each note says what the tool is for, a conservative way to run it, what to record, and where the official manual is. They are not an attack procedure and they are not a payload list.

Run them only against assets named in the current rules of engagement, inside the window, at a rate the target can survive. A command with `TARGET` in it is a placeholder. Substitute a host you are allowed to test, or do not run it.

| Note | Tool |
| --- | --- |
| [Nmap](nmap.md) | Host and service discovery. |
| [ffuf](ffuf.md) | HTTP content discovery at a capped rate. |
| [Nuclei](nuclei.md) | Template-based checks, with intrusive categories excluded unless the rules allow them. |
| [Burp Suite](burp-suite.md) | The manual-testing workflow. OWASP ZAP is the free alternative. |
| [HTTP headers and TLS](http-headers-and-tls.md) | The defensive checks, including the utilities in `tools/`. |

The defensive utilities are documented in [tools/README.md](../tools/README.md). Prefer them when the question is "what headers and TLS settings does this one host present", because they are read-only and they refuse to run without an authorisation flag.

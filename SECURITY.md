# Security policy

## Authorised use

The utilities in this repository are defensive aids. Use them only on systems you own or are explicitly authorised to assess. The network tools require an `--authorized` flag because a hostname typed on a command line is not, by itself, proof of permission. The flag is an operator attestation. It is not a technical control that can make an unlawful scan lawful.

Do not point the tools at customers, suppliers, or neighbouring infrastructure unless that exact asset is inside a current authorisation.

## Reporting a problem in this repository

If you find a defect in these documents or utilities — a broken check, a dangerous default, an incorrect citation, or a script that does more than it claims — report it to the maintainer through a private GitHub security advisory on [AlanKam555/redteamtools](https://github.com/AlanKam555/redteamtools), or by opening an issue if the defect is already obvious from the public source and does not include sensitive data.

Include:

- The file or command involved.
- The behaviour you expected and the behaviour you saw.
- The Python version and operating system, for tool defects.

## What not to send

Do not send exploit payloads, malware, stolen credentials, session cookies, packet captures from a real engagement, or proof-of-concept code that compromises a system. A description of the defect is enough. If a sample request or response is useful, replace hosts, tokens, and personal data with placeholders.

This repository is not a bug-bounty programme for third-party products, and the maintainer cannot accept vulnerability reports about systems that belong to other organisations. Report those to the system owner, following their published disclosure policy. [OWASP's Vulnerability Disclosure Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html) describes the general responsible-disclosure practice.

## Supported use of the tools

| Tool | Intended behaviour |
| --- | --- |
| `security_header_checker.py` | One HTTP GET (plus a few redirects) to a URL you name. Reads response headers. |
| `tls_config_checker.py` | A handful of TLS handshakes to a host and port you name. Reads certificate and negotiated parameters. |
| `report_skeleton.py` | Writes a Markdown file under the current directory. No network access. |
| `scope_roe_validator.py` | Reads a local rules-of-engagement file and reports missing sections. No network access. |

The tools do not discover hosts, do not brute-force credentials, do not send exploit payloads, and do not include a target of their own.

## Disclosure of engagement findings

Findings from a real assessment belong to the client. Store them under the engagement's data-handling rules. Do not commit them to this repository, and do not publish them because a template in `templates/` happens to be public.

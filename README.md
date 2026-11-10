# Red team and penetration-testing reference

> **Authorised use only.** This is a methodology and defensive-tooling reference for people who already have permission to test a system, and for the engineers who fix what those tests find. It is not an exploit kit. Read [DISCLAIMER.md](DISCLAIMER.md), [SECURITY.md](SECURITY.md), and the [MIT licence](LICENSE) (Copyright (c) 2026 Alan) before you use the notes or the utilities. The network utilities do nothing until you name a target and pass `--authorized`.

An authorised-use knowledge base for planning, performing, and reporting security assessments, and for fixing what those assessments find. It is a methodology and defence reference in the tradition of the [OWASP Web Security Testing Guide](https://wstg.owasp.org/), the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/), [MITRE ATT&CK](https://attack.mitre.org/), and [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final).

The maintainer is Alan. The repository is [AlanKam555/redteamtools](https://github.com/AlanKam555/redteamtools). Changes are recorded in [CHANGELOG.md](CHANGELOG.md). How to add a note or a check is [CONTRIBUTING.md](CONTRIBUTING.md).

## Contents

1. [Authorised use](#authorised-use)
2. [Repository map](#repository-map)
3. [Methodology](#methodology)
4. [Vulnerability classes](#vulnerability-classes)
5. [Cheatsheets, checklists, and templates](#cheatsheets-checklists-and-templates)
6. [Utilities](#utilities)
7. [Tests and continuous integration](#tests-and-continuous-integration)
8. [How to extend it](#how-to-extend-it)
9. [Primary sources](#primary-sources)
10. [Licence](#licence)

## Authorised use

Use this material only against systems you own or are explicitly authorised to test, inside a written scope and rules of engagement. Permission for one host, one application, or one time window is not permission for anything else. Scanning or accessing a system without that permission can be a crime.

The utilities refuse to contact a target until you pass `--authorized`, which records your attestation. The flag does not create permission. There is no default host. A URL with an embedded username or password is rejected.

| Document | What it settles |
| --- | --- |
| [DISCLAIMER.md](DISCLAIMER.md) | Authorised-use limits, what this repository will not do, and the lack of warranty. |
| [SECURITY.md](SECURITY.md) | How to report a defect in this repository, and what the four utilities are allowed to do. |
| [LICENSE](LICENSE) | MIT licence. Copyright (c) 2026 Alan. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | What belongs in a change, and what must stay out. |

## Repository map

| Path | Contents |
| --- | --- |
| [methodology/](methodology/README.md) | Assessment phases, from scoping through reporting, and a note for each major vulnerability class. |
| [cheatsheets/](cheatsheets/README.md) | Short, safety-bounded usage notes for common public tools. |
| [checklists/](checklists/README.md) | Scoping, rules of engagement, web, API, and reporting checklists. |
| [templates/](templates/README.md) | Rules of engagement, finding, report, and executive-summary templates. |
| [tools/](tools/README.md) | Defensive utilities: header review, TLS review, a report skeleton, and a rules-of-engagement checker. |
| [resources/](resources/README.md) | Curated links to standards, tools, and training. |

Each vulnerability note covers four things:

1. What the class is and why it matters.
2. How to test for it, at a high level, on a system you are allowed to test.
3. How to confirm impact with the smallest safe proof.
4. How to fix it and how to detect it afterwards.

Raw test-string catalogues are not copied into this repository. Where an authorised tester needs those strings, the notes point at the public projects that already maintain them: the OWASP testing guide, PortSwigger Web Security Academy, [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), and [HackTricks](https://hacktricks.wiki/). Those projects are citations for laboratory and authorised use. They are not a suggestion to run their contents against a system you do not have permission to test.

## Methodology

The working method is [methodology/README.md](methodology/README.md). The phases, in order:

| Phase | Note | Pair it with |
| --- | --- | --- |
| Scope | [Scoping and rules of engagement](methodology/01-scoping-and-rules-of-engagement.md) | [Scoping checklist](checklists/scoping.md), [rules checklist](checklists/rules-of-engagement.md), [rules template](templates/rules-of-engagement.md) |
| Reconnaissance | [Reconnaissance](methodology/02-reconnaissance.md) | Anything newly found goes back to the scope note. |
| Enumeration | [Enumeration](methodology/03-enumeration.md) | [Nmap](cheatsheets/nmap.md), [ffuf](cheatsheets/ffuf.md) |
| Analysis | [Vulnerability analysis](methodology/04-vulnerability-analysis.md) | [Nuclei](cheatsheets/nuclei.md), the class notes below |
| Web | [Web application testing](methodology/05-web-application-testing.md) | [Web checklist](checklists/web-application-testing.md), [Burp Suite](cheatsheets/burp-suite.md) |
| API | [API testing](methodology/06-api-testing.md) | [API checklist](checklists/api-testing.md) |
| Impact | [Post-exploitation concepts](methodology/07-post-exploitation-concepts.md) | Concepts and detection only. Not a procedure. |
| Report | [Reporting](methodology/08-reporting.md) | [Reporting checklist](checklists/reporting.md), [report template](templates/report.md) |

```text
scoping and rules of engagement
        |
        v
passive and active reconnaissance  -->  anything new goes back to scope
        |
        v
enumeration of in-scope assets
        |
        v
vulnerability analysis (known issues, then classes)
        |
        +--> web application testing
        +--> API testing
        |
        v
impact, only as far as the rules allow
        |
        v
report, retest, and the client's remediation
```

Post-exploitation is covered as concepts and defender expectations. It is not a procedure for persistence, credential theft, or lateral movement. If an engagement needs to demonstrate impact beyond a safe proof, that activity has to be written into the rules of engagement first, and it still has to stay short of harm.

## Vulnerability classes

Index: [methodology/vulnerabilities/README.md](methodology/vulnerabilities/README.md). Public sources for the same classes: [resources/vulnerability-classes.md](resources/vulnerability-classes.md).

| Class | Note |
| --- | --- |
| Cross-site scripting | [xss.md](methodology/vulnerabilities/xss.md) |
| SQL injection | [sql-injection.md](methodology/vulnerabilities/sql-injection.md) |
| Server-side request forgery | [ssrf.md](methodology/vulnerabilities/ssrf.md) |
| OS command injection | [command-injection.md](methodology/vulnerabilities/command-injection.md) |
| Server-side template injection | [ssti.md](methodology/vulnerabilities/ssti.md) |
| XML external entities | [xxe.md](methodology/vulnerabilities/xxe.md) |
| IDOR and access control | [idor-access-control.md](methodology/vulnerabilities/idor-access-control.md) |
| Authentication flaws | [authentication-flaws.md](methodology/vulnerabilities/authentication-flaws.md) |
| Deserialization | [deserialization.md](methodology/vulnerabilities/deserialization.md) |
| LLM prompt injection | [llm-prompt-injection.md](methodology/vulnerabilities/llm-prompt-injection.md) |

## Cheatsheets, checklists, and templates

Cheatsheets, from [cheatsheets/README.md](cheatsheets/README.md): [Nmap](cheatsheets/nmap.md), [ffuf](cheatsheets/ffuf.md), [Nuclei](cheatsheets/nuclei.md), [Burp Suite](cheatsheets/burp-suite.md), [HTTP headers and TLS](cheatsheets/http-headers-and-tls.md).

Checklists, from [checklists/README.md](checklists/README.md): [scoping](checklists/scoping.md), [rules of engagement](checklists/rules-of-engagement.md), [web application testing](checklists/web-application-testing.md), [API testing](checklists/api-testing.md), [reporting](checklists/reporting.md).

Templates, from [templates/README.md](templates/README.md): [rules of engagement](templates/rules-of-engagement.md), [finding](templates/finding.md), [report](templates/report.md), [executive summary](templates/executive-summary.md). Fictional completed rules files, which the validator accepts, are under [templates/examples/](templates/examples/README.md). They do not authorise anyone to test `example.com`.

## Utilities

The programs under `tools/` use the Python 3.10+ standard library. Nothing else needs to be installed. [pyproject.toml](pyproject.toml) records an empty runtime dependency list, and [tools/requirements.txt](tools/requirements.txt) says the same thing.

```bash
python3 tools/security_header_checker.py --help
python3 tools/tls_config_checker.py --help
python3 tools/report_skeleton.py --help
python3 tools/scope_roe_validator.py --help
python3 -m unittest discover -s tools/tests -v
```

| Program | Network | Needs |
| --- | --- | --- |
| [security_header_checker.py](tools/security_header_checker.py) | One GET, plus at most three redirects | `--url` and `--authorized` |
| [tls_config_checker.py](tools/tls_config_checker.py) | A handful of handshakes to one host and port | `--host` and `--authorized` |
| [report_skeleton.py](tools/report_skeleton.py) | None | Client, engagement, dates, and author |
| [scope_roe_validator.py](tools/scope_roe_validator.py) | None | `--file` pointing at a local rules file |

A header or TLS check sends a few read-only requests to the single URL or host you name. The report generator and the rules-of-engagement checker never open a network connection. Exit status is `0` when the check finished without a fail-level result, `1` when it finished and found a fail-level gap (or a rules file is not ready), and `2` when the arguments were refused or the check could not run. Details, limits, and examples are in [tools/README.md](tools/README.md). The header and TLS cheatsheet is [cheatsheets/http-headers-and-tls.md](cheatsheets/http-headers-and-tls.md).

## Tests and continuous integration

```bash
python3 -m unittest discover -s tools/tests -v
python3 -m pip install "ruff>=0.8"
ruff check tools
```

GitHub Actions (`.github/workflows/ci.yml`) runs that lint and the unit tests on push and pull request. The workflow's only permission is `contents: read`. Tests use localhost only.

## How to extend it

Add methodology, checklists, and defensive utilities. Keep a new vulnerability note in the same shape as the ones in `methodology/vulnerabilities/`: class, responsible test approach, safe confirmation, remediation, detection, and a real public reference. [CONTRIBUTING.md](CONTRIBUTING.md) is the full rule.

Leave exploit code, malware, and ready-to-run payload collections out. If a sentence would be enough for someone to compromise a system they have no permission to touch, it belongs in a primary source's authorised testing guide, or it does not belong here at all. Cite sources you have actually opened. Invented advisories and invented test identifiers are worse than a shorter note.

## Primary sources

- OWASP Web Security Testing Guide — <https://wstg.owasp.org/>
- OWASP Cheat Sheet Series — <https://cheatsheetseries.owasp.org/>
- OWASP Application Security Verification Standard — <https://owasp.org/www-project-application-security-verification-standard/>
- OWASP Top 10 (2021) — <https://owasp.org/Top10/2021/>
- OWASP API Security Top 10 (2023) — <https://owasp.org/API-Security/editions/2023/en/0x11-t10/>
- OWASP GenAI / LLM risk — <https://genai.owasp.org/>
- MITRE ATT&CK — <https://attack.mitre.org/>
- MITRE CWE — <https://cwe.mitre.org/>
- NIST SP 800-115 — <https://csrc.nist.gov/pubs/sp/800/115/final>
- FIRST CVSS — <https://www.first.org/cvss/>

The longer catalogue, including learning material, is [resources/standards.md](resources/standards.md), [resources/tools.md](resources/tools.md), and [resources/learning.md](resources/learning.md).

## Licence

The software and these documents are released under the MIT licence. Copyright (c) 2026 Alan. See [LICENSE](LICENSE).

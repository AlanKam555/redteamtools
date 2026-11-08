# Red team and penetration-testing reference

An authorised-use knowledge base for planning, performing, and reporting security assessments, and for fixing what those assessments find. It is a methodology and defence reference in the tradition of the [OWASP Web Security Testing Guide](https://wstg.owasp.org/), the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/), [MITRE ATT&CK](https://attack.mitre.org/), and [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final).

The maintainer is Alan. The repository is [AlanKam555/redteamtools](https://github.com/AlanKam555/redteamtools).

## Authorised use

Use this material only against systems you own or are explicitly authorised to test, inside a written scope and rules of engagement. Permission for one host, one application, or one time window is not permission for anything else. Scanning or accessing a system without that permission can be a crime.

Read [DISCLAIMER.md](DISCLAIMER.md) and [SECURITY.md](SECURITY.md) before you use the notes or the utilities. The utilities refuse to contact a target until you pass `--authorized`, which records your attestation. The flag does not create permission.

## What you will find here

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

## How the phases fit together

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

## Utilities

The programs under `tools/` use the Python 3.10+ standard library. Nothing else needs to be installed.

```bash
python3 tools/security_header_checker.py --help
python3 tools/tls_config_checker.py --help
python3 tools/report_skeleton.py --help
python3 tools/scope_roe_validator.py --help
python3 -m unittest discover -s tools/tests -v
```

A header or TLS check sends a few read-only requests to the single URL or host you name. The report generator and the rules-of-engagement checker never open a network connection. Details, limits, and examples are in [tools/README.md](tools/README.md).

## How to extend it

Add methodology, checklists, and defensive utilities. Keep a new vulnerability note in the same shape as the ones in `methodology/vulnerabilities/`: class, responsible test approach, safe confirmation, remediation, detection, and a real public reference.

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

## Licence

The software and these documents are released under the MIT licence. Copyright (c) 2026 Alan. See [LICENSE](LICENSE).

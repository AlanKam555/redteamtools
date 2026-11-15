# Standards and frameworks

These are the documents an assessment report can cite without apologising. Use the edition you actually followed, and name it in the methodology section.

## Testing and requirements

- OWASP Web Security Testing Guide — <https://wstg.owasp.org/> and the project page <https://owasp.org/www-project-web-security-testing-guide/>. The versioned tests cited in this repository are under `https://wstg.owasp.org/v4.2/`.
- OWASP Cheat Sheet Series — <https://cheatsheetseries.owasp.org/index.html>. Prevention and defence live here.
- OWASP Application Security Verification Standard — <https://owasp.org/www-project-application-security-verification-standard/> and the repository <https://github.com/OWASP/ASVS>.
- OWASP Top 10 (2021) — <https://owasp.org/Top10/2021/> and the project page <https://owasp.org/www-project-top-ten/>.
- OWASP API Security Top 10 (2023) — <https://owasp.org/API-Security/editions/2023/en/0x11-t10/> and the project page <https://owasp.org/API-Security/>.
- OWASP GenAI security project, including LLM risk — <https://genai.owasp.org/>. Prompt injection is <https://genai.owasp.org/llmrisk/llm01-prompt-injection/>.
- OWASP Software Assurance Maturity Model — <https://owaspsamm.org/>. Useful when the recommendation is about the programme, not a single defect.
- NIST SP 800-115, Technical Guide to Information Security Testing and Assessment — <https://csrc.nist.gov/pubs/sp/800/115/final>. The PDF is <https://nvlpubs.nist.gov/nistpubs/legacy/SP/nistspecialpublication800-115.pdf> and the DOI is <https://doi.org/10.6028/NIST.SP.800-115>.
- NIST SP 800-53 Rev. 5 — <https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final>. Control catalogue for the remediation side of a finding.
- NIST SP 800-63-4, Digital Identity Guidelines — <https://csrc.nist.gov/pubs/sp/800/63/4/final>. Authentication and identity findings should line up with this when the client is designing identity, not only a login form.
- NIST Cybersecurity Framework — <https://www.nist.gov/cyberframework>.

## Weakness, attack, and vulnerability identifiers

- MITRE CWE — <https://cwe.mitre.org/>. Cite the specific weakness, not "CWE" as a gesture.
- MITRE ATT&CK — <https://attack.mitre.org/> and the enterprise matrix <https://attack.mitre.org/matrices/enterprise/>. Use tactics and techniques as a language for what a defender should be able to see. This repository does not restate procedure-level technique steps.
- CVE — <https://www.cve.org/>.
- National Vulnerability Database — <https://nvd.nist.gov/>.
- FIRST CVSS — <https://www.first.org/cvss/> and CVSS v4.0 <https://www.first.org/cvss/v4-0/>.

## Disclosure and benchmarks

- OWASP Vulnerability Disclosure Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html>.
- NCSC vulnerability management collection — <https://www.ncsc.gov.uk/collection/vulnerability-management>.
- CIS Benchmarks — <https://www.cisecurity.org/cis-benchmarks>. Configuration findings for platforms often map more cleanly to a benchmark than to an application CWE.

## How to cite them in a finding

Name the identifier and give the URL you opened. "OWASP says this is bad" is not a reference. "CWE-639, broken access control on a user-supplied object identifier, WSTG authorization test for IDOR" is a reference. If you adjusted a CVSS score for business impact, say so next to the vector rather than publishing the adjusted number as if FIRST had produced it.

## Related in this repository

- [Resource index](README.md)
- [Vulnerability classes](vulnerability-classes.md)
- [Methodology](../methodology/README.md)
- [Disclaimer](../DISCLAIMER.md)

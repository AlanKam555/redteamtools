# Security assessment report: [Engagement title]

| Field | Value |
| --- | --- |
| Client | [Client legal name] |
| Engagement | [Engagement title] |
| Assessment window | [YYYY-MM-DD] to [YYYY-MM-DD] |
| Author | [Author] |
| Classification | [Confidential, or the label the rules require] |
| Status | Draft |

Authorised-use reminder. This report describes an engagement that already has written permission. Remove client data before the file is stored anywhere a methodology repository is published. Describe the weakness class, the evidence, and the fix. Do not embed live exploit strings.

`python3 tools/report_skeleton.py --help` writes this outline with the table filled in. The section guidance below is the same as that generator.

## 1. Executive summary

Write this so it can be lifted into [executive-summary.md](executive-summary.md). Cover why the assessment was done, which environment it covered, the risk themes in business language, what is going well, and the decisions you want. Leave severity counts until the findings are real.

## 2. Scope

- In-scope assets actually tested:
- Out-of-scope assets observed and left alone:
- Accounts and roles provided:
- Environments:
- Known limits:

The list should match the signed rules of engagement. A host you discovered and did not test belongs in the second bullet, not in a finding.

## 3. Methodology

Name the public method. For web and API work that is the [OWASP Web Security Testing Guide](https://wstg.owasp.org/). For the overall process, [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final). State whether testing was authenticated, and whether you had source code. Record the proxy or scanner and the defensive checkers you ran, with versions.

## 4. Risk rating

Use the qualitative scale published with [CVSS](https://www.first.org/cvss/) and name the version. When business impact differs from the base score, write the reason. A missing header and a missing authorization check are not the same finding because the numbers were close.

## 5. Findings summary

| ID | Title | Severity | Asset | Status |
| --- | --- | --- | --- | --- |
| F-01 | [Title] | [Severity] | [Asset] | Open |

## 6. Detailed findings

Copy [finding.md](finding.md) once per row. Each entry needs the class, the impact, sanitised evidence, a remediation, and a primary reference.

## 7. Positive observations

Record controls that held: authorization that stayed consistent across a sample, parameterised queries in the services you reviewed, multi-factor authentication on administrative roles, audit logs that contained the actor and the object. These tell the next tester where not to spend the whole window.

## 8. Remediation roadmap

Group fixes by theme (authorization, injection handling, transport and headers, logging). Mark the ones that remove a class. Name the environment for the retest of high and critical items.

## 9. Data handling

Where evidence is stored, who may read it, and when it will be deleted. This section should agree with the rules of engagement.

## 10. References

- OWASP Web Security Testing Guide — <https://wstg.owasp.org/>
- OWASP Cheat Sheet Series — <https://cheatsheetseries.owasp.org/>
- OWASP Application Security Verification Standard — <https://owasp.org/www-project-application-security-verification-standard/>
- NIST SP 800-115 — <https://csrc.nist.gov/pubs/sp/800/115/final>
- FIRST CVSS — <https://www.first.org/cvss/>

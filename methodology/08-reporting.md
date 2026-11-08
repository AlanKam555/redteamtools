# Reporting

A report is a decision document. The technical record exists so a sceptical engineer can believe the decision and so a retest can be done later. [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final) treats analysis and reporting as the step that turns observations into risk reduction. Findings that cannot be reproduced, or that cannot be explained to the person who will fund the fix, do not clear that bar.

Use [templates/report.md](../templates/report.md), [templates/finding.md](../templates/finding.md), and [templates/executive-summary.md](../templates/executive-summary.md). The generator in `tools/report_skeleton.py` writes a local draft with the same skeleton. The checklist is [checklists/reporting.md](../checklists/reporting.md).

## Audiences

Write two layers, on purpose.

- **Executive summary.** Why the work was done, what was in scope, the themes, what is already solid, and the decisions requested. No payload detail, no host-by-host tour. A director who reads only this page should know whether to fund a programme change or a patch.
- **Technical findings.** One entry per weakness or per systemic pattern. Enough for an engineer who was not in the readout to fix the right thing, and enough for a second tester to retest it.

A third layer, the raw evidence, stays in the engagement store named in the rules of engagement. It is not an appendix that gets emailed to the whole distribution list.

## What every finding contains

| Field | What "done" looks like |
| --- | --- |
| Title | The class and the place, not a joke and not a CVE number alone. |
| Severity | A FIRST qualitative band, the CVSS version and vector if you scored it, and one sentence of business adjustment if the base score misleads. |
| Affected asset | Environment, host or route, parameter or object type, role. |
| Description | What the application does, what the boundary was supposed to be, and how the boundary fails. Class-level language. |
| Impact | The action and the data that become available, given the access the tester actually had. |
| Evidence | Sanitised comparison of baseline and variant. Identifiers of canary records. A pointer to the restricted evidence, not a paste of a live exploit string or a session token. |
| Remediation | The design change that removes the class, plus the containment control. Link the relevant note in `methodology/vulnerabilities/`. |
| Detection | The log or test that should fire next time. |
| References | A real CWE, a real OWASP page, a vendor advisory if there is one. |

Group systemic issues. Fifty missing authorization checks on one pattern are one finding with a representative sample and a count, plus a statement about whether you stopped sampling.

## Severity

Use the qualitative scale published with CVSS by [FIRST](https://www.first.org/cvss/v4-0/): Informational, Low, Medium, High, Critical. Name whether the vector is CVSS 3.1 or 4.0. Then apply judgement:

- Raise the engagement rating when the data or the action is central to the business even if the base score is modest. Say why.
- Lower it when the precondition is unreachable, the feature is already isolated, or the client has a tested compensating control. Say why.
- Do not average findings into a single number for the whole assessment. Themes communicate. A mean hides the one issue that matters.

Informational items are real: a missing hardening header, a version banner, a log that almost has the right fields. Park them where they will be read, and do not let them dilute the first page.

## Reproduction and retest

An engineer should be able to retest from the technical finding and the test accounts, without calling you. That means the finding names the route, the role, the kind of input (the class, not a copied exploit), and the symptom of success and failure.

It also means you leave the environment as you found it. Revert canary writes. Expire tokens you issued. Tell the client about anything you could not revert.

During a retest, verify the fix on the same class, not only the original parameter. A filter on one field is not a repair of string-concatenated queries. Note the new build identifier. A retest on a different build than production is a retest of that build, and the report should say so.

## Writing about evidence safely

- Redact secrets, session tokens, personal data, and internal hostnames the client does not want in a mobile copy of the report.
- Describe exploit strings by class ("the marker was interpreted as template syntax") and keep the raw bytes in the restricted store if the client needs them for the fix.
- Do not include a tutorial that would let a reader attack a system that was not in scope. Link to the public testing guide for the class instead.
- Mark the document with the classification from the rules of engagement. The skeleton defaults to Confidential for a reason.

## Positive observations and limitations

A report that is only a list of defects trains the client to hide the next assessment. Record controls that held: authorization that failed closed on a sampled object type, queries that were parameterised, MFA on the administrative role, logs that contained actor and object.

Record limits with equal honesty: routes you did not reach, roles you were not given, scanner categories you excluded, days the environment was down. [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final) is clear that a test samples the posture. The limitations section is what stops a reader from treating the report as a certificate of safety.

## The readout

Walk the themes, one representative finding, and the decisions. Do not discover a new critical issue in the meeting and narrate it from memory. If something is still unconfirmed, it is not in the deck.

Agree who receives the document, which copy is canonical, and when the retest window is. Those three facts belong in the email that carries the report, and they should match the data-handling section.

## References

- NIST SP 800-115 — <https://csrc.nist.gov/pubs/sp/800/115/final>
- FIRST CVSS — <https://www.first.org/cvss/> and <https://www.first.org/cvss/v4-0/>
- CWE — <https://cwe.mitre.org/>
- Report template — [../templates/report.md](../templates/report.md)
- Executive summary template — [../templates/executive-summary.md](../templates/executive-summary.md)
- Finding template — [../templates/finding.md](../templates/finding.md)

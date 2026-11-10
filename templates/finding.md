# Finding F-[NN]: [Short title]

| Field | Value |
| --- | --- |
| Severity | [Critical, High, Medium, Low, or Informational, and the CVSS vector if you computed one] |
| Status | Open |
| Asset | [URL or component, environment, version] |
| Class | [CWE identifier and the OWASP category] |
| Account used | [Test account role, not a password] |

## Description

State the class in two or three sentences, the way the matching note in `methodology/vulnerabilities/` does. Name the control that failed. Do not paste a working exploit. A reader who needs the public test strings can follow the reference link.

## Impact

What an attacker who already had the access you had could do, in the client's language: read another tenant's record, change a payment, run code as the application user. Tie the claim to the evidence below. If you stopped at a canary, say that the canary is the proof and that you did not continue.

## Evidence

- Date and environment.
- The request shape: method, route, and which field you changed. Redact tokens.
- The baseline result and the result after the change.
- The second principal, if this is an access-control finding.
- A statement of what you did not do (no data exported, no second payload, no production write).

Keep screenshots cropped. Store the raw proxy history in the engagement store named in the rules of engagement, not in this file if the file will be emailed.

## Remediation

1. The change that removes the class, not a filter for the one string you sent.
2. The containment that reduces blast radius while the change is built (authorization in front of the feature, least privilege, a header).
3. How to detect a recurrence: the log fields and the alert.

Point at the OWASP cheat sheet or the WSTG test that describes the fix. Prefer that primary source over a paraphrase.

## References

- [CWE URL]
- [OWASP cheat sheet or WSTG test URL]
- [Vendor advisory, if one applies]

## Related in this repository

- [Report template](report.md)
- [Reporting method](../methodology/08-reporting.md)
- [Reporting checklist](../checklists/reporting.md)
- [Vulnerability class notes](../methodology/vulnerabilities/README.md)
- [Disclaimer](../DISCLAIMER.md)

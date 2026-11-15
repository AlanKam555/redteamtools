# Reporting checklist

Use this before a report leaves the engagement store, alongside [reporting](../methodology/08-reporting.md), the [report template](../templates/report.md), and the [executive summary](../templates/executive-summary.md).

## Truthfulness

- [ ] Every finding was reproduced, or it is clearly marked as a configuration or code observation.
- [ ] The asset, the environment, the account, and the date are on each finding.
- [ ] Severity uses a named scheme (CVSS version, plus any business adjustment) and the adjustment is explained.
- [ ] Limitations are listed: routes you did not reach, credentials you did not receive, tools you were told not to run.
- [ ] Positive observations are included, so the reader can see what held.

## Safety of the document

- [ ] Live exploit strings are not in the report. The class, the evidence, and the fix are.
- [ ] Session tokens, passwords, and personal data are redacted. A screenshot was cropped before it was embedded.
- [ ] Canary values are identified as canaries, so nobody treats them as a real customer record.
- [ ] The classification label matches what the rules of engagement allow you to circulate.
- [ ] The file you are about to email is the redacted copy. The full evidence stays in the engagement store.

## Usefulness

- [ ] The executive summary can be read without the appendix and still says what to fund.
- [ ] Each finding has a remediation an engineer can start, with the primary reference (CWE and the OWASP cheat sheet or WSTG test).
- [ ] Fixes that remove a class are distinguished from fixes that patch one parameter.
- [ ] A retest plan names which findings will be rechecked and in which environment.
- [ ] The scope section matches the rules of engagement, including hosts you discovered and did not test.

## Delivery

- [ ] The named audience has the report, and a copy is not in a public ticket or a chat tool with a wider membership.
- [ ] The client knows where evidence is and when you will delete it.
- [ ] Test accounts and test data are handed back for revocation and deletion.
- [ ] You kept the validator output, the tool versions, and the command lines you actually ran, in the engagement store.

## Related in this repository

- [Checklist index](README.md)
- [Reporting method](../methodology/08-reporting.md)
- [Report template](../templates/report.md)
- [Finding template](../templates/finding.md)
- [Executive summary](../templates/executive-summary.md)
- [Disclaimer](../DISCLAIMER.md)

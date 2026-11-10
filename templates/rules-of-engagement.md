# Rules of engagement

Replace every bracketed prompt before anyone sends a request. This blank file is supposed to fail `python3 tools/scope_roe_validator.py --file templates/rules-of-engagement.md`. A completed file has no `TODO` markers and no leftover bracketed prompts, and it names systems that must not be touched.

This template is a record of permission. It does not create permission by being filled in. The person named as the approver has to have the authority to grant it.

## Authorization

[Client legal name] authorises [tester legal name] to test only the assets in the next section, between the dates in the schedule, using the methods listed below.

Approved by: [Approver name and role]
Date of approval: [YYYY-MM-DD]
Reference: [Contract or ticket identifier]

## In-scope assets

- [URL, hostname, or repository, plus the environment and version]
- Accounts provided: [Role and account identifier, test data only]

## Out of scope

- [Neighbouring production host, third-party service, or shared platform that must not be touched]
- Any asset not named under in-scope assets, including names discovered during reconnaissance.

## Allowed methods

- [Manual review, authenticated testing, header and TLS review, or other agreed methods]
- Rate ceiling: [Requests per second or "single-threaded manual"]
- Impact demonstration stops at: [Safe canary, configuration evidence, or a step written here]

## Prohibited activities

- Denial of service, flooding, and resource exhaustion.
- Data destruction, ransomware, and persistence on the client's systems.
- Credential theft against real users, password guessing, and social engineering, unless a line below explicitly allows a named technique.
- Testing of third-party services and of any host that is not in scope.
- [Anything else the client forbids]

## Schedule

Start: [YYYY-MM-DD]
End: [YYYY-MM-DD]
Hours: [HH:MM-HH:MM and timezone]
Pause mechanism: [How either party stops the test the same day]

## Emergency contacts

- Client: [Name, method, backup method]
- Tester: [Name, method, backup method]

## Data handling

Evidence is stored in [Engagement store]. Access is limited to [Named roles]. Evidence is deleted on [Date or "N days after the retest"]. Live secrets and personal data are redacted before a report is circulated. Exploit strings are not written into the report.

## Acknowledgement

Both parties acknowledge that this authorisation is limited to the assets, methods, and window above. Permission for one host is not permission for another. Discovering a new system creates a question for the approver, not a new target.

## Related in this repository

- [Scoping method](../methodology/01-scoping-and-rules-of-engagement.md)
- [Rules checklist](../checklists/rules-of-engagement.md)
- [Validator](../tools/README.md)
- [Completed example](examples/README.md)
- [Disclaimer](../DISCLAIMER.md)

# Rules of engagement

Fictional example for the validator. Example Corp and example.com are documentation names. This file is not an authorisation.

## Authorization

Example Corp authorises Alan to test the named assets during the schedule below. The approver is Jordan Example, Head of Security, on 2026-10-15, under internal ticket SEC-2048.

## In-scope assets

- https://app.example.com, staging, build 2026.10.1
- Test accounts: one standard user and one administrator, both in the staging tenant, issued by Example Corp.

## Out of scope

- https://payments.example.com and every third-party service not listed above.
- Production, the corporate identity provider, and any hostname discovered during the test that is not in the list above.

## Allowed methods

- Manual web and API testing at a modest rate, no more than five requests per second.
- Read-only header and TLS review of app.example.com.
- Impact demonstration stops at a harmless canary or a second test account. No further action without a written change to this document.

## Prohibited activities

- Denial of service, data destruction, and persistence.
- Password guessing, social engineering, and testing of real customer accounts.
- Any request to a host that is not in scope.

## Schedule

2026-11-01 to 2026-11-08, 09:00-17:00 UTC. Either party may pause the test immediately by phoning the emergency contact. Testing stays paused until both contacts agree to resume.

## Emergency contacts

- Alex Example, security-oncall@example.com, +1-555-0100. Backup: Jordan Example, +1-555-0101.
- Alan, tester-oncall@example.com, +1-555-0199.

## Data handling

Evidence stays in the engagement vault operated by Example Corp and is deleted 90 days after the retest. The report that leaves the vault is redacted. Session tokens and personal data are not copied into tickets.

## Acknowledgement

Both parties acknowledge this authorisation is limited to the assets, methods, and window above. A new hostname is a question for Jordan Example, not a new target.

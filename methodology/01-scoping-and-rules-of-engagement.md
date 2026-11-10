# Scoping and rules of engagement

Scoping is the security control that sits in front of every other control in an assessment. It decides which systems may be touched, which techniques are acceptable, how much noise is tolerable, who gets a phone call at 02:00, and what happens to the evidence afterwards. [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final) treats planning, rules of engagement, and data handling as part of the assessment, not as paperwork around it.

The blank document to fill in is [templates/rules-of-engagement.md](../templates/rules-of-engagement.md). The checklist is [checklists/scoping.md](../checklists/scoping.md). `tools/scope_roe_validator.py` checks that the required decisions are still present after editing.

## What "in scope" has to name

An asset list made of company names is not a scope. Write the things that will actually receive a packet or an authenticated request:

- DNS names, URLs, and IP addresses, including whether the whole address is in scope or only specific ports.
- Applications and API base paths, and the environments (production, staging, a named tenant, a preview).
- Account roles the client will provide, and whether those accounts are synthetic.
- Mobile binaries, thick clients, or repositories, if the test includes them.
- The time window, including the timezone, and any blackout dates (payroll, a product launch, a market event).

Write the negative space with the same care. Typical exclusions:

- Third parties that sit in front of or beside the target: identity providers, payment processors, CDNs, email gateways, and shared SaaS, unless that third party has given its own written permission.
- Networks and hosts discovered during the test that the client has not adopted into scope.
- Availability testing, social engineering, physical access, and anything that destroys or encrypts data, unless a separate plan exists.
- Real personal data. Seed canary records instead.

A scope of "everything we own" feels efficient and produces an unlawful or contractual miss the first time the tester follows a link. Discovery of a new asset is a scope change, not an invitation.

## Authorisation

The authorisation statement names the legal entity that owns or operates the targets, the person who is allowed to grant access, and the tester or firm that receives it. It states that the activity is authorised, and it points at the asset list and the window rather than saying "security testing" in the abstract.

Keep the signed copy with the engagement records. A verbal approval in a chat channel is a reason to start drafting the document, not a reason to start scanning. If the person granting access cannot actually bind the owner (a developer approving a test of a system their team does not operate, a subsidiary approving a test of the parent), stop and find the right signatory.

Emergency contacts are part of the authorisation. Name a person who can tell the tester to stop, a person on the client side who can explain an outage, and the path the tester will use (phone, then a named bridge). Test the path once before the window opens. A contact that goes to a shared inbox nobody reads is not a contact.

## Methods, depth, and rate

Agree the classes of activity in language a non-tester can understand:

- Passive collection of public information about the named organisation.
- Network and application enumeration of the named assets, with a rate limit.
- Authenticated and unauthenticated application and API testing.
- Whether automated scanners are allowed, and which categories are excluded (availability, intrusive checks, brute force).
- Whether a proof may create a record, send an email, or read a canary the client planted.
- Whether any action past "we have shown the class" is in scope at all.

Brute force, credential stuffing, and password spraying against a real identity system are a product decision. They lock users out and they look like an attack to the defenders who were not told. Default them to off. If they are on, cap the attempt rate, use a client-provided list, and exclude production identities unless the rules say otherwise.

Denial of service, resource exhaustion, and ransomware-style exercises are separate projects with their own abort criteria. They do not ride along inside a web assessment because a scanner template happened to include them.

## Data handling

An assessment creates sensitive data even when the application does not: proxy histories, screenshots, tokens, source snippets, and the report itself. Decide, before the first request:

- Where evidence is stored, and who can read it.
- Whether the tester's laptop, the firm's vault, or the client's tenant is the system of record.
- How long evidence is kept after the retest, and how it is destroyed.
- Whether any sample of live data is allowed. The default in this methodology is no. Use test accounts and canaries.
- How findings are transmitted. Email of an unencrypted full report to a distribution list is a common second incident.

The report template's data-handling section exists so this decision survives into the document the client archives.

## Environments and success criteria

Ask what "done" means. A fixed window with a best-effort coverage statement is honest. A promise to "find everything" is not, and [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final) is explicit that a test is a sample of the security posture, not a proof of its absence of flaws.

Prefer a production-like environment when the finding has to be believed, and prefer a non-production environment when the test writes, deletes, or stresses anything. Record the build identifier, the feature flags, and the configuration that was actually deployed. A fix verified on a different build is not a retest.

Also record what the client believes is already true: a WAF in blocking mode, a bug-bounty policy, an identity provider, a list of accepted risks. Testing blindly against a control the client can explain wastes the window and produces findings they have already accepted.

## Changes during the test

Scope changes are normal. Write them down, name who approved them, and attach them to the rules of engagement. The validator in `tools/` will not know about a verbal change. The engagement file should.

If the client asks for something the rules forbid (a production denial-of-service check, a test of a supplier, a copy of a real customer record "just to prove it"), the answer is a revised document or a refusal. Quietly expanding the test is how authorised work becomes something else.

## References

- NIST SP 800-115, Technical Guide to Information Security Testing and Assessment — <https://csrc.nist.gov/pubs/sp/800/115/final>
- OWASP Web Security Testing Guide, introduction and principles — <https://wstg.owasp.org/>
- NCSC vulnerability management collection — <https://www.ncsc.gov.uk/collection/vulnerability-management>
- Rules of engagement template — [../templates/rules-of-engagement.md](../templates/rules-of-engagement.md)
- Scoping checklist — [../checklists/scoping.md](../checklists/scoping.md)

## Related in this repository

- [Methodology index](README.md)
- [Next: reconnaissance](02-reconnaissance.md)
- [Scoping checklist](../checklists/scoping.md)
- [Rules-of-engagement checklist](../checklists/rules-of-engagement.md)
- [Rules template](../templates/rules-of-engagement.md)
- [Completed example](../templates/examples/README.md)
- [Rules validator](../tools/README.md)
- [Disclaimer](../DISCLAIMER.md)

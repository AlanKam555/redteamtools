# Reconnaissance

Reconnaissance answers a narrow question: what can already be learned about the named organisation from sources you are allowed to consult, and which of those facts describe an asset the client has put in scope?

It is not a licence to investigate employees, customers, or suppliers. Personal data that is irrelevant to the assessment does not get collected "because it was public".

## Passive collection

Passive work uses data someone else already published. For an authorised external assessment, the useful categories are:

- **DNS.** The names the client listed, their name servers, mail hosts, and TXT records that reveal providers (email authentication, site verification, SaaS). Record the resolver you used and the time. DNS results change.
- **Certificates.** Public certificate-transparency logs show names that were put on a certificate. A name is a lead, not a target. If it is not in scope, it goes on the "ask the client" list. The [Certificate Transparency](https://certificate.transparency.dev/) site describes the logs themselves.
- **The organisation's own public sites and documents.** Marketing pages, status pages, API portals, privacy notices, and published mobile-app store entries often name the real hostnames.
- **Public code and paste sites, searched for the organisation's name and namespaces.** A leaked key is an incident to report, not a credential to use. Stop, record the location, and tell the emergency contact. Do not clone unrelated personal repositories because a developer mentioned the employer.
- **Job advertisements and conference talks.** They reveal technologies. They are context for the test, not a list of people to contact.

Keep provenance. "We saw this hostname" is weaker than "this hostname was on a certificate logged on this date, and the client confirmed it on this date".

Search operators and breach-index services exist and are widely documented. Use them only to look for the authorised organisation's own material, store what you keep under the data-handling rules, and do not turn a reconnaissance note into a dossier on a person. This repository does not include a dork list. The [OWASP Web Security Testing Guide](https://wstg.owasp.org/) information-gathering chapter is the public catalogue for this phase.

## Active reconnaissance

Active work touches infrastructure. It belongs inside the window, against names and addresses that are in scope, at the agreed rate.

- Resolve the in-scope names and record the addresses. Shared anycast and CDN addresses are often not "the client's server". Confirm before you treat an address as dedicated.
- Send the application requests the enumeration phase needs (a fetch of the public home page, a fetch of a published API description) and keep the evidence.
- If a wildcard, a virtual host, or a redirect names a new host, write it down and ask. Following it on the same afternoon is how scope drifts into a marketing agency or a payments company.

Active reconnaissance and enumeration blend together in practice. The distinction that matters is permission and rate, not the job title of the phase.

## Handling leads

Sort every new fact into one of four piles:

| Pile | What happens |
| --- | --- |
| In scope | It can be tested under the existing rules. |
| Ask | It might belong to the client. Do not test it yet. |
| Out of scope | It was named as excluded, or it is clearly a third party. Record it so the report can say it was seen and left alone. |
| Incident | A secret, a personal-data exposure, or an outage. Call the emergency contact and stop poking it. |

The report should mention material leads the client did not know about, including the ones you were not allowed to test. "We found a hostname and did not test it" is a useful sentence. Pretending the hostname does not exist, because it was inconvenient, is not.

## What this phase produces

- An asset table: name, address, owner confirmation, environment, source, date.
- A technology sketch: identity provider, CDN, framework hints from public pages and headers. Hints are not versions until enumeration confirms them.
- A list of questions for the client.
- Nothing that requires a password to have been guessed, and no contact with people who were not named as contacts.

## Defensive counterpart

The same sources are how an unsolicited party builds a picture. Defenders can:

- Keep an authoritative inventory and compare it to certificate-transparency names and DNS on a schedule.
- Remove public documents that embed internal hostnames, stack traces, and keys.
- Treat a leaked secret as an incident with rotation, not as a finding to file for the next quarterly test.
- Publish a vulnerability-disclosure route so the reports that reconnaissance triggers have somewhere to go. The [OWASP Vulnerability Disclosure Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerability_Disclosure_Cheat_Sheet.html) describes that practice.

## References

- OWASP Web Security Testing Guide — <https://wstg.owasp.org/>
- NIST SP 800-115 — <https://csrc.nist.gov/pubs/sp/800/115/final>
- Certificate Transparency — <https://certificate.transparency.dev/>
- MITRE ATT&CK reconnaissance tactic, as a vocabulary for the report — <https://attack.mitre.org/matrices/enterprise/>
- Enumeration, which consumes this phase's asset table — [03-enumeration.md](03-enumeration.md)

## Related in this repository

- [Methodology index](README.md)
- [Previous: scoping](01-scoping-and-rules-of-engagement.md)
- [Next: enumeration](03-enumeration.md)
- [Scoping checklist](../checklists/scoping.md)
- [Nmap cheatsheet](../cheatsheets/nmap.md)
- [Disclaimer](../DISCLAIMER.md)

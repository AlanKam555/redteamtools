# Scoping checklist

Use this while the engagement is being agreed, together with [scoping and rules of engagement](../methodology/01-scoping-and-rules-of-engagement.md). Every "yes" needs a name, a date, or a document, not a recollection.

## Parties and permission

- [ ] The client legal entity is named, and the person approving the test has authority to authorise it.
- [ ] The tester's organisation and the individuals who will test are named.
- [ ] Written authorisation exists and will still be in force on the first day of testing.
- [ ] The client has confirmed they have the right to authorise every asset in scope, including anything hosted by a third party.
- [ ] Third parties (cloud, CDN, identity, payment, email) have been asked, or they are explicitly out of scope.
- [ ] A point of contact can answer scope questions during the window, and a second person can if the first is away.

## Assets

- [ ] In-scope hosts, applications, APIs, and mobile or thick-client builds are listed with identifiers (URL, hostname, repository, version).
- [ ] IP addresses are listed only where the client owns the address. Shared and anycast addresses are called out.
- [ ] Production, staging, and tenant identifiers are distinguished. The environment to be tested is the one named, not "whichever is up".
- [ ] Accounts and roles are listed: how many, which privilege level, and whether they contain real customer data.
- [ ] Source code, architecture notes, or a previous report will be provided, or the test is explicitly black box.
- [ ] Out-of-scope systems that sit next to the target are named, including the production twin of a staging target if only one of them is allowed.

## Constraints

- [ ] The calendar window, the daily hours, and the timezone are written down.
- [ ] The rate ceiling is written down, especially for authentication and for anything shared with other customers.
- [ ] Denial of service, data destruction, persistence, and social engineering are each marked allowed or prohibited.
- [ ] The depth of impact demonstration is agreed: configuration evidence, a safe canary, or a further step that is itself written into the rules.
- [ ] Data the test must not collect is listed (payment cards, health data, credentials of real users, contents of mailboxes).
- [ ] Where evidence will be stored, who may read it, and when it will be deleted are agreed.

## Logistics

- [ ] Source IP addresses or a VPN the client can allow-list are known.
- [ ] Emergency contacts on both sides include a method that works outside business hours if the window includes those hours.
- [ ] A way to pause testing (phone, ticket, chat) is named, and the tester has tested that the method reaches a person.
- [ ] The report audience is named: technical owners, an executive reader, a regulator, or a customer of the client.
- [ ] Retest expectations are agreed, including whether a retest is in this engagement or a later one.

## Ready to write the rules

- [ ] Anything still marked "to be decided" has an owner and is not going to be filled in by the tester on the first morning.
- [ ] The [rules-of-engagement template](../templates/rules-of-engagement.md) can be completed from this list without inventing a decision.

## Related in this repository

- [Checklist index](README.md)
- [Scoping and rules of engagement](../methodology/01-scoping-and-rules-of-engagement.md)
- [Rules checklist](rules-of-engagement.md)
- [Rules template](../templates/rules-of-engagement.md)
- [Disclaimer](../DISCLAIMER.md)

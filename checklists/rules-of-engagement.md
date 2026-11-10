# Rules-of-engagement checklist

Complete this against the signed rules, not against the proposal. The [template](../templates/rules-of-engagement.md) has the sections. The [validator](../tools/scope_roe_validator.py) checks that those sections exist and that placeholder markers are gone. A passing validation means the document is complete enough to read. It does not mean the engagement is lawful.

## The document

- [ ] Authorisation is stated in a sentence, with the client name and the tester's name.
- [ ] The approver and the date of approval are recorded.
- [ ] In-scope assets are specific. "The corporate network" is not an asset list.
- [ ] Out of scope names the neighbours: production if you are on staging, third-party services, and anything reconnaissance might stumble into.
- [ ] Allowed methods match the test you intend to run (manual web, API, authenticated, configuration review).
- [ ] Prohibited activities include denial of service, destruction, and anything else the client forbade.
- [ ] The schedule has a start, an end, hours, and a timezone.
- [ ] Emergency contacts have a name and a method that reaches a person.
- [ ] Data handling says where evidence lives and when it is deleted.
- [ ] Both sides acknowledge that permission is limited to the assets and the window.
- [ ] `python3 tools/scope_roe_validator.py --file <the-file>` exits 0.

## Before the first request

- [ ] The copy you are about to test against is the signed copy, not the draft with the old host list.
- [ ] Your source addresses match what the client was told.
- [ ] Test accounts work, and you know which account is which role.
- [ ] You can name the abort condition and the person you call.
- [ ] The proxy, scanner, and wordlists are restricted to the in-scope hosts.
- [ ] Evidence will land in the engagement store, not in a public repository or a personal notes app.

## During the test

- [ ] A new hostname, a new API, or a new cloud account is added to scope before it is tested, or it is left alone and listed as a lead.
- [ ] A change of window or of method is written down. A chat message is enough only if the approver sent it and you kept it.
- [ ] If you hit the rate ceiling or an error spike, you stop and tell the emergency contact before you restart.
- [ ] You are not collecting data the rules told you to avoid, even when the application offers it.

## After the test

- [ ] Active sessions and any test data you created are listed for the client to remove.
- [ ] Credentials the client issued are revoked or returned.
- [ ] The report's scope section matches the rules, including what you did not test.

## Related in this repository

- [Checklist index](README.md)
- [Scoping method](../methodology/01-scoping-and-rules-of-engagement.md)
- [Rules template](../templates/rules-of-engagement.md)
- [Validator](../tools/README.md)
- [Disclaimer](../DISCLAIMER.md)

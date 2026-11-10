# IDOR and broken access control

Insecure direct object references are [CWE-639](https://cwe.mitre.org/data/definitions/639.html). The broader failure, missing or incorrect authorization, is [CWE-284](https://cwe.mitre.org/data/definitions/284.html). Broken access control is [OWASP Top 10 (2021) A01](https://owasp.org/Top10/2021/), and it is API1, API3, and API5 in the [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/). The public test description for direct object references is [WSTG IDOR](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References). The design guidance is the [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), the [Access Control Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html), and the [IDOR Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html).

## What it is

The application performs an action on an object, a field, or a function because the caller named it and presented some valid authentication, without deciding whether this caller is allowed to act on this thing. "IDOR" is the special case where the name is an identifier in a request. The same defect exists when the identifier is hidden in a POST body, a file path, a tenant header, or a property the user interface never shows.

Guessability of the identifier is not the control. A UUID that is not authorized is still a broken check the day the identifier leaks through a log, a referrer, or another bug. Unguessable identifiers are a reduction in accident, not an authorization model.

Two comparisons cover most of the risk:

- **Horizontal.** Two principals in the same role. User A can read or change user B's object.
- **Vertical.** A lower-privilege principal can call a function reserved for a higher role.

Multi-tenant applications add a third: a principal in tenant A can name an object in tenant B. Test it explicitly. A check that compares users inside one tenant and forgets the tenant column is a classic miss.

## Where it appears

- Routes that include an identifier, and routes that take the identifier from the body, a header, or a JSON field.
- "Export", "download", and "share" features, which often use a second code path that skipped the check on the page.
- Bulk endpoints that accept a list of identifiers and check only the first, or check none.
- GraphQL nodes and REST sub-resources (`/users/1/invoices/2`), where one of the two identifiers is checked.
- Property-level updates (mass assignment): the caller sets `owner`, `role`, `price`, or `tenant` on their own object. That is API3, and the [Mass Assignment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html) describes the defensive pattern.
- Administrative routes that are "hidden" by not being linked from the user's navigation.

## Responsible testing

This class is tested with principals, not with payloads.

1. Build the matrix from enumeration: object types, actions (read, create, update, delete, share, export), and the roles you were given.
2. As user A, create or locate a canary object. As user B, request that object by the same identifier the application used for A. Repeat for update and delete only on canaries the client has said you may change, and revert afterwards.
3. As the lower role, request a function you saw as the higher role. Compare status, body, and whether a side effect happened. A 403 with a body that still contains the object is a finding. A 200 that returns an empty document because the object is not yours is a pass. Look at the body.
4. For each object, try the identifier in every place it appears, including the copy of the request a background job uses if you can see that path. One checked route and one unchecked route is one pattern. Sample enough routes to say whether the pattern is systemic, then stop and write it up.
5. For property-level control, add a property the ordinary client does not send, using a value that is harmless on a canary (a display name you can see, not a role change), and read the object back. Escalate to a sensitive property only when the client has agreed that a canary role or a canary price is allowed to change for the test. Revert it.

Do not iterate identifiers looking for a real customer. The canary is the proof. Sequential guessing against production is an availability and privacy problem, and it is unnecessary once a second test account exists. If the client cannot provide a second account, document the limitation and test only vertical cases you can reach with the accounts you have. Do not borrow a real user's identifier from a log or from another finding and keep reading.

Function-level and object-level failures in APIs are the same test. [API testing](../06-api-testing.md) points back here so the method is described once.

## Safe confirmation

- The two principals, the object type, the action, and the canary identifier.
- The response code and a redacted body that shows the canary marker.
- Whether the pattern repeated on the other routes you sampled, with the count and the scope of the sample.
- Confirmation that you reverted writes and that you did not continue into real records.

A single horizontal read of a canary is a complete high-severity finding when the object is sensitive. You do not need a hundred examples.

## Remediation

The [Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) is the design reference. The implementation habits that prevent the class:

- **Authorize on the server for every action**, using the object, not the route. The check receives the authenticated principal and the object (or its identifier) and fails closed. Middleware that only checks "is logged in" does not do this.
- **Load the object through a scoped query.** "Select this invoice where the identifier matches and the owner is the current user and the tenant is the current tenant" is harder to forget than a check written after an unscoped load. Apply the same scope to exports, searches, and bulk identifiers. If any identifier in a bulk list fails the scope, fail the request.
- **Deny by default.** A new route is unauthorized until a rule is added. The framework should make the opposite (open until someone remembers) difficult.
- **Separate property allow-lists per role.** Bind request bodies onto a type that contains only the fields that role may write. Ignore or reject the rest. Do not bind onto the persistence model.
- **Use opaque identifiers if you want defence in depth**, and still authorize. Never accept a tenant identifier, a role, or a price from the client as authoritative.
- **Centralise the policy** so a reviewer can see it. Scattered `if` statements drift. Tests can target a central policy.
- **Return a consistent denial** that does not include the object. Existence oracles are a lesser cousin of the same bug. For sensitive objects, the same response for "not yours" and "does not exist" is appropriate. Document where you chose otherwise.

Regression tests belong in CI: for each object type, an automated check that principal B cannot read principal A's canary. This is an ordinary functional test with two fixtures. It is the highest-value test an application team can add after an assessment like this.

## Detection

- Log the actor, the object type, the object identifier, the action, and the decision. An alert on a surge of denials is useful. An alert on a success that the policy layer cannot explain is better, and it requires the policy layer to be the thing that logs.
- Review new routes in code review with an explicit question: where is the object-level check? A review checklist that says "auth" will be answered with "the user is logged in".
- In production, look for identifiers in URLs that are then requested by a different user id within a short window, if your logs can see both. This is a heuristic with false positives on shared objects. Tune it to object types that are not shared.

## References

- CWE-639 — <https://cwe.mitre.org/data/definitions/639.html>
- CWE-284 — <https://cwe.mitre.org/data/definitions/284.html>
- OWASP Authorization Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html>
- OWASP Access Control Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html>
- OWASP IDOR Prevention Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html>
- OWASP Mass Assignment Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html>
- WSTG IDOR — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References>
- PortSwigger, access control — <https://portswigger.net/web-security/access-control>

## Related in this repository

- [Vulnerability class index](README.md)
- [Web application checklist](../../checklists/web-application-testing.md)
- [API testing checklist](../../checklists/api-testing.md)
- [Finding template](../../templates/finding.md)
- [Where each class is documented](../../resources/vulnerability-classes.md)
- [Disclaimer](../../DISCLAIMER.md)

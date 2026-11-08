# API testing

APIs fail in the same classes as web applications, and they fail more often on authorization because there is no page rendering to hide a missing check. The public catalogue for the failure modes is the [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/). The matching defensive sheet is the [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html). GraphQL and gRPC are the same trust questions over a different encoding: who is the caller, which object did they name, which fields can they read or write, and what does the server do with a value it did not expect.

The checklist is [checklists/api-testing.md](../checklists/api-testing.md).

## Build the map first

Collect, for each in-scope API:

- The base URL and the environment.
- The description the producer publishes (OpenAPI, GraphQL schema, gRPC reflection if it is intentionally enabled) and the routes you actually observe. The difference between those two lists is the shadow-API question (API9, improper inventory).
- The authentication scheme: anonymous, API key, bearer token, mutual TLS, a cookie shared with the website.
- The object types and the identifier style (integer, UUID, a slug that is still a capability).
- The roles the client gave you.

A description file is a claim. Test the deployment, not the file. A route that the description omits and the server still answers is part of the API.

## The ten risks, as test questions

The 2023 list, rewritten as questions an authorised tester can answer with two accounts and a canary:

| ID | Risk | Question |
| --- | --- | --- |
| API1 | Broken object level authorization | Can user A read or change user B's object by naming its identifier? |
| API2 | Broken authentication | Are tokens bound to the client, expired, revoked on logout, and absent from URLs and logs? |
| API3 | Broken object property level authorization | Can a caller set or read a property their role does not own, by sending it or asking for it? |
| API4 | Unrestricted resource consumption | Does a single caller dictate page size, fan-out, or an expensive query with no limit? Confirm with a modest size, not a flood. |
| API5 | Broken function level authorization | Can a normal user call an administrative function if they know the route? |
| API6 | Unrestricted access to sensitive business flows | Can the flow be repeated in a way that breaks a business rule (inventory, invitations, transfers) using test data? |
| API7 | Server-side request forgery | Does the API fetch a URL the caller supplies? Test with a URL you control inside the agreement, not with an internal address, unless the rules allow that proof. See [SSRF](vulnerabilities/ssrf.md). |
| API8 | Security misconfiguration | Verbose errors, unnecessary methods, default credentials, missing TLS, a management port left open. |
| API9 | Improper inventory | Which versions and hosts are live, and which of them are no longer maintained? |
| API10 | Unsafe consumption of APIs | Does this API trust a third-party response (a webhook, a redirect, an identity claim) without validating it? |

API1, API3, and API5 are authorization. They are tested by comparing principals, which is described in [IDOR and access control](vulnerabilities/idor-access-control.md). You do not need a special API payload to show that user A received user B's object. You need user B's canary and a request user A is not supposed to be allowed to make.

## Authentication and tokens

- Send a request with no credential, with a malformed credential, and with an expired credential. The interesting result is a success, or a failure that still returns the object.
- Confirm logout, password change, or key rotation actually invalidates what the server will accept. A token that keeps working has a concrete impact statement.
- Look at where tokens appear: query strings end up in logs and referrers. That is a finding about the design, and the evidence is the request line with the token redacted.
- If the API is called by a browser, the web session notes apply as well: cookie flags, CSRF where cookies authenticate, and CORS. The header checker sends one probe origin and reports a reflective credentialed policy.

Do not brute-force keys or passwords. Do not use a token you found in a public repository. Report the exposure and stop.

## Resource consumption, done safely

API4 is real and easy to turn into an incident. The safe confirmation is a single request that asks for an unreasonable but bounded page size, a very deep GraphQL query of modest cost, or a documented expensive filter, then a comparison with the documented limit. If the server honours a page size far beyond its own documentation, you have the finding. You do not need to ask for the largest number the integer type allows, and you do not need to open a hundred connections. Agree the ceiling with the client when the endpoint is shared or production.

## Webhooks and server-side fetches

A webhook URL or an "import from URL" field is an SSRF and authentication question. The safe approach:

- Prefer a destination the client has placed in scope, or a collector they have approved, so you can show that the server made the request.
- Do not aim the server at link-local addresses, cloud metadata services, or internal ranges unless the rules explicitly allow that proof, and even then stop at "the server issued a request", not "the server returned a credential".
- Remediation is an allow-list, egress control, and authentication of the caller, covered in the SSRF note.

## Errors and mass assignment

Verbose errors that include a query, a stack, or another user's identifier are a finding of their own (information exposure) and a clue to a class. Record the error class. Do not keep pushing until the database falls over.

Mass assignment is API3 in practice: send a property the user interface never displays, using a canary value on your own object ("role", "owner", "price", "isAdmin"), and see whether the server stores it. Use a property name the client confirms is sensitive, or a property you can see on your own administrative read and not on the ordinary read. Confirm by reading the object back. Revert the canary when you are done.

## What the report should say about an API

Group findings by object type and by the missing check, not by the route list. "Every object read is authorized only by possession of the identifier" is one finding with many endpoints. A table of fifty identical rows hides the design defect and buries the one endpoint that is different.

## References

- OWASP API Security Top 10 (2023) — <https://owasp.org/API-Security/editions/2023/en/0x11-t10/>
- OWASP REST Security Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html>
- OWASP Authorization Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html>
- OWASP Mass Assignment Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html>
- OWASP API project — <https://owasp.org/API-Security/>
- API testing checklist — [../checklists/api-testing.md](../checklists/api-testing.md)

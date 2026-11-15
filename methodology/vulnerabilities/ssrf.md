# Server-side request forgery (SSRF)

SSRF is [CWE-918](https://cwe.mitre.org/data/definitions/918.html) and [OWASP Top 10 (2021) A10](https://owasp.org/Top10/2021/). In APIs it is API7 in the [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/). The public test description is [WSTG SSRF](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/19-Testing_for_Server-Side_Request_Forgery), and the fix is the [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).

## What it is

The server issues an HTTP, or other network, request whose destination the caller can influence, and the request runs from the server's network position rather than the caller's. The caller borrows the server's identity and its route to addresses the caller cannot reach: loopback services, private ranges, link-local addresses, and cloud metadata services that hand credentials to anything on the instance that can ask.

Impact depends on what answers. A request that only proves the server can reach a collaborator you own is a reachability finding. A request that returns the body of an internal administrative service, or a cloud credential, is a different incident. This method stops at reachability unless the rules explicitly allow a further proof, and even then the proof uses a canary the client placed, not a live credential.

Redirects, DNS responses that change between the check and the connection, and URL parsers that disagree with each other are the reasons naive filters fail. You do not need a catalogue of those parser disagreements to design the fix. You need the application to decide the destination after it has resolved it, and to refuse destinations that are not on an allow-list.

## Where it appears

- "Import from URL", "preview this link", webhook configuration, and image fetchers.
- PDF and document renderers that retrieve remote resources named in the document.
- Server-side requests hidden inside an integration: an OIDC discovery URL the client supplies, a custom identity endpoint, a build system that clones a caller-supplied repository URL.
- Headers some middleware trusts as the original target. Only treat a header as a sink when you have shown the application uses it to make a request. Host-header issues are a related but separate WSTG topic.

## Responsible testing

1. Find the feature that fetches. Confirm with a URL on a host the client has put in scope, or on a collector the rules name. The evidence you want is a log line on that collector showing the application made the request.
2. Compare with a baseline URL that is supposed to work, so you know the feature functions.
3. If the rules allow an internal-reachability proof, ask the client for a canary listener inside the network they care about, and request that. Do not scan private ranges. Do not request cloud metadata endpoints. Do not ask the server to return secrets. A single agreed URL that answers with a marker is the proof.
4. If the rules do not allow an internal proof, the external collaborator is the whole demonstration, and the impact statement says "the server will issue a request to a caller-chosen destination; internal reachability was not tested". That is an honest finding.
5. Watch for redirects. If your in-scope collector records the first hop and the application then requests somewhere else, stop and report the redirect behaviour. Do not steer the second hop at an internal address you were not given.

One request at a time. SSRF tests that "see what else is open" are a port scan performed from the server, and they are out of scope unless the rules say otherwise.

Parser and metadata tricks are documented in the [WSTG SSRF chapter](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/19-Testing_for_Server-Side_Request_Forgery), the [Web Security Academy](https://portswigger.net/web-security/ssrf), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), and [HackTricks](https://hacktricks.wiki/). They are not reproduced here. Cloud providers document metadata-service hardening in their own manuals. Follow those manuals for the defence, and do not turn a test into a credential-theft exercise.

## Safe confirmation

- The feature, the URL you were allowed to name, and the collector log showing the server as the client.
- The identity the server used, if the collector can see it without receiving a secret (a user agent, a source address the client confirms).
- A clear statement of the proofs you did not attempt.
- If a response body came back, quote only the marker. If the body contains anything else, stop reading it, store the minimum the client asked for, and tell them.

## Remediation

The [SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html) is the checklist. The controls that hold up are:

- **Allow-list destinations.** Accept a small set of schemes, hosts, and ports that this feature needs. Prefer "the application already knows the URL" over "the caller supplies a URL". If the product truly must fetch arbitrary public URLs, isolate that fetcher on a network that cannot route to internal ranges, metadata addresses, or loopback.
- **Resolve, then decide, then connect to the address you resolved.** Check the resolved address against the deny ranges (loopback, link-local, private, and the current metadata ranges for the clouds you run). Re-check on every redirect. A check that looks only at the hostname string is not a check.
- **Disable redirects** unless the next hop is validated the same way. Cap the number of hops.
- **Do not return the response body to the caller** unless the feature requires it, and even then return a processed subset. Many SSRF bugs are severe because the application is an open proxy back to the caller.
- **Block cloud metadata** at the instance and at the network. Where the provider offers a session-oriented metadata service and a hop limit, turn those on so a request that merely reaches the instance still cannot read a role credential. Use the provider's current documentation. Do not depend on an application deny-list of a single address, because addresses and hostnames change.
- **Give the fetcher its own identity** with no cloud role and no access to internal services. A compromise of the fetcher should be boring.

Denial of odd encodings and odd IP spellings is useful only as a supplement to resolving and allow-listing. There will always be another spelling.

## Detection

- Log every outbound request the application makes on behalf of a user: destination host, resolved address, feature, actor, result. Alert when the resolved address is private, link-local, or a metadata range.
- Alert when an application role that never makes arbitrary requests starts doing so.
- Network policy logs are the backstop: a deny event from the fetcher subnet toward the metadata service or the internal administration ranges is a detection, not a surprise.
- In CI, a test that points the feature at a reserved address and expects a refusal. Use the address in the test fixture the client owns, not as a payload list in the report.

## References

- CWE-918 — <https://cwe.mitre.org/data/definitions/918.html>
- OWASP SSRF Prevention Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html>
- WSTG SSRF — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/19-Testing_for_Server-Side_Request_Forgery>
- OWASP API Security Top 10 (2023) — <https://owasp.org/API-Security/editions/2023/en/0x11-t10/>
- PortSwigger, SSRF — <https://portswigger.net/web-security/ssrf>

## Related in this repository

- [Vulnerability class index](README.md)
- [Web application checklist](../../checklists/web-application-testing.md)
- [API testing checklist](../../checklists/api-testing.md)
- [Finding template](../../templates/finding.md)
- [Where each class is documented](../../resources/vulnerability-classes.md)
- [Disclaimer](../../DISCLAIMER.md)

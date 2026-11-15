# API testing checklist

Use this for an HTTP API you are authorised to test, alongside [API testing](../methodology/06-api-testing.md) and the [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/). The same rules of engagement that cover the website do not automatically cover a different host or a partner API.

## Inventory

- [ ] Every base URL, version prefix, and environment is listed and matched to scope.
- [ ] You have an official specification (OpenAPI or equivalent), or you recorded that you are working from observed traffic.
- [ ] Undocumented routes you observed were reported as inventory and tested only if they are on an in-scope host.
- [ ] Deprecated versions still mounted in production are in the asset list.
- [ ] Webhooks, asynchronous callbacks, and "import this URL" features are identified. They are SSRF candidates. See [SSRF](../methodology/vulnerabilities/ssrf.md).

## Authentication

- [ ] You know which scheme is in use (session, bearer token, mutual TLS, signed request) and where the secret lives.
- [ ] Tokens you were given are for test tenants. You are not replaying a token found in a public repository.
- [ ] Expired, malformed, and missing credentials receive a failure from the server, which you confirmed with one request each.
- [ ] A token for tenant A was not accepted against tenant B's host, if the design has more than one tenant.
- [ ] Refresh and revocation behave: a revoked token stays revoked.

## Authorization

- [ ] Object-level checks were compared across two principals (BOLA / IDOR). See [access control](../methodology/vulnerabilities/idor-access-control.md).
- [ ] Function-level checks were compared across two roles (a reader calling a writer or an administrator route).
- [ ] Property-level checks were compared: a response and a write payload were reviewed for fields the caller should not see or set.
- [ ] Identifiers in headers, paths, query strings, and bodies were all included in the comparison.

## Data and behaviour

- [ ] Mass assignment was tested by adding one field the client should not control, on a test object.
- [ ] Resource consumption was observed (page size, batch size, expensive filters) without attempting to exhaust the service.
- [ ] Business flows that must not be automated (checkout, invite, password reset) have a control you can describe, or you recorded the gap without driving the flow in volume.
- [ ] Error bodies do not return stack traces, SQL, or other tenants' identifiers.
- [ ] CORS on credentialed responses reflects only the origins the client named.

## Dependencies of the API

- [ ] The API's consumption of other APIs (webhooks it receives, URLs it fetches, files it parses) is in the notes.
- [ ] GraphQL or similar query languages, if present, have a depth and cost limit you observed, and introspection is either intended or recorded as a finding.
- [ ] An LLM feature in front of the API was reviewed with [prompt injection](../methodology/vulnerabilities/llm-prompt-injection.md), with the tools treated as the boundary.

## Close-out

- [ ] The specification and the live behaviour disagree in places you wrote down, even where the live behaviour was safe.
- [ ] Test objects you created are listed for deletion.
- [ ] Findings cite the API Security Top 10 category and the concrete route, not only the category name.

## Related in this repository

- [Checklist index](README.md)
- [API testing](../methodology/06-api-testing.md)
- [Access control](../methodology/vulnerabilities/idor-access-control.md)
- [SSRF](../methodology/vulnerabilities/ssrf.md)
- [Disclaimer](../DISCLAIMER.md)

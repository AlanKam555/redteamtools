# Web application testing checklist

Use this on an application you are authorised to test, alongside [web application testing](../methodology/05-web-application-testing.md) and the class notes in [methodology/vulnerabilities](../methodology/vulnerabilities/README.md). The goal of each box is a decision: confirmed, not present in the sample, or not tested, with a reason.

## Setup

- [ ] Scope in the proxy matches the rules of engagement.
- [ ] You have at least two principals when the application has more than one role.
- [ ] You recorded the build, the tenant, and the environment.
- [ ] Automated scanning is either allowed and rate-limited, or turned off.

## Transport and browser controls

- [ ] HTTP redirects to HTTPS, and HSTS is present on the HTTPS response. The [header checker](../tools/security_header_checker.py) is enough for a single URL.
- [ ] The certificate matches the name and chains to a trusted root. The [TLS checker](../tools/tls_config_checker.py) covers one host.
- [ ] Session cookies are `Secure` and `HttpOnly`, with an explicit `SameSite`.
- [ ] A content security policy exists, and you noted whether it still allows inline script.
- [ ] Framing is restricted with `frame-ancestors` or `X-Frame-Options`.

## Authentication and session

- [ ] Login, logout, and password or recovery flows were exercised with the test accounts only.
- [ ] Session identifiers change across login.
- [ ] Logout invalidates the server-side session, which you checked by replaying the old request.
- [ ] Multi-factor authentication, where the design says it exists, is enforced on the roles that need it.
- [ ] Error messages do not tell you which half of the credential was wrong in a way the client has not accepted.
- [ ] Account lockout or rate limiting was observed gently, not driven to a customer-facing outage.

## Access control

- [ ] Horizontal access was compared: principal A requested an object created by principal B, using B's identifier and A's session.
- [ ] Vertical access was compared: a lower role requested an action you saw a higher role perform.
- [ ] Identifiers in the body, the query, and the path were all considered, not only the one in the URL.
- [ ] A forced-browsing sample of administrative paths, using the lower role, returned the authorization decision rather than the page.
- [ ] Multi-step flows re-check authorization on the step that performs the action.

## Input handling

- [ ] Reflected and stored output was sampled with a benign marker before any class-specific test. See [XSS](../methodology/vulnerabilities/xss.md).
- [ ] A query that the application turns into a database call was compared with a parameterised baseline. See [SQL injection](../methodology/vulnerabilities/sql-injection.md).
- [ ] Features that fetch a URL, render a template, parse XML, or shell out were identified and tested within the class notes for [SSRF](../methodology/vulnerabilities/ssrf.md), [SSTI](../methodology/vulnerabilities/ssti.md), [XXE](../methodology/vulnerabilities/xxe.md), and [command injection](../methodology/vulnerabilities/command-injection.md).
- [ ] File upload, if present, was checked for where the file is stored and who can later retrieve it, not only for the extension.
- [ ] State-changing requests were checked for a cross-site request forgery control that is bound to the session.
- [ ] Mass assignment was considered wherever the client sends a whole object and the server persists it.

## Client and logic

- [ ] Price, role, and status fields that the browser sends were modified once to see whether the server believes them.
- [ ] Redirects and return URLs stay on the application's own hosts.
- [ ] Sensitive actions have an audit event you can see, or you recorded that they do not.

## Close-out

- [ ] Each candidate is either a finding with sanitised evidence or a note explaining why it was discarded.
- [ ] You did not keep a copy of another user's real data. Canaries and test records are identified so the client can delete them.
- [ ] Tools were stopped, and the project file is in the engagement store.

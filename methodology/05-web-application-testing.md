# Web application testing

Web testing is a walk over the trust boundaries of an application you are allowed to test, using the [OWASP Web Security Testing Guide](https://wstg.owasp.org/) as the catalogue and the class notes in this repository as the depth. It is authenticated when the client has given you accounts, and it is paced so that a production system, if production is even in scope, still serves its users.

The checklist is [checklists/web-application-testing.md](../checklists/web-application-testing.md). A proxy workflow is described in [cheatsheets/burp-suite.md](../cheatsheets/burp-suite.md). [OWASP ZAP](https://www.zaproxy.org/) is the free public alternative and is documented by the [OWASP ZAP project](https://owasp.org/www-project-zap/).

## Before the first interesting request

- Confirm the host, the environment, and the window against the rules of engagement.
- Configure the proxy's scope so logging and active features stay on the named hosts. A browser will happily wander into a third-party analytics domain. The proxy should not attack it just because the page loaded it.
- Note the build, the commit, or the release the client said you are testing.
- Map roles to accounts. Label the proxy project with the account so a screenshot next week is still attributable.
- Send a baseline request for each major route and keep the ordinary response. Every later comparison needs it.

## Coverage, in the order that usually pays off

1. **Session and transport.** Cookies, tokens, logout, cache, and TLS. The header and TLS utilities in `tools/` cover the configuration half. Session behaviour (does logout invalidate the server-side session, does a session survive a password change) is an application test and is covered with the authentication note.
2. **Access control.** For each object and each action, compare two users in the same role and one user in a lower role. This is where engagements actually find impact, and it does not require a payload catalogue. See [IDOR and access control](vulnerabilities/idor-access-control.md).
3. **Authentication and account recovery.** Only against the identity system that is in scope. See [authentication flaws](vulnerabilities/authentication-flaws.md).
4. **Input handling, by sink.** Once you know where data is rendered, queried, fetched, parsed, templated, or executed, test that class and stop. The class notes are the method. The WSTG pages linked from those notes are the public step-through.
5. **Business logic.** Limits, prices, quantities, workflow order, and features that exist only as a client-side button. These are specific to the application. Describe the rule you think exists, then show a request that breaks it using your own test data.
6. **Client-side secrets and configuration.** Anything shipped to the browser is public. A key in a script is a finding about where that key is accepted, not a surprise about the browser.
7. **Dependency and configuration issues** confirmed as in [vulnerability analysis](04-vulnerability-analysis.md).

Automated crawling and scanning supplement the map. They do not replace the role comparison or the business-logic pass. If a scanner is permitted, exclude intrusive and availability checks, throttle it, and read what it sent before you believe the row.

## How to test a class without a payload library in your notes

The pattern, repeated in every vulnerability note:

- Find the sink during enumeration (a parameter reflected into HTML, a value concatenated into a query, a URL the server fetches, an identifier that selects a row).
- Send a benign marker you can recognise, with no special meaning to a browser, a database, or a shell.
- Observe whether the application treats the marker as data. Encoding, parameterisation, and authorization all have visible, safe symptoms: the marker comes back encoded, the query behaviour does not change when the marker contains characters the parser would care about, a second user receives a denial.
- Only if the rules allow a proof beyond that symptom, use the smallest public test case from the WSTG or the Web Security Academy that demonstrates the class, against test data, and stop.
- Do not chain the result into a second system, a real user's session, or a persistent foothold.

If a colleague cannot tell, from your notes, what you compared and what you refused to do, the note is not finished.

## Evidence that belongs in the finding

- Route, parameter or object type, and the role.
- Baseline and variant, described. Where a request would contain a live exploit string, replace the string in the client-facing report with the class ("a benign marker was returned inside an HTML text node without encoding") and keep the raw exchange in the restricted evidence store.
- Impact in one or two sentences, tied to the data the role was not supposed to reach or the action it was not supposed to take.
- The control that failed (missing server-side check, string-built query, disabled encoder) and the control that would have contained it (CSP, least-privilege database role, egress filter).

## Safety

- Writes, deletes, emails, and payments use test records and test inboxes.
- One-at-a-time is the default on authentication, password reset, and anything that locks an account or sends a message.
- If the application returns someone else's personal data, stop reading, capture the minimum evidence the client asked for (often just the fact of the foreign identifier and the response code), and move the detail into the restricted store.
- If responses slow down or error rates rise, stop and call the emergency contact. You can resume after they say so.

## Defensive counterpart

The matching engineering work is the [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/): access control on every object, output encoding, parameterised queries, session controls, and logging. Teams that already test against an ASVS level turn this engagement into a confirmation exercise. Teams that do not, turn it into the first time those requirements are written down. Either outcome is useful if the report says which one it was.

## References

- OWASP Web Security Testing Guide — <https://wstg.owasp.org/>
- OWASP ASVS — <https://owasp.org/www-project-application-security-verification-standard/>
- OWASP Top 10 (2021) — <https://owasp.org/Top10/2021/>
- PortSwigger Web Security Academy — <https://portswigger.net/web-security>
- OWASP ZAP — <https://www.zaproxy.org/>
- Web testing checklist — [../checklists/web-application-testing.md](../checklists/web-application-testing.md)

## Related in this repository

- [Methodology index](README.md)
- [Web checklist](../checklists/web-application-testing.md)
- [API testing](06-api-testing.md)
- [Vulnerability classes](vulnerabilities/README.md)
- [Burp Suite cheatsheet](../cheatsheets/burp-suite.md)
- [Headers and TLS](../cheatsheets/http-headers-and-tls.md)
- [Finding template](../templates/finding.md)
- [Disclaimer](../DISCLAIMER.md)

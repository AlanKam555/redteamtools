# Authentication flaws

Authentication failures are [CWE-287](https://cwe.mitre.org/data/definitions/287.html) and [OWASP Top 10 (2021) A07](https://owasp.org/Top10/2021/). The API-shaped version is API2 in the [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/). The public test catalogue is the WSTG authentication chapter, including [bypassing an authentication schema](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/04-Authentication_Testing/04-Testing_for_Bypassing_Authentication_Schema). The design references are the [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), the [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), the [Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html), and [NIST SP 800-63-4](https://csrc.nist.gov/pubs/sp/800/63/4/final) for digital identity.

Credential stuffing, password spraying, and online brute force are not part of this method unless the rules of engagement contain a separate, rate-capped plan. They lock real people out and they are easy to confuse with an attack the defenders were not told about. The tests below use accounts the client gave you.

## What it is

The application accepts a claim about who the caller is, and that claim is weaker than the application thinks. The claim might be a password, a session token, a remember-me cookie, a password-reset link, an OAuth or OIDC redirect, an API key, or a mutual TLS certificate. The flaw is anything that lets a caller become a principal they are not, or remain a principal after they should have stopped.

Session management is included here because a perfect password check followed by a session that never dies, or that the attacker can fix in advance, is still an authentication failure. Authorization, which decides what an authenticated principal may do, is covered in [IDOR and access control](idor-access-control.md). Keep the two separate in the report so the fix lands in the right layer.

## Where it appears

- Login, logout, registration, email or phone change, and password reset.
- Multi-factor enrolment and step-up prompts, including "remember this device".
- Session cookies and bearer tokens, including tokens placed in URLs.
- SSO and OAuth or OIDC: the redirect target, the state parameter, the nonce, the audience, and the signature of the assertion.
- API keys and personal access tokens, including keys that appear in a mobile binary or a public repository.
- Administrative consoles with a default, documented, or shared credential.
- A second, older login path (a mobile API, a report scheduler, a "legacy" subdomain) that does not enforce the control the main site added.

## Responsible testing

Work through the lifecycle with the test accounts, one change at a time.

**Transport and storage of the secret.**

- The login and the reset flow are HTTPS only. The [TLS checker](../../tools/tls_config_checker.py) and the cookie flags from the [header checker](../../tools/security_header_checker.py) cover the configuration. A session cookie without `Secure` or `HttpOnly` is a finding even when you never steal it.
- Tokens do not appear in query strings. If the application puts one there, the evidence is the request line with the token redacted, plus a note about referrers and access logs.

**The session.**

- Log in, record the session identifier, log out, and show that the same identifier is no longer accepted. Repeat after a password change on the test account.
- Confirm the identifier changes when the user authenticates, so a value fixed before login cannot be forced on the user (session fixation).
- Confirm a session has an expiry and an idle timeout that match the client's policy. Quote the policy. Do not argue with a risk appetite that is written down. Do argue with a session that the policy says expires and that does not.

**Recovery.**

- Request a reset for a test account. Confirm the token is single-use, expires quickly, and is not predictable from anything you can see (a timestamp, a user id). You can show unpredictability by asking the client how it is generated, or by inspecting the code. Do not attempt to guess tokens.
- Confirm the reset flow does not tell a stranger whether an email address is registered, if the client's policy is to avoid that oracle. Some products accept the oracle. Record the choice rather than inventing a vulnerability the client has accepted.
- Confirm you cannot reset an account you do not own by changing the identifier in the request. That is authorization on the reset function, and it belongs in the finding if it fails.

**Factors.**

- Where MFA is supposed to be required, confirm a test account cannot finish a sensitive action with only the first factor, including through the older API. The bypass is often a second route, not a broken code check.
- Confirm backup codes and "remember this device" can be revoked. Do not disable MFA on an account a real person uses.

**Federation.**

- Confirm the application, not the browser, validates the token signature, the issuer, the audience, and the expiry.
- Confirm the redirect destination is an allow-list. A caller-supplied redirect that leaves the site is an open-redirect finding ([CWE-601](https://cwe.mitre.org/data/definitions/601.html)) and, in an OAuth flow, a token-theft risk. Demonstrate with a destination the client has approved, not with a server you operate outside the agreement.
- Confirm a `state` or equivalent CSRF defence is present and checked on the login callback, and that a `nonce` is checked on the identity token when the flow uses one. The public OIDC threat model is the specification and the identity provider's documentation. This note does not restate the protocol.

**Defaults and secrets.**

- Ask the client for the list of default accounts and confirm they are gone. Trying a list of common passwords against a production login is a brute-force test and needs the separate plan mentioned above.
- If reconnaissance finds a key in a public repository, report the location and stop. Do not use the key.

The [Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) and the WSTG authentication chapter contain the longer public test list, including the cases this method refuses to run without an explicit rule (lockout testing at scale, default-password lists, credential stuffing).

## Safe confirmation

- The flow, the test account, and the symptom (a session accepted after logout, a reset token reused, a sensitive action completed without the second factor, a redirect to an agreed external marker).
- Redacted evidence. Never paste a live session, a reset token, a password, or an authorization code into the report or into this repository.
- The second route you checked, so the client does not fix only the page you happened to use.
- Anything you changed (a password on a test account, a revoked session) and the fact you restored it or handed it back.

## Remediation

- Adopt a current identity platform or follow [NIST SP 800-63-4](https://csrc.nist.gov/pubs/sp/800/63/4/final) directly. Practical consequences that teams mis-implement: long passwords are more useful than composition rules, breached-password screening beats rotation on a calendar, and SMS is a weaker factor than a phishing-resistant authenticator for administrative access.
- Issue session identifiers from the server, from a cryptographic generator, and rotate them on authentication. Invalidate them on logout, password change, and factor change. Store server-side state or use a signed token format you can revoke.
- Set `Secure`, `HttpOnly`, and an explicit `SameSite` on session cookies. Do not put bearer tokens in URLs or in local storage if a cookie with those flags will do. The [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) has the detail.
- Rate-limit authentication and recovery per account and per source, and alert on the limit. Prefer a response that does not lock a person out forever because someone else tried their username. The [Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) discusses the trade-off.
- Build recovery tokens as random values, stored hashed, single-use, and short-lived. Bind the reset to the account that requested it.
- Require MFA for administrative and production access, and make every route, including older APIs and "remember me", honour it. The [Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html) covers enrolment and recovery.
- For OAuth and OIDC, use a maintained library, validate issuer, audience, expiry, and signature, allow-list redirect URIs exactly, and check `state` and `nonce`. Do not accept a token whose signature you did not verify because you "trust the network".
- Remove default credentials in deployment. Scan your own code and CI logs for secrets, using the practices in the [Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html).

## Detection

- Log authentication successes and failures, password changes, reset requests, factor changes, and session revocations, with a stable account identifier and a source, without the password or the token.
- Alert on a spike of failures, on a success from a new factor, and on an administrative login that bypasses MFA.
- Alert when a token or a cookie value appears in a URL log. That is a pipeline bug as well as an application bug.
- Review new authentication routes as a privileged change. A second login path added by a feature team is the usual bypass.

## References

- CWE-287 — <https://cwe.mitre.org/data/definitions/287.html>
- CWE-601 — <https://cwe.mitre.org/data/definitions/601.html>
- NIST SP 800-63-4 — <https://csrc.nist.gov/pubs/sp/800/63/4/final>
- OWASP Authentication Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html>
- OWASP Session Management Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html>
- OWASP Multifactor Authentication Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html>
- OWASP Secrets Management Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html>
- WSTG bypassing authentication schema — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/04-Authentication_Testing/04-Testing_for_Bypassing_Authentication_Schema>
- PortSwigger, authentication — <https://portswigger.net/web-security/authentication>

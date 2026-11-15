# Cross-site scripting (XSS)

XSS is [CWE-79](https://cwe.mitre.org/data/definitions/79.html). It sits in [OWASP Top 10 (2021) A03, Injection](https://owasp.org/Top10/2021/), and the public test descriptions are [WSTG reflected XSS](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/01-Testing_for_Reflected_Cross_Site_Scripting) and [WSTG stored XSS](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting). PortSwigger's overview is the [cross-site scripting topic](https://portswigger.net/web-security/cross-site-scripting).

## What it is

The application takes data it does not fully control and places it into a browser context where the browser will interpret it as code: an HTML document, an attribute, a URL, a script block, or a DOM API that parses HTML. The caller's data and the page's instructions share one channel, and the application failed to encode for the context it used.

Three delivery shapes matter because the fix and the evidence differ:

- **Reflected.** The response to this request echoes the input. The victim has to be induced to send the request. Impact is usually session abuse or an action performed as the victim, inside the site's origin.
- **Stored.** The application saves the input and serves it later to other users. Impact scales with whoever is allowed to view that page.
- **DOM-based.** The browser itself takes data from a source such as the URL, storage, or a message and inserts it through a dangerous sink. The server's logs may never see the payload. The source and the sink are both in client-side code.

XSS is a confidentiality and integrity bug against the user of the origin. It is not "alert boxes". A script running in the origin can read the DOM, act as the user, and sometimes read a token the application placed in the page. Cookies marked `HttpOnly` are not readable to script, which is why that flag is necessary and also why it is not a cure for XSS.

## Where it appears

- Any template that disables encoding, concatenates HTML, or uses a "raw" or "safe" marker on untrusted data.
- Rich-text fields, comments, profiles, and file names rendered into HTML.
- Error pages that echo a parameter.
- Client-side code that assigns to `innerHTML`, writes the document, builds a URL with a script scheme, or evaluates a string. Those are sinks. Treat the URL, referrer, storage, and `postMessage` data as sources.
- PDF, email, and SVG renderers that the application hosts. The context is still "something will parse this as a document".

## Responsible testing

Map the reflection or the sink before you try to execute anything.

1. Place a unique benign marker, with no HTML or script meaning, into the parameter or the stored field. Use a marker you can search for.
2. Find where it comes back: HTML text, an attribute, a JavaScript string, a URL, a JSON body that a script later inserts into the DOM.
3. Compare with the baseline. If the marker is encoded for that context (text encoded as text, an attribute encoded as an attribute), the output encoder is doing its job for this path. Record the positive observation and move on.
4. If the marker is returned raw into an HTML or script context, you have a strong indication of the class. Confirm the context from the response or from the client-side sink, not from a guess.
5. Only with permission, and only against a test account, demonstrate execution with the smallest public test case from the WSTG or the Web Security Academy that matches the context. Do not borrow another user's session, do not persist a payload in a field real users view, and do not call infrastructure outside the agreement.

Stored XSS needs a cleanup plan before the write: a test record you can delete, and a viewer role that is also a test account. Writing a proof into a public page and leaving it there is an incident.

DOM XSS is confirmed by reading the client-side flow from source to sink and showing, with a benign marker, that the source reaches the sink. A browser proof uses a test page and a test user.

This repository does not include a payload catalogue. Context-specific strings are maintained by the [OWASP testing guide](https://wstg.owasp.org/), the [Web Security Academy](https://portswigger.net/web-security/cross-site-scripting), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), and [HackTricks](https://hacktricks.wiki/).

## Safe confirmation

Enough evidence for the finding:

- The request or the stored field, the marker, and the response context, showing the marker unencoded where encoding was required.
- The role that can submit it and the role that renders it.
- For a DOM sink, the source, the sink, and the code path between them.
- A statement of what you did not do: no other user's session, no content left on a page real users see, no external callback unless the rules named one.

A screenshot of a dialog is optional and often unhelpful. The unencoded context is the defect. The dialog is theatre unless the client needs it to believe the context is executable.

## Remediation

The primary fix is **contextual output encoding** at the moment data enters a document. Encode for the context you are actually in:

- HTML text is not the same as an HTML attribute, which is not the same as a JavaScript string, which is not the same as a URL component.
- Perform that encoding in the template layer that knows the context. A framework's default encoder is the right tool when the team has not switched it off.
- Do not build HTML by concatenating strings in application code. When a framework offers a raw-output escape hatch, require a review for every use and keep untrusted data out of it.

For rich text that is supposed to contain markup, encoding everything would destroy the feature. Use a maintained sanitiser with an allow-list of elements and attributes, on output as well as on input, and keep the sanitiser's version current. Treat a home-grown list of banned tags as a bug. The [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html) is the reference for the contexts and for sanitiser guidance. The [XSS Filter Evasion Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html) exists to show why filters fail. Link it for that lesson, and do not copy it into a report as a fix list.

Containment, which does not replace encoding:

- A [Content Security Policy](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html) that does not allow inline script or evaluation, using nonces or hashes for the scripts you ship. A report-only policy is a measurement tool, not a control.
- `HttpOnly` and `Secure` on session cookies, and `SameSite` as appropriate, so script that does run cannot read the cookie. See the [Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html).
- Trusted Types, where the application can adopt them, so DOM sinks refuse strings that did not pass through a checked policy.
- Avoid sinks that parse HTML if a text API does the job.

Input validation is useful for structured fields (an identifier, a colour, an enum) and is not a general XSS fix. Attackers encode. The browser decodes. The encoder at the sink is what stays aligned with the parser.

## Detection

- Template reviews and static analysis that flag raw-output constructs and DOM sinks (`innerHTML` and equivalents, document writes, evaluation of strings).
- A regression test that submits a marker and asserts it is encoded in the rendered context. This is a unit or view test, and it does not require an exploit string. Asserting on a known-bad payload in perpetuity is how teams build a private payload list that goes stale. Asserting that a punctuation-bearing marker is encoded is enough.
- CSP violation reports, collected on a system the application team owns, reviewed as defects rather than as noise.
- For stored content, a render-time sanitiser check in CI against the allow-list, plus monitoring for sanitiser bypass advisories.
- A WAF rule is containment at the edge. It misses DOM XSS and it misses novel encoding. Do not accept "the WAF will catch it" as the remediation.

## References

- CWE-79 — <https://cwe.mitre.org/data/definitions/79.html>
- OWASP XSS Prevention Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html>
- OWASP Content Security Policy Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html>
- WSTG reflected XSS — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/01-Testing_for_Reflected_Cross_Site_Scripting>
- WSTG stored XSS — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting>
- PortSwigger, cross-site scripting — <https://portswigger.net/web-security/cross-site-scripting>

## Related in this repository

- [Vulnerability class index](README.md)
- [Web application checklist](../../checklists/web-application-testing.md)
- [API testing checklist](../../checklists/api-testing.md)
- [Finding template](../../templates/finding.md)
- [Where each class is documented](../../resources/vulnerability-classes.md)
- [Disclaimer](../../DISCLAIMER.md)

# Burp Suite and the proxy workflow

[Burp Suite](https://portswigger.net/burp/documentation) is a manual testing proxy. [OWASP ZAP](https://www.zaproxy.org/) is the free public tool that fills the same role and is documented by the [OWASP ZAP project](https://owasp.org/www-project-zap/). The workflow below is the same in either tool. The web method is [web application testing](../methodology/05-web-application-testing.md).

This page does not describe scanner policies or payload lists. Those live in the vendor documentation and in the OWASP testing guide, and they are subject to the rules of engagement.

## Scope the proxy first

- Add the in-scope hosts to the tool's target scope before you browse.
- Turn off anything that attacks out-of-scope URLs. Browsers request analytics, fonts, and identity providers on their own.
- Use a project file that is encrypted with a password you store under the engagement's rules, because the history will contain session tokens.
- Give each test account its own browser profile or its own project, so a request is still attributable next week.

## The loop

1. Browse the feature as the intended user and find the request that performs the action.
2. Send that request to the repeater (or ZAP's equivalent). Change one thing. Send it. Compare with the baseline you saved.
3. For access control, replace the session with the second test account's session and send the same request again. Do not change two things at once, or you will not know which change mattered.
4. For an input class, insert a benign marker first and observe the context. Only then, if the rules allow and the class note says a proof is appropriate, use a single public test case from the WSTG or the Web Security Academy.
5. Log the result in the engagement notes: account, route, what you changed, what came back, what you refused to do.

The interceptor is for the requests you intend to hold. Leaving it on and walking away stalls the browser and can leave a half-finished write on the server. Finish the request or drop it.

## Scanner and active features

Automated crawling and active scanning are optional and often forbidden on production. If they are allowed:

- Restrict them to the scope you configured.
- Exclude authentication lockout paths or give them the test account and a low rate.
- Read the issues. A scanner row is a hypothesis until the repeater reproduces it.

## Evidence

- Export the single request and response that prove the finding, then redact tokens and personal data before anything is copied into the report.
- Keep the project file in the engagement store, not in git.
- Record the tool and the build. "Burp" is not a methodology. The comparison you performed is the methodology.

## Official documentation

- Burp Suite documentation — <https://portswigger.net/burp/documentation>
- OWASP ZAP — <https://www.zaproxy.org/>
- PortSwigger Web Security Academy — <https://portswigger.net/web-security>

## Related in this repository

- [Cheatsheet index](README.md)
- [Web application testing](../methodology/05-web-application-testing.md)
- [Web checklist](../checklists/web-application-testing.md)
- [Headers and TLS](http-headers-and-tls.md)
- [Disclaimer](../DISCLAIMER.md)

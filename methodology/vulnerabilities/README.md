# Vulnerability classes

These notes describe weakness classes that show up in ordinary web and API assessments. Each one is written so that an authorised tester can recognise the class and prove it safely, and so that an engineer can remove the class rather than patch a single parameter.

They are aligned with [CWE](https://cwe.mitre.org/), the [OWASP Top 10 (2021)](https://owasp.org/Top10/2021/), the [OWASP Web Security Testing Guide](https://wstg.owasp.org/), and the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/). Prompt injection follows the [OWASP GenAI project](https://genai.owasp.org/).

This directory does not contain exploit strings. The public catalogues linked from each note exist for that purpose and carry their own licences and terms. Use them in a lab or under a rules of engagement, not against a system you have not been allowed to test.

| Class | CWE | Note |
| --- | --- | --- |
| Cross-site scripting | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) | [xss.md](xss.md) |
| SQL injection | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) | [sql-injection.md](sql-injection.md) |
| Server-side request forgery | [CWE-918](https://cwe.mitre.org/data/definitions/918.html) | [ssrf.md](ssrf.md) |
| OS command injection | [CWE-78](https://cwe.mitre.org/data/definitions/78.html) | [command-injection.md](command-injection.md) |
| Server-side template injection | [CWE-1336](https://cwe.mitre.org/data/definitions/1336.html) | [ssti.md](ssti.md) |
| XML external entities | [CWE-611](https://cwe.mitre.org/data/definitions/611.html) | [xxe.md](xxe.md) |
| IDOR and access control | [CWE-639](https://cwe.mitre.org/data/definitions/639.html), [CWE-284](https://cwe.mitre.org/data/definitions/284.html) | [idor-access-control.md](idor-access-control.md) |
| Authentication flaws | [CWE-287](https://cwe.mitre.org/data/definitions/287.html) | [authentication-flaws.md](authentication-flaws.md) |
| Deserialization | [CWE-502](https://cwe.mitre.org/data/definitions/502.html) | [deserialization.md](deserialization.md) |
| LLM prompt injection | OWASP LLM01 | [llm-prompt-injection.md](llm-prompt-injection.md) |

## Shared testing rules

- You have written authorisation for the asset, the account, and the window.
- You have a baseline response before you change anything.
- The first probe is a benign marker or a second test principal, not a public exploit.
- You stop when the class is shown. You do not pivot, persist, or collect real customer data.
- You can explain the failed control in a sentence an engineer can act on.
- You attach the detection gap as well as the code fix.

## Shared remediation habits

- Perform the security decision on the server, in a place the caller cannot skip.
- Prefer a language or framework feature that makes the dangerous thing structurally hard (parameterised queries, contextual encoding, an authorization middleware that receives the object).
- Treat deny-lists of bad characters as a temporary containment, not as the fix.
- Give the application identity the least privilege that still lets it run, so a missed check has a small blast radius.
- Log the actor, the object, the action, and the decision, and alert on the pattern this class produces.

The [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/) is the requirement set these habits map back to.

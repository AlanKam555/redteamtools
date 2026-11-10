# Server-side template injection (SSTI)

Server-side template injection is [CWE-1336](https://cwe.mitre.org/data/definitions/1336.html). It is a form of code injection, [CWE-94](https://cwe.mitre.org/data/definitions/94.html), aimed at the template engine rather than at a shell. The public test description is [WSTG server-side template injection](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/18-Testing_for_Server-side_Template_Injection). PortSwigger's topic page is the [server-side template injection overview](https://portswigger.net/web-security/server-side-template-injection). There is no separate OWASP prevention cheat sheet dedicated to templates. Use the [Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html) for the general rule, and this note for the template-specific design.

## What it is

The application treats untrusted data as a template, or it inserts untrusted data into a template in a way that the engine still evaluates. Template engines exist to mix a trusted template with untrusted data. The bug is a mix-up of those two roles: the user supplies the template, or the user's value is concatenated into the template string before compilation.

The impact is the impact of running code in the template's environment. Many engines expose the language runtime, the filesystem, and the process environment to a template that asks. A "sandboxed" mode is a reduction in that exposure, not a guarantee. Sandboxes for template engines have a long history of escape. Design as if the sandbox will fail, and do not give untrusted authors a template.

This is distinct from cross-site scripting. XSS runs in the visitor's browser. SSTI runs on the server, before the page is sent. Encoding the output will not save you if the engine already executed the template.

## Where it appears

- User-editable email, invoice, or page templates stored as text and compiled on the server.
- Error pages, notification formatters, and "customise this message" features that pass the string through the same engine the application uses for its own pages.
- A template path or template name the caller can influence, so a different file is compiled.
- Debugging features that render an expression from a query parameter.

A template that is fixed in the repository and receives user data only as a declared variable is the safe pattern. Confirm that the variable is passed as data. Some engines stringify and re-parse if the developer calls the wrong function.

## Responsible testing

1. Determine whether the user controls the template source, the template name, or only a variable. Read the code if you can. The first two are the defect. The third is safe unless the engine is being misused.
2. If the user controls the source, you already have a design finding. Confirm with a benign marker that has no template meaning and is stored as the template, and show that the server later renders it. You do not need an expression that runs code to show that the user is the author of a server-side template.
3. If you need to show that the engine evaluates syntax, agree a canary expression with the client that returns a marker and does nothing else (no file read, no process, no outbound connection). One expression, on a test record, in a test environment. If you cannot think of an expression that is harmless, do not invent one in production. Report the design defect and stop.
4. Do not use public "universal payload" lists against a live template editor. They are aimed at identifying the engine by side effects and at escaping sandboxes. Identification of the engine can be done by asking the client or by reading the dependency file.

Engine-specific syntax is documented in the [WSTG chapter](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/18-Testing_for_Server-side_Template_Injection), the [Web Security Academy](https://portswigger.net/web-security/server-side-template-injection), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), and [HackTricks](https://hacktricks.wiki/). Use those sources in a lab. Do not paste them into a production editor "to see which one works".

## Safe confirmation

- Where the template text comes from (a user field, a tenant setting, a file path the caller names).
- Evidence that the server compiles that text: a rendered marker, or the code that passes the string to the engine's compile function.
- The identity the renderer runs as, from configuration, so the impact sentence is accurate.
- A statement that you did not read files, list environment variables, or execute a process through the engine.

If a canary expression returns a computed marker the baseline cannot explain, that is enough execution proof. Stop. A second expression that opens a file is a different, unnecessary test.

## Remediation

- **Keep untrusted data out of the template source.** Authors of templates are developers, reviewed and shipped with the application, or a tightly controlled admin action that is audited. End users supply data, which is passed in as variables.
- **Use an engine feature that does not evaluate code.** Logic-less templates, or a sandbox that the vendor still supports, are appropriate for user-facing customisation. Prefer a purpose-built formatter (a fixed layout with named slots) over a general-purpose engine when the user only needs to rearrange fields.
- **Do not concatenate** user input into the template string and then compile the result. Pass a context object.
- **Lock the template name** to an allow-list of files inside a directory the application owns. Resolve the path and confirm it stays there.
- **Run the renderer with least privilege** and without access to cloud credentials, deployment secrets, or the internal network. Assume a template bug is code execution.
- **Disable features** the product does not need: arbitrary object traversal, imports, and helpers that shell out or read files. Document the configuration so a framework upgrade does not turn them back on.
- Treat "we will filter the dangerous tokens" as a temporary mitigation while the design change lands. Engines have more syntax than a filter will name, and the [injection prevention guidance](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html) is explicit that the structured interface, not the filter, is the control.

If the business requirement is truly "customers upload templates", isolate rendering on a separate service with no secrets and no network path to production data, and review the engine's current security documentation before you trust the sandbox. Revisit that decision on every engine upgrade.

## Detection

- Code review for compile-from-string and for any template body read from a database or from a request.
- Dependency review of the template engine, with an owner who reads its security advisories.
- A test that submits a marker with characters that would be special in the engine you use and asserts the marker comes back as data, not as an evaluated result. Keep that test specific to the engine in the repository, and do not expand it into a payload library.
- Process and file-integrity monitoring on the renderer host, for the case where the design control fails. A renderer that starts a shell or reads a credential file is an incident even if the template feature is "only email".

## References

- CWE-1336 — <https://cwe.mitre.org/data/definitions/1336.html>
- CWE-94 — <https://cwe.mitre.org/data/definitions/94.html>
- WSTG server-side template injection — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/18-Testing_for_Server-side_Template_Injection>
- OWASP Injection Prevention Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html>
- PortSwigger, server-side template injection — <https://portswigger.net/web-security/server-side-template-injection>

## Related in this repository

- [Vulnerability class index](README.md)
- [Web application checklist](../../checklists/web-application-testing.md)
- [API testing checklist](../../checklists/api-testing.md)
- [Finding template](../../templates/finding.md)
- [Where each class is documented](../../resources/vulnerability-classes.md)
- [Disclaimer](../../DISCLAIMER.md)

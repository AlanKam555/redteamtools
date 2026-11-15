# OS command injection

OS command injection is [CWE-78](https://cwe.mitre.org/data/definitions/78.html), a special case of [CWE-77](https://cwe.mitre.org/data/definitions/77.html). It falls under [OWASP Top 10 (2021) A03, Injection](https://owasp.org/Top10/2021/). The public test description is [WSTG command injection](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/12-Testing_for_Command_Injection), and the fix is the [OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html).

## What it is

Untrusted data is concatenated into a string that a shell or a command interpreter executes. The interpreter treats metacharacters as syntax, so the caller adds commands or arguments the application did not plan. The code then runs as the operating-system user the application runs as.

That user is the impact. A web user who can run as the application user can usually read the application's configuration and credentials, and can often write the paths that user can write. Calling a shell is how a small parsing bug becomes host compromise. The remediation is to stop calling a shell.

Argument injection is the related defect in which the application does not call a shell, but still places untrusted data into an argument that the target program interprets as a flag or a path. The fix is the same family: allow-list, separate arguments, no shell.

## Where it appears

- Features that wrap a command-line tool: image conversion, archive handling, diagnostic "ping" or "traceroute" pages, certificate generation, git operations, PDF conversion.
- A language helper that runs a string through a shell when a list of arguments was available.
- Build systems, admin consoles, and "custom script" features that pass a user field into a command template.
- File names and paths that later appear quoted, or not quoted, inside a script.

If the application calls a library instead of a command, this class does not apply. The library can still be dangerous (see [deserialization](deserialization.md) and [XXE](xxe.md)). Do not force a command-injection narrative onto a library bug.

## Responsible testing

1. Find the call site. In code, search for process helpers and shell flags. In a black-box test, the candidates are features whose job is obviously a system command, or parameters documented as "the host to ping" and similar.
2. Establish a baseline with a legal value. If the feature is "ping", the client should name a host you are allowed to probe, ideally one they operate and that logs the probe. One probe. You are confirming the feature, not mapping the network.
3. Prefer a code-level confirmation: show that the argument is concatenated into a shell string. That confirmation does not require a successful command, and it is the one to use on production.
4. If the rules allow a behavioural proof, use a canary the client prepared: a command or argument that writes or requests a marker in a place you were given, running as a test, with the process timeout kept short. Do not run a shell that reads credential files, spawns a reverse connection, or changes system configuration.
5. Time-based and out-of-band symptoms are documented in the public guides. They are easy to misread (the network was slow) and easy to overdo (you left a long delay in a worker). Use them only when you understand the baseline timing and the rules allow them, and use a single modest trial.

If you cannot see the code and you cannot get a safe canary, report the dangerous pattern as a suspected issue with the evidence you do have, and ask for a code review. Do not escalate to a public exploit string against production to settle the question.

Syntax for shells and for common tools is maintained in the [WSTG chapter](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/12-Testing_for_Command_Injection), the [Web Security Academy](https://portswigger.net/web-security/os-command-injection), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), and [HackTricks](https://hacktricks.wiki/). It is not copied here.

## Safe confirmation

- The feature and the parameter.
- The code path, if you have it, showing a shell invocation with untrusted data in the string.
- Or a canary effect the client agreed to, with the process user identified.
- An explicit note that you did not obtain an interactive shell, did not read secrets, and did not leave a process running.

An interactive shell is not a responsible confirmation. It is a new system to operate, and it is outside this method.

## Remediation

The [OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html) is short because the design fix is short:

- **Do not invoke a shell.** Use the process API that takes an argument array. The operating system then does not parse metacharacters.
- **Avoid the process entirely** when a library implements the operation. A library has its own risks, but it does not parse a shell command line.
- **Allow-list** when the user really does choose a mode or a host. Compare the whole value to a list you wrote. Quoting a string you then pass through a shell is a recurring source of mistakes. Do not make quoting the design.
- **Bind paths** to a directory you control. Resolve the path and confirm the result is still inside that directory before you use it. A path argument can escape a working directory even when no shell is involved.
- **Drop privileges.** The process user should not be able to read deployment secrets that belong to another service, and should not be able to write the web root. Containers and sandbox profiles help when the tool itself is untrusted (archive and image parsers).
- **Timeout and resource-limit** the child. A hung converter is an availability bug sitting next to the injection bug.

If a product requirement is "administrators can run a configured command", make the command part of server-side configuration, not part of the request, and audit every use.

## Detection

- Code search and review for shell helpers. The review rule is "argument array or it does not merge".
- Process-creation logs on the host or container. A web or worker process that starts a shell, or that starts a tool it never starts in normal operation, is an alert. This is also the detection a defender wants for the ATT&CK execution tactic, described at the concept level in [post-exploitation concepts](../07-post-exploitation-concepts.md).
- Alert on child processes of the application user that are interactive or short-lived command interpreters.
- An application log of the feature that includes the allow-listed target and the actor, not the raw command string if that string can contain secrets.

A deny-list of metacharacters in the application is not a detection strategy and not a fix. Shells have more syntax than the list will contain, and legitimate fields sometimes contain the same characters.

## References

- CWE-78 — <https://cwe.mitre.org/data/definitions/78.html>
- CWE-77 — <https://cwe.mitre.org/data/definitions/77.html>
- OWASP OS Command Injection Defense Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html>
- WSTG command injection — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/12-Testing_for_Command_Injection>
- PortSwigger, OS command injection — <https://portswigger.net/web-security/os-command-injection>

## Related in this repository

- [Vulnerability class index](README.md)
- [Web application checklist](../../checklists/web-application-testing.md)
- [API testing checklist](../../checklists/api-testing.md)
- [Finding template](../../templates/finding.md)
- [Where each class is documented](../../resources/vulnerability-classes.md)
- [Disclaimer](../../DISCLAIMER.md)

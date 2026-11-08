# Insecure deserialization

Insecure deserialization is [CWE-502](https://cwe.mitre.org/data/definitions/502.html) and [OWASP Top 10 (2021) A08, Software and Data Integrity Failures](https://owasp.org/Top10/2021/). The defensive reference is the [OWASP Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html). PortSwigger's overview is the [deserialization topic](https://portswigger.net/web-security/deserialization).

## What it is

The application takes a byte stream or a document that a caller can influence and rebuilds objects from it using a general-purpose deserializer. The format is allowed to say which classes to construct and which methods to call as a side effect of construction. The caller does not need to send you a program file. The program is the set of classes already on your classpath or in your process, and the document picks a chain of them.

Languages and libraries that have had this problem in their native formats include Java's object serialization, .NET's binary formatter and some of its relatives, PHP's native object unserialization, Python's pickle, and Ruby's marshal. The list of dangerous APIs changes. The rule does not: if the format can name a type and the caller supplies the bytes, treat it as code execution.

A signature or an encryption layer around the blob proves that someone who holds the key produced it. It does not make the format safe. If the key leaks, if a client-side component holds the key, or if the attacker is a user you gave a legitimate blob to, the deserializer still runs whatever types the format names. Authenticity is useful. It is not the control. The control is to stop using a general-purpose object deserializer on untrusted data.

JSON, XML, and other data formats become this bug when a library is configured to turn type hints inside the document into real objects. A plain JSON parser that produces maps and lists, which the application then copies onto a type it chose, is the safe pattern.

## Where it appears

- Session cookies, remember-me tokens, and cache entries that contain a native serialized object.
- Message queues and background jobs that accept a serialized body from a producer outside the trust boundary.
- File uploads and "export/import" features in a language's native format.
- A framework feature that binds a request onto an object graph and will instantiate whatever type the request names.
- A dependency that deserializes internally. The application looks as if it only accepts JSON, and a library underneath still accepts a gadget document. This is why the dependency's configuration belongs in the review.

## Responsible testing

1. Identify the format. Look at cookies, tokens, queue messages, and file headers, and look at the code for the APIs named above. A cookie that is a random session identifier is not this bug. A cookie that decodes to a structured object graph is a candidate.
2. Prefer a configuration and code finding: name the API, name the trust boundary, and state that the caller can supply the bytes. That is enough to write a high-severity design finding when the API is a known dangerous one and the data is untrusted.
3. Do not run a public gadget chain against a production process to "prove code execution". Gadget chains are exploits. They are maintained in the public catalogues for lab use, and they are not a confirmation method this repository endorses for a live system. A safe confirmation is one of: the code review, a unit test in a non-production environment that shows an unexpected type was instantiated and then stops, or a vendor advisory that matches the exact library and a reachable endpoint.
4. If the client wants a lab demonstration, do it on a copy of the service with test data, with no production credentials on the box, and throw the instance away. Do not point a generated payload at production from a research tool you have not read.

The catalogues are the [Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html) (for the defensive configuration of each platform), the [Web Security Academy](https://portswigger.net/web-security/deserialization), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), and [HackTricks](https://hacktricks.wiki/). Read them to understand the class and to configure the safe settings. Do not treat them as a checklist to fire at the engagement.

## Safe confirmation

- The API and the file or function that calls it.
- The source of the bytes (cookie, upload, queue, request body) and who can supply them.
- The privilege of the process that deserializes.
- The statement that you did not execute a gadget chain against the deployed system.
- If a lab demonstration was in scope, the identifier of the disposable environment and what was done with it afterwards.

An unexpected exception that names an internal class can support the "this parser instantiates types from the document" claim. Quote it carefully, and do not keep mutating the document to walk a chain.

## Remediation

The [Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html) has the platform-specific flags. The architecture is:

- **Replace native deserialization of untrusted data** with a data format that cannot name code. Parse JSON or a similar format into structures, then copy fields onto a type the application selected. Reject documents that contain type hints if your library supports them. The default in several libraries is the unsafe direction. Set the safe one explicitly.
- **Delete the dangerous API** from new code. In platforms where the vendor has deprecated it, turn the deprecation into a build failure. .NET's binary formatter and Python's pickle-on-the-wire are the usual examples to remove, not to wrap.
- **If you must accept a blob from a trusted producer**, authenticate the producer (mutual TLS or a signature with a key the producer alone holds), restrict the types to an allow-list the deserializer will enforce, and keep the producer inside the same trust boundary. Revisit this every time someone proposes to let a browser or a tenant hold the key.
- **Isolate** any parser you cannot replace. A separate process with no secrets and no network is the containment for a file format you do not control. Monitor it as if it will be compromised.
- **Patch and reduce the classpath.** Gadgets are classes. Fewer libraries means fewer chains, and it is still not a fix. The fix is the parser.
- **Do not build a filter** that looks for the byte signatures of known gadgets. The next chain will not match, and the filter becomes a payload list you now have to maintain.

Integrity checks (HMAC of a cookie) remain a good idea for tamper detection of data you serialized yourself, after you have moved that cookie to a safe format. They are a second control.

## Detection

- Static analysis and review for the dangerous APIs and for JSON libraries configured to honour type discriminators from the document.
- Dependency review against the vendor's deserialization advisories. [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/) is one public tool for the identification half.
- Runtime alerts when a process that should only parse data starts a child process or loads a class from an unexpected package. This is environment-specific. Agree it with the team that owns the host.
- Log parser failures that include type names, and alert on types that are not in the allow-list. Do this only after an allow-list exists, or the alert has nothing to compare against.

## References

- CWE-502 — <https://cwe.mitre.org/data/definitions/502.html>
- OWASP Deserialization Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html>
- OWASP Top 10 (2021) A08 — <https://owasp.org/Top10/2021/>
- PortSwigger, insecure deserialization — <https://portswigger.net/web-security/deserialization>
- OWASP Dependency-Check — <https://owasp.org/www-project-dependency-check/>

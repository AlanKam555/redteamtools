# XML external entities (XXE)

XXE is [CWE-611](https://cwe.mitre.org/data/definitions/611.html). It is an injection into an XML parser, and it is covered by [OWASP Top 10 (2021) A05, Security Misconfiguration](https://owasp.org/Top10/2021/), because the usual defect is a parser left in a dangerous default, and also by A03 when the document is untrusted input. The public test description is [WSTG XML injection](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/07-Testing_for_XML_Injection). The fix is the [OWASP XML External Entity Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html), which has per-language settings. Use that sheet for the settings. This note explains which setting and why.

## What it is

An XML parser that honours a document type definition can be asked, by the document, to resolve an external entity: a local file, an HTTP request, or another source the parser can reach. The document is untrusted. The parser runs as the application. If the parser inserts the result into the document the application then returns or stores, the caller can read files the application can read, or can make the server issue a request (an SSRF performed by the parser). Even when the result is not returned, a parser that tries to resolve an external resource can be used as a blind reachability oracle, and a parser that loads a huge expansion can exhaust memory. Those last two are reasons to disable the feature, not reasons to demonstrate them in production.

JSON, and an XML parser with DTDs and external entities disabled, do not have this channel. The appearance of XML in a modern API is often a legacy integration, a SAML or SOAP endpoint, a document upload, or an office file (which is a zip of XML). All of those are in scope for this class.

## Where it appears

- Any endpoint that accepts XML, including endpoints that accept "JSON or XML" based on a content type.
- SOAP services, SAML assertions if the application parses them itself, and RSS or other feed fetchers.
- Office documents, SVG, and other formats that are XML internally, if the application parses them on the server.
- Configuration uploads and "import this file" features.
- A client-side parser is a different risk (to the user who opens the document). The server-side parser is the one this class is about.

## Responsible testing

1. Find parsers. In code, look at the XML library's configuration. In a black-box test, look at content types and file uploads. The configuration review is the preferred confirmation: a parser that has external entities enabled is a finding even before a document is sent.
2. If the configuration is already "DTDs disabled, external entities disabled", record the positive observation and do not spend the window throwing documents at it.
3. If you need a behavioural proof, agree a canary with the client. The safe proofs are: the parser rejects a document that merely declares a DTD, or a test parser in a non-production environment resolves an entity that points at a marker file the client created for the test. Do not point an entity at a real credential file, a cloud metadata address, or an internal service you were not given.
4. Do not demonstrate billion-laughs style expansion. It is a denial of service. Note that expansion limits should be set, and move on.

Per-parser test documents are published in the [WSTG XML chapter](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/07-Testing_for_XML_Injection), the [Web Security Academy](https://portswigger.net/web-security/xxe), the [XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html) (as the behaviour you are disabling), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), and [HackTricks](https://hacktricks.wiki/). Keep them in the lab. A production confirmation is the configuration, plus at most one agreed canary.

## Safe confirmation

- The endpoint or file type, and the library and version.
- The configuration flags that enable or disable DTDs and external entities, quoted from the code or the runtime setting.
- If a canary was used, the marker and the fact that the document was a test document against a test file.
- A statement that you did not request files outside the canary and did not stress the parser.

A parser error that names an internal path can be a small information leak of its own. Quote the path only if the client is comfortable with it in the report, and do not keep probing for more paths.

## Remediation

Follow the language section of the [XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html). The design rules are stable even when the flag names are not:

- **Disable DTDs and external entities** on every parser that handles untrusted documents. Do this in a factory the application uses everywhere, not in one endpoint. A second parser created for a new feature with default settings is the usual regression.
- **Prefer a format that is not XML** for new interfaces, so the class is not available. Where XML is required by a protocol (SOAP, SAML), use a maintained library that already disables external resolution, and pin its security configuration.
- **Disable external stylesheets, schema locations, and XInclude** unless the feature requires them, and if it requires them, fetch only from an allow-list.
- **Set expansion and size limits** so a malicious document fails rather than consuming the process.
- **Run the parser as a low-privilege user** that cannot read deployment secrets. Defence in depth for the day a new parser is constructed wrong.
- **Validate after parsing** against a schema you wrote, and reject documents that do not match. Schema validation is not a substitute for disabling entities. The entity is resolved before your schema sees the document, in many libraries.

Patch the library. XXE advisories are often "the safe flag was not the default" or "a new API ignored the flag". An owner who reads the parser's release notes is part of the control.

## Detection

- A repository check that the XML factory is the safe one, and that nobody instantiates the parser directly. This can be a lint rule.
- Application logs of parse failures that mention DTDs or entities, alerted during periods that are not a scheduled test.
- For office and SVG uploads, the same configuration review on the converter's parser, not only on the API parser.
- Outbound requests from the application host that coincide with an upload are the SSRF-shaped detection. See [SSRF](ssrf.md).

## References

- CWE-611 — <https://cwe.mitre.org/data/definitions/611.html>
- OWASP XML External Entity Prevention Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html>
- WSTG XML injection — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/07-Testing_for_XML_Injection>
- PortSwigger, XXE — <https://portswigger.net/web-security/xxe>

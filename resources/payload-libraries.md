# Payload and wordlist libraries

> Authorised use only. [Disclaimer](../DISCLAIMER.md) · [Security policy](../SECURITY.md) · [Repository index](../README.md) · [Licence](../LICENSE) · [Contributing](../CONTRIBUTING.md)

This page names the public projects that already maintain test strings and wordlists. This repository does not copy those files. The utilities under [tools/](../tools/README.md) do not load them, crawl, or send them.

Open a library only for a lab you control or for a target named in written rules of engagement. Follow that project's licence and terms. A link is a citation. It is not permission to send the contents at a host you have not been allowed to test. When a proof is in scope, use the smallest published example that matches the class, then stop. For content discovery, start with the short list that matches the technology. Every wordlist entry is a request the application has to answer.

## Test-string catalogues

| Library | What it is | Useful for |
| --- | --- | --- |
| [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) | A community catalogue of web test strings, organised by vulnerability class. | Finding the upstream example for a class this repository describes but does not reproduce. |
| [FuzzDB](https://github.com/fuzzdb-project/fuzzdb) | Dictionaries of fault-injection patterns and discovery names for black-box testing. | Choosing a labelled pattern set when you are testing how a parser or a path handles unexpected input. |
| [Big List of Naughty Strings](https://github.com/minimaxir/big-list-of-naughty-strings) | Strings that often break parsers, encodings, and user-interface handling. | Robustness checks on input handling. These are not exploit strings for a vulnerability class. |

## Wordlists

| Library | What it is | Useful for |
| --- | --- | --- |
| [SecLists](https://github.com/danielmiessler/SecLists) | A large collection of assessment lists, including paths, parameters, and filenames. It also holds credential and similar lists that this reference does not use. | Content and parameter discovery with a small list that matches the stack. A credential list is an authentication attack and needs its own written rule. |
| [Assetnote Wordlists](https://wordlists.assetnote.io/) ([repository](https://github.com/assetnote/wordlists)) | Technology-specific wordlists built from real application routes and files. | Discovery when the framework or product is known and a generic list would mostly miss. |
| [fuzz.txt](https://github.com/Bo0oM/fuzz.txt) | A short list of filenames that are often left exposed by mistake. | A first pass for leftover backups, dumps, and configuration names. |
| [OneListForAll](https://github.com/six2dez/OneListForAll) | One large combined web-content wordlist. | A fallback when no technology-specific list fits. A shorter matching list is still the better default. |

## Method, labs, and prevention

These projects publish the test method, a hosted lab, or the fix. Read them for the class. Do not treat a page as a list to replay.

| Library | What it is | Useful for |
| --- | --- | --- |
| [OWASP Web Security Testing Guide](https://wstg.owasp.org/) | The OWASP method for web testing, with a page per test. | The test description to follow, and the public example when the local note stops at the class. |
| [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) | Short prevention and configuration guidance for each control. | The fix, and the behaviour a safe test should observe, such as encoding or a refused frame. |
| [PortSwigger Web Security Academy](https://portswigger.net/web-security) | Explanations and hosted labs, organised by class. The topic index is [all topics](https://portswigger.net/web-security/all-topics). | Learning the smallest demonstration of a class on infrastructure the Academy runs, rather than on a client's production system. |
| [HackTricks](https://hacktricks.wiki/) ([repository](https://github.com/HackTricks-wiki/hacktricks)) | Technique notes for web, infrastructure, and cloud, including environment-specific detail. | Reading a trick the local class note deliberately does not copy, inside a lab or a written scope. |

## What to do with a link

- Cite the project from the finding or the lab note. Do not paste its files into this repository, a report, or a ticket.
- Keep the local method in the [class notes](../methodology/vulnerabilities/README.md). An upstream catalogue is the source of strings, not a second methodology.
- If a project moves, update this page to the successor on the same project. Do not replace it with an unverified mirror.
- A new library belongs on this page. It does not belong as a vendored directory in the tree. [CONTRIBUTING.md](../CONTRIBUTING.md) says the same thing.

## Related in this repository

- [Resource index](README.md)
- [Where each class is documented](vulnerability-classes.md)
- [Web application testing](../methodology/05-web-application-testing.md)
- [ffuf](../cheatsheets/ffuf.md)
- [Disclaimer](../DISCLAIMER.md)

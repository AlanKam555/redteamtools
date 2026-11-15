# Tools

Public tools that support the method in this repository. The usage boundaries are in [cheatsheets/](../cheatsheets/README.md). Install them from the project itself, pin a version in the engagement notes, and read that version's manual before you rely on a flag you copied from a cheatsheet.

## Discovery and content

- Nmap — <https://nmap.org/>, manual <https://nmap.org/book/man.html>. Host and service discovery.
- ffuf — <https://github.com/ffuf/ffuf>, wiki <https://github.com/ffuf/ffuf/wiki>. HTTP content discovery at a rate you chose.
- SecLists — <https://github.com/danielmiessler/SecLists>. Wordlists. A smaller list that matches the technology is the professional choice. The other upstream catalogues are on [payload and wordlist libraries](payload-libraries.md), which is a list of links, not a copy of the files.

## Template and proxy testing

- Nuclei — <https://github.com/projectdiscovery/nuclei>, documentation <https://docs.projectdiscovery.io/tools/nuclei/overview>. Exclude intrusive and denial-of-service tags unless the rules name them, and confirm every match by hand.
- Burp Suite documentation — <https://portswigger.net/burp/documentation>.
- OWASP ZAP — <https://www.zaproxy.org/> and the project page <https://owasp.org/www-project-zap/>.

## Dependencies and configuration

- OWASP Dependency-Check — <https://owasp.org/www-project-dependency-check/>. Identifies known-vulnerable components. Pair it with the [Vulnerable Dependency Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html).
- The header and TLS checkers in [tools/](../tools/README.md). Read-only, one target, authorisation flag required.
- SSL Labs rating guide — <https://www.ssllabs.com/projects/rating-guide/>. Grading criteria. Sending a hostname to a public grader shares that hostname with a third party, so it belongs in the rules first.
- Mozilla Observatory — <https://observatory.mozilla.org/>. Same constraint: it is a third-party fetch of a public name.

## What this list leaves out

Exploit frameworks, payload generators, and credential-attack tools are widely published and widely misused. They are not linked here. An engagement that has written permission for a specific technique can use the vendor's own documentation for that technique, under those rules, without this repository mirroring it.

## Related in this repository

- [Resource index](README.md)
- [Payload and wordlist libraries](payload-libraries.md)
- [Cheatsheets](../cheatsheets/README.md)
- [Defensive utilities](../tools/README.md)
- [Disclaimer](../DISCLAIMER.md)

# ffuf

[ffuf](https://github.com/ffuf/ffuf) is an HTTP fuzzer. In an assessment it is used for content discovery: which paths, virtual hosts, or parameter names exist on a host you are allowed to test. The project README and [wiki](https://github.com/ffuf/ffuf/wiki) are the manual. The method around it is [enumeration](../methodology/03-enumeration.md).

A wordlist is a hypothesis about names. [SecLists](https://github.com/danielmiessler/SecLists) is a public collection. Pick a small list that matches the technology, not the largest list in the repository. Every entry is a request the application has to answer.

## Before you run it

- Scope the tool to the agreed host. Do not follow redirects onto a different registrable domain.
- Cap the rate. Ten requests a second is a starting point for a healthy staging site and is already too much for some production logins. Authentication endpoints deserve a lower cap or a manual test.
- Filter the responses that mean "nothing was there", or you will save a million identical 404s.
- Stop if latency rises or if the error rate climbs. That is the abort condition from the rules of engagement, not a reason to retry.

## A capped path discovery

```bash
ffuf -u https://TARGET/FUZZ \
  -w WORDLIST \
  -mc 200,204,301,302,307,401,403 \
  -rate 10 -timeout 10 -maxtime 600 \
  -o evidence/ffuf-paths.json
```

`TARGET` and `WORDLIST` are placeholders. `-mc` keeps the status codes worth reading. `-maxtime` stops the run even if the list is long. Recursion (`-recursion`) multiplies the traffic. Leave it off unless the rules allow it and you have already reviewed the first level.

A 401 or a 403 is a lead, not an invitation to guess passwords. Record the path and test it with the accounts you were given.

## What to write down

- The list you used, the match codes, and the rate.
- Paths that differ from the baseline response, with the title or the length that made them different.
- Paths you then confirmed by opening them once, by hand, in the proxy.
- Paths you did not test because they landed on a third party.

## What not to add

- A password or key wordlist pointed at a login form. That is an authentication attack and needs its own rule.
- Recursion across the whole site because the first results were interesting.
- A run you cannot stop. If you do not know the abort step, do not start.

## Official documentation

- ffuf — <https://github.com/ffuf/ffuf>
- ffuf wiki — <https://github.com/ffuf/ffuf/wiki>
- SecLists — <https://github.com/danielmiessler/SecLists>
- Other wordlists, and the rule that this repository does not copy them — [payload and wordlist libraries](../resources/payload-libraries.md)

## Related in this repository

- [Cheatsheet index](README.md)
- [Enumeration](../methodology/03-enumeration.md)
- [Nmap](nmap.md)
- [Web application testing](../methodology/05-web-application-testing.md)
- [Payload and wordlist libraries](../resources/payload-libraries.md)
- [Disclaimer](../DISCLAIMER.md)

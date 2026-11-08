# Enumeration

Enumeration takes the asset table from reconnaissance and describes what each in-scope asset actually exposes: names, ports, protocols, routes, parameters, and roles. It is still not exploitation. The output is a map a tester can cover and a defender can compare with their own inventory.

Stay inside the rules of engagement. A port that responds on an in-scope address is fair game to record. A port that responds on the address next door is a lead, not a scan.

## Network and service enumeration

For hosts that are in scope, the usual questions are:

- Which addresses answer, and which were dead or filtered during the window?
- Which TCP and, if agreed, UDP ports accept a connection?
- What protocol speaks first, and does the banner or handshake name a product and version?
- Is the service the one the client thinks is there?

The [Nmap cheatsheet](../cheatsheets/nmap.md) records a conservative way to ask those questions and points at the [Nmap reference](https://nmap.org/book/man.html). Use a timing and a retry policy that the production rules can survive. Version detection sends real protocol traffic. That is appropriate against an authorised host and inappropriate as a wide sweep of a cloud provider's shared ranges.

Record negatives. "Port 443 was the only open port on this host at 14:10 UTC" is evidence. A blank row is not.

When a service banner names a version, treat it as a hypothesis for [vulnerability analysis](04-vulnerability-analysis.md). Banners lie, backports exist, and a version string is not a vulnerable configuration by itself.

Skip exploit-oriented scan scripts unless the rules name them. A discovery script and a script that attempts a compromise are different tools even when they share a binary. This methodology uses enumeration to build the map, and uses vulnerability analysis to decide what is real.

## Application enumeration

For each in-scope web application or API:

- Fetch the entry points the client named and the ones linked from them: home, login, robots-style site maps the application itself publishes, OpenAPI or GraphQL descriptions, and health routes that are intentionally public.
- List routes, parameters, content types, and whether each route is anonymous or authenticated.
- Note technologies from headers, cookies, and public script paths. Confirm with the client when the stack is unclear. The [header checker](../tools/security_header_checker.py) is enough for the response-header half of this and will not crawl.
- Build a role matrix: for each role the client gave you, which objects you can see and which actions the interface offers. Empty cells are the ones [access-control testing](vulnerabilities/idor-access-control.md) cares about.
- Identify where the application fetches a URL, renders a template, parses XML, builds a query, shells out, or deserialises a blob. Those are the sinks the class notes describe. You are listing them, not attacking them yet.

Content discovery (a wordlist of common paths) is enumeration, and it is also easy to overdo. Agree the wordlist source, the rate, and the response codes worth keeping. [ffuf](../cheatsheets/ffuf.md) is one public tool for this. Stop if error rates climb or if the application starts returning the same body for every path. A backup file or an exposed administrative path is a finding to confirm carefully, not a door to walk through at production scale.

Authentication endpoints deserve a lower rate than static files. Lockouts are an availability incident you caused.

## Accounts and test data

Ask the client for:

- At least two accounts in the same role, so horizontal access control can be compared.
- One account in a higher role and one in a lower role, so vertical access control can be compared.
- Canary records those accounts own, clearly named, so a screenshot does not contain a real customer.
- A way to reset the accounts if a test locks them.

If the client can only offer a shared administrator account, say so in the report. Several classes cannot be tested properly without a second principal, and the gap belongs in the limitations section rather than in a guessed finding.

## Defensive counterpart

Enumeration is also what an inventory programme should already have done.

- Maintain a list of names, addresses, ports, and owners, and alert when certificate transparency or DNS adds a name the inventory does not know.
- Remove version banners you do not need. They are not a control, but they make the defender's and the tester's inventory match reality more slowly when they are wrong, and they help targeting when they are right.
- Publish intentional API descriptions for the APIs you mean to support, and keep shadow routes out of production. The [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) calls out improper inventory as its own risk (API9).
- Rate-limit and monitor login and content-discovery patterns. A burst of requests for unlikely paths is an enumeration signal even when every response is a 404.

## What good notes look like

```text
app.example.com  A 203.0.113.10  confirmed by client 2026-11-02
  443/tcp  https  banner: reverse proxy, version not disclosed
  routes:  GET /  GET /login  GET /api/v1/items  POST /api/v1/items
  roles:   anonymous, user-a, user-b, admin (all synthetic)
  sinks:   item title rendered in HTML; item URL fetched server-side (client-confirmed)
```

That note is enough to plan the next two phases. A folder of unlabelled scanner XML is not.

## References

- Nmap reference guide — <https://nmap.org/book/man.html>
- OWASP Web Security Testing Guide — <https://wstg.owasp.org/>
- OWASP API Security Top 10 (2023) — <https://owasp.org/API-Security/editions/2023/en/0x11-t10/>
- NIST SP 800-115 — <https://csrc.nist.gov/pubs/sp/800/115/final>

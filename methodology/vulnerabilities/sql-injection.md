# SQL injection

SQL injection is [CWE-89](https://cwe.mitre.org/data/definitions/89.html). It is the canonical example of [OWASP Top 10 (2021) A03, Injection](https://owasp.org/Top10/2021/). The public test description is [WSTG SQL injection](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection), and the fix is the [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html).

## What it is

The application builds a database statement by mixing untrusted data with the statement's structure. The database then parses that mixture as a query. The caller gets to change which rows are selected, which columns come back, or which statement runs, using a channel that was supposed to be a value.

The impact tracks the database account. A low-privilege account that can only read one table is a different incident from an account that can write, read other databases, or reach the operating system through a database feature. Both are findings. The second is why least privilege is part of the fix and not an optional extra.

Error-based, boolean, and time-based symptoms are three ways the same defect becomes visible. They are evidence categories, not three different bugs. A stacked query or a database function that reaches the network or the filesystem is the same defect with a larger blast radius. This note does not catalogue those functions.

## Where it appears

- String concatenation, format strings, or template literals that include request data, headers, cookies, or a sort field.
- Object-relational mappers used through their "raw query" escape hatch.
- Stored procedures that concatenate internally. Moving the concatenation into the database does not parameterise it.
- Identifiers that cannot be bound as parameters in the engine you use: table names, column names, and `ORDER BY` targets. These need an allow-list, not a parameter.
- Search builders that assemble `WHERE` clauses from a client-supplied structure.

Second-order variants store a value safely and later concatenate it. The sink is the later statement. A test that only looks at the request that stored the value will miss it. Trace where the value is used, with the client's help or by reading the query log in a test environment.

## Responsible testing

1. Identify statements. In a white-box or grey-box test this is a code search for query construction. In a black-box test it is a hypothesis from parameters that look like filters, identifiers, and sort keys.
2. Send a baseline with a known-good value and record the response shape, the status, and, if you have it, the query the application actually issued.
3. Send a benign variant that is still a legal value but is distinct (a different canary identifier you are allowed to ask for). Confirm the application returns the matching canary and not someone else's data. That is an authorization test as well. Keep it.
4. If, and only if, you are authorised to test the query parser: compare the baseline with a single input that is syntactically meaningful to a query and observe whether the application changes class of behaviour (a database error where the baseline was clean, a result set that changes in a way a plain value cannot explain, or a delay that matches the database rather than the network). Use one request at a time. Do not walk a public payload list through production.
5. Prefer a test environment where query logging is on, so the confirmation is "the statement structure changed in the log" rather than "we extracted a table".

Stop when the log or the behaviour shows that data was parsed as structure. You do not need the contents of a system table, a file read, or another network connection from the database to write the finding. Those demonstrations raise the impact statement and the chance of an incident, and they require an explicit line in the rules of engagement plus a database account the client is willing to see abused.

Do not use a vulnerability scanner's SQL module on a production database unless that module's behaviour has been read and the rules allow it. Many modules are noisy and some are destructive.

The concrete syntax for each engine is documented in the [WSTG SQL injection chapter](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection), the [Web Security Academy](https://portswigger.net/web-security/sql-injection), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), and [HackTricks](https://hacktricks.wiki/). Use those in a lab or under the rules. They are not reproduced here.

## Safe confirmation

- The parameter, the route, and the account.
- Baseline behaviour versus the variant, in words.
- Where you have it, a query-log excerpt showing the value outside the parameter channel, with literals redacted.
- The database role's privileges, so the impact sentence is about that role and not about a theoretical superuser.
- Confirmation that you did not dump data, alter schemas, or ask the database to contact other hosts.

If the only evidence is a verbose database error, say that. An error that leaks the query text is already a finding (information exposure) and a strong indicator of the injection class. It is not, by itself, proof that a useful statement can be formed. Do not keep retrying until the error goes away or the service falls over.

## Remediation

**Parameterise every value.** Use the driver's prepared statements or the ORM's bound parameters so the engine receives the statement structure and the data on separate channels. This is the fix the [SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) centres on, and it is the fix that survives encoding tricks.

Practical rules that teams actually need written down:

- Ban string concatenation into SQL in review. Provide one helper that accepts a statement and a parameter list, and make the raw helper require a named reviewer.
- Bind variables even when you "know" the value is an integer. Cast in the application for your own logic, and still bind it.
- Stored procedures are safe only when they parameterise too. Review the procedure body.
- For identifiers the engine cannot bind, compare the input to an allow-list of known column or table names that you wrote, and interpolate only the matched literal. Reject everything else.
- For dynamic `IN` lists, generate the right number of placeholders and bind each value. Do not concatenate the list.
- For search frameworks, use the library's structured query objects. If a caller can pass a query string, they own your database.

**Reduce what a failure can see.**

- Give the application a database role that can touch only the schemas it needs, with no permission to read other tenants' schemas, no administrative role, and no feature that runs operating-system commands or fetches network resources.
- Separate migration credentials from runtime credentials.
- Return a generic error to the caller. Log the database error server-side, with the request identifier, without echoing the statement back to the browser.

A web application firewall rule is a temporary containment. It will not understand every encoding, and it does not fix the query.

## Detection

- Code review and static analysis aimed at query construction. The useful alert is "non-literal SQL", not "a keyword appeared in a comment".
- A test that fails the build if a query helper is called with a format string, where the language makes that detectable.
- Database auditing of statement structure from the application role: an alert when the shape of a statement changes for a given code path, or when the application role issues a statement type it never issues in production (schema changes, file or network functions).
- Application errors that mention the database engine, counted and alerted. A spike during a test window is expected and should have been on the calendar. A spike outside it is an incident.
- Do not rely on a deny-list in the application ("reject quotes") as detection or as prevention. It breaks legitimate names and it does not match the way query parsers work.

## References

- CWE-89 — <https://cwe.mitre.org/data/definitions/89.html>
- OWASP SQL Injection Prevention Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html>
- OWASP Injection Prevention Cheat Sheet — <https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html>
- WSTG SQL injection — <https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection>
- PortSwigger, SQL injection — <https://portswigger.net/web-security/sql-injection>

## Related in this repository

- [Vulnerability class index](README.md)
- [Web application checklist](../../checklists/web-application-testing.md)
- [API testing checklist](../../checklists/api-testing.md)
- [Finding template](../../templates/finding.md)
- [Where each class is documented](../../resources/vulnerability-classes.md)
- [Disclaimer](../../DISCLAIMER.md)

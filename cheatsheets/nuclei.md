# Nuclei

[Nuclei](https://github.com/projectdiscovery/nuclei) runs templates against a host. Templates range from "read this header" to checks the template author has marked as intrusive or as denial of service. The official overview is the [Nuclei documentation](https://docs.projectdiscovery.io/tools/nuclei/overview). How a hit becomes a finding is [vulnerability analysis](../methodology/04-vulnerability-analysis.md).

Use a template set you trust, on hosts that are in scope, at a rate the rules allow. A template you have not read is not evidence.

## Before you run it

- Update templates on a schedule you control, and pin the set you used in the evidence notes so a retest can match it.
- Exclude tags the rules do not allow. The common exclusions for a standard web assessment are the intrusive, fuzzing, and denial-of-service tags. Confirm the tag names in the template set you installed, because metadata changes.
- Prefer severity filters over "run everything".
- Treat every match as unconfirmed. Read the template, send one manual request that you understand, and keep or discard the row.

## A restrained run

```bash
nuclei -u https://TARGET \
  -severity low,medium,high,critical \
  -rate-limit 10 -timeout 5 -retries 1 \
  -exclude-tags dos,fuzz,intrusive \
  -o evidence/nuclei.txt
```

`TARGET` is an in-scope base URL. `-rate-limit` is requests per second. If the installed client uses a different flag for the same idea, the manual wins over this page.

Do not add `-as` or a workflow you have not reviewed just because an example used it. Do not point Nuclei at a file of every hostname reconnaissance produced. Put it through the scope list first.

## What to write down

- The template version and the command.
- Matches you confirmed, with the template identifier and the manual request.
- Matches you rejected, with the reason (banner mismatch, feature not enabled, template expected a different product).
- Any template that caused an error spike. That is an incident note to the emergency contact, even if the template was supposed to be safe.

## What not to add

- Community templates whose description says they exploit, brute-force, or exhaust a resource, unless the rules name that template.
- A custom template you wrote during the test and did not share with the client before running it.
- A screenshot of a match as the whole finding. The finding still needs impact, the affected asset, and the remediation from the vendor advisory or the class note.

## Official documentation

- Nuclei — <https://github.com/projectdiscovery/nuclei>
- Documentation — <https://docs.projectdiscovery.io/tools/nuclei/overview>

## Related in this repository

- [Cheatsheet index](README.md)
- [Vulnerability analysis](../methodology/04-vulnerability-analysis.md)
- [Class notes](../methodology/vulnerabilities/README.md)
- [Disclaimer](../DISCLAIMER.md)

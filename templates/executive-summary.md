# Executive summary: [Engagement title]

| Field | Value |
| --- | --- |
| Client | [Client legal name] |
| Window | [YYYY-MM-DD] to [YYYY-MM-DD] |
| Environment | [Production, staging, or the tenant name] |
| Classification | [Label] |
| Full report | [Where the technical report lives] |

Write this for someone who will fund or accept risk and will not read the request traces. One page is the right length. If a sentence only makes sense to the person who sent the request, move it to the finding.

## Why this assessment happened

[One paragraph. The business reason, the environment, and the authorisation. Name the rules-of-engagement reference.]

## What matters

Describe two to four themes, not a list of every bug. For each theme:

- The business effect (customer records, payments, ability to detect).
- Whether it is a class that will recur, or a single defect.
- The decision you are asking for: fund now, schedule, or accept with a named owner.

Do not invent counts. If you mention a number, it has to match the findings summary in the full report.

## What held

[A short paragraph on the controls that worked. Executives use this to see the programme, and the next assessment uses it to avoid retesting a solved problem as if it were unknown.]

## Limits

[What you did not test, in one paragraph: missing accounts, production held out of scope, a feature that was down, a third party you were told to leave alone. A clean summary that hides a limit is a false summary.]

## Asked decisions

1. [Decision, owner, and what "done" means.]
2. [Decision, owner, and what "done" means.]

A retest of the high-severity themes, in the same environment, is usually the last item.

## Related in this repository

- [Report template](report.md)
- [Reporting method](../methodology/08-reporting.md)
- [Reporting checklist](../checklists/reporting.md)
- [Disclaimer](../DISCLAIMER.md)

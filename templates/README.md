# Templates

Copy these into the engagement store and fill them in there. Do not fill them with client data inside this repository.

| Template | Purpose |
| --- | --- |
| [Rules of engagement](rules-of-engagement.md) | The decisions the test is allowed to make. The blank copy contains placeholders on purpose, so `tools/scope_roe_validator.py` reports it as not ready. |
| [Finding](finding.md) | One weakness, in the shape the report expects. |
| [Report](report.md) | The full assessment write-up. `tools/report_skeleton.py` can generate the same outline with the names filled in. |
| [Executive summary](executive-summary.md) | The short version for a reader who will not open the findings. |

The examples under [examples/](examples/README.md) are fictional and exist so you can see a rules file the validator accepts. They are not a real authorisation to test anything, including `example.com`.

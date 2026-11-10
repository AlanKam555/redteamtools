# Examples

> Authorised use only. These files are not permission to test anything. [Disclaimer](../../DISCLAIMER.md) · [Security policy](../../SECURITY.md) · [Repository index](../../README.md) · [Licence](../../LICENSE)

These files are fictional. They show the shape of a rules-of-engagement record that `tools/scope_roe_validator.py` accepts. They do not authorise anyone to test `example.com` or any other system.

| File | Validator |
| --- | --- |
| [completed-rules-of-engagement.md](completed-rules-of-engagement.md) | Markdown sections. Expect exit code 0. |
| [completed-rules-of-engagement.json](completed-rules-of-engagement.json) | The same decisions as JSON. Expect exit code 0. |

The blank [rules of engagement](../rules-of-engagement.md) contains placeholders and is expected to exit 1 until it is copied and completed in the engagement store.

```bash
python3 tools/scope_roe_validator.py --file templates/examples/completed-rules-of-engagement.md
python3 tools/scope_roe_validator.py --file templates/examples/completed-rules-of-engagement.json
python3 tools/scope_roe_validator.py --file templates/rules-of-engagement.md
```

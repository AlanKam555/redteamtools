# Contributing

Thank you for improving this reference. The maintainer is Alan. The repository is [AlanKam555/redteamtools](https://github.com/AlanKam555/redteamtools).

> Authorised use only. Read [DISCLAIMER.md](DISCLAIMER.md) and [SECURITY.md](SECURITY.md) before you add a note or change a utility. The [MIT licence](LICENSE) is Copyright (c) 2026 Alan. By contributing, you agree that your contribution is provided under that licence.

## What belongs here

- Methodology, in the shape already used under [methodology/](methodology/README.md): what the phase or class is, how an authorised tester recognises it at a high level, the smallest safe confirmation, remediation, and detection.
- Checklists, cheatsheets, and templates that point at those notes.
- Defensive utilities that review configuration or local documents. A network utility must require an explicit target and `--authorized`, must not crawl, and must not send exploit payloads.
- Tests for those utilities, including the case where `--authorized` is missing.
- Corrections to citations, broken links, and wording that overstates what a check proves.

## What does not belong here

- Exploit code, malware, credential attacks, or a generator for them.
- A copied catalogue of raw payloads. Link [OWASP](https://wstg.owasp.org/), [PortSwigger](https://portswigger.net/web-security), [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings), or [HackTricks](https://hacktricks.wiki/) instead.
- Client data, packet captures, session cookies, or a filled-in report from a real engagement.
- A default target, a hidden host list, or a flag that skips `--authorized`.

If a sentence would be enough for someone to compromise a system they have no permission to touch, it belongs in a primary source's authorised testing guide, or it does not belong here.

## Notes and links

- Use the headings the neighbouring file already uses. Vulnerability notes keep **What it is**, **Where it appears**, **Responsible testing**, **Safe confirmation**, **Remediation**, **Detection**, and **References**.
- Link the related checklist, template, and cheatsheet when one exists. Relative links only.
- British spelling in prose (`authorised`, `authorisation`) matches the rest of the repository. The CLI flag stays `--authorized`, because that is the flag the tools already require.
- Cite a page you have opened. Name the CWE, WSTG test, or cheat sheet. Do not invent advisory identifiers.

## Utilities

The programs in [tools/](tools/README.md) are Python 3.10+ and standard-library only. [pyproject.toml](pyproject.toml) keeps `dependencies` empty on purpose. Do not add a runtime package to make a check shorter.

Before you open a pull request:

```bash
python3 -m pip install "ruff>=0.8"
ruff check tools
python3 -m unittest discover -s tools/tests -v
```

Exit codes stay stable: `0` finished with no fail-level result, `1` finished and found a fail-level gap (or a rules file is not ready), `2` the arguments were refused or the check could not run. Network code runs only after both the target and `--authorized` have been accepted.

## Tests

Tests live in `tools/tests/` and are discovered with `unittest`. New behaviour needs a test. A change to a guardrail needs a test that fails if the guardrail is removed, including a test that no socket is opened when `--authorized` is absent. Use `127.0.0.1` only. Do not contact an external host from a test.

## Reporting a defect

A broken check, a dangerous default, or a script that does more than it claims is a security report. Follow [SECURITY.md](SECURITY.md). Do not send exploit payloads or data from a real engagement.

## Changelog

Add a line under the unreleased or current version in [CHANGELOG.md](CHANGELOG.md) when behaviour or the documented method changes. A typo does not need an entry.

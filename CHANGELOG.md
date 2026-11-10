# Changelog

All notable changes to this reference are recorded here. The licence is the MIT licence in [LICENSE](LICENSE). Copyright (c) 2026 Alan.

## 1.1.0 — 2026-11-10

### Documentation

- Expanded the top-level README with a table of contents and direct links across methodology notes, cheatsheets, checklists, templates, and the utilities.
- Added [resources/payload-libraries.md](resources/payload-libraries.md), a directory of upstream payload catalogues and wordlists. The files themselves are not vendored.
- Renamed the web and API checklists so their filenames match the methodology notes that already linked to them.
- Added [CONTRIBUTING.md](CONTRIBUTING.md) and this changelog.
- Made [DISCLAIMER.md](DISCLAIMER.md), [SECURITY.md](SECURITY.md), and the MIT licence easier to reach from the index and from each section README.

### Utilities

- Documented stable exit codes (`0`, `1`, `2`) in help text. Missing required arguments now print an `error:` line as well as the help.
- Tightened input checks: URL ports, bracketed IPv6 hosts, non-finite timeouts, control characters in report paths, and rules-file paths.
- Header review now treats a wildcard `frame-ancestors` source as "not a framing control" even when the spacing varies, and it caps how many header names and characters it will score.
- A Markdown link in a rules file is no longer mistaken for a bracketed placeholder.
- Runtime dependencies remain empty. [pyproject.toml](pyproject.toml) records that, and that Python 3.10+ is required.

### Tests and CI

- Expanded the unittest suite for the `--authorized` guard, refused targets, redirect limits, and the shipped rules examples.
- Added a GitHub Actions workflow that runs Ruff and the unit tests with `contents: read` only.

## 1.0.0 — 2026-11-09

- Initial authorised-use methodology reference, cheatsheets, checklists, templates, and the four standard-library utilities.

"""Write a local Markdown report skeleton. No network access."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections.abc import Sequence
from pathlib import Path

from lib.banner import emit_banner, fail

_SLUG = re.compile(r"[^a-z0-9]+")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def clean_field(value: str, *, label: str, limit: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    text = value.strip()
    if not text:
        raise ValueError(f"{label} is empty")
    if len(text) > limit:
        raise ValueError(f"{label} exceeds {limit} characters")
    if _CONTROL.search(text):
        raise ValueError(f"{label} contains control characters")
    return text


def parse_date(value: str, *, label: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be YYYY-MM-DD") from exc


def slugify(text: str) -> str:
    slug = _SLUG.sub("-", text.lower()).strip("-")
    return slug[:48] or "engagement"


def resolve_output(path: Path, *, force: bool) -> Path:
    cwd = Path.cwd().resolve()
    candidate = path if path.is_absolute() else cwd / path
    resolved = candidate.resolve()
    if resolved != cwd and cwd not in resolved.parents:
        raise ValueError("output path must stay inside the current working directory")
    if resolved.exists() and not force:
        raise ValueError("output file already exists; pass --force to overwrite")
    if resolved.exists() and resolved.is_dir():
        raise ValueError("output path is a directory")
    return resolved


def render(
    *,
    client: str,
    engagement: str,
    start: dt.date,
    end: dt.date,
    author: str,
    classification: str,
) -> str:
    if end < start:
        raise ValueError("end date is before the start date")
    return f"""# Security assessment report: {engagement}

| Field | Value |
| --- | --- |
| Client | {client} |
| Engagement | {engagement} |
| Assessment window | {start.isoformat()} to {end.isoformat()} |
| Author | {author} |
| Classification | {classification} |
| Status | Draft |

> Authorised-use reminder. This skeleton is for an engagement that already has written permission and a rules of engagement. Remove client data before the file is stored anywhere this repository is published. Do not paste live exploit strings into the report; describe the weakness class, the evidence, and the fix.

## 1. Executive summary

Write for a reader who will not open the technical appendix. In a few paragraphs, state:

- Why the assessment was done and which environment it covered.
- The risk themes, in business language (exposure of customer records, ability to change payments, gaps in detection).
- What is going well, so the reader can see the programme rather than only the defects.
- The decisions you want: which themes to fund now, which to schedule, which to accept.

Leave severity counts until the findings are real. A table of invented numbers is worse than a short paragraph.

## 2. Scope

- In-scope assets actually tested:
- Out-of-scope assets observed and left alone:
- Accounts and roles provided:
- Environments (production, staging, tenant):
- Known limits (time, rate, features that were down):

## 3. Methodology

Name the public method you followed, typically the OWASP Web Security Testing Guide for web and API work and NIST SP 800-115 for the overall assessment process. State whether testing was unauthenticated, authenticated, or both, and whether it was black, grey, or white box. Record tools used for evidence (proxy, scanner, the defensive checkers in this repository) and the build or configuration you were asked to look at.

## 4. Risk rating

Use the qualitative scale published with CVSS by FIRST (Critical, High, Medium, Low, Informational) and say which CVSS version produced the vector. Adjust the engagement rating when business impact differs from the base score, and write down why. A missing header on a marketing site and a missing authorization check on a medical record are not the same finding because a calculator said they were close.

## 5. Findings summary

| ID | Title | Severity | Asset | Status |
| --- | --- | --- | --- | --- |
| F-01 |  |  |  | Open |

## 6. Detailed findings

Copy `templates/finding.md` once per finding. Each entry needs a description of the class, the impact, sanitised evidence, a concrete remediation, and a primary reference (CWE and the relevant OWASP cheat sheet or WSTG test).

## 7. Positive observations

Record controls that stood up to testing: consistent authorization on a sample of object identifiers, parameterised queries in the reviewed services, MFA on administrative roles, useful audit logs. These observations tell the next tester where not to spend the whole window.

## 8. Remediation roadmap

Group fixes by theme (authorization, injection handling, TLS and headers, logging) and mark which ones remove a whole class rather than a single bug. Suggest a retest of the high and critical items after the fixes are deployed to the same environment.

## 9. Data handling

State where evidence is stored, who may read it, and when it will be deleted. Screenshots and proxy history belong in the engagement store named in the rules of engagement, not in this file if the file will be emailed widely.

## 10. References

- OWASP Web Security Testing Guide — https://wstg.owasp.org/
- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- OWASP Application Security Verification Standard — https://owasp.org/www-project-application-security-verification-standard/
- NIST SP 800-115 — https://csrc.nist.gov/pubs/sp/800/115/final
- FIRST CVSS — https://www.first.org/cvss/
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="report_skeleton",
        description="Write a Markdown security-report skeleton in the current directory. Makes no network connections.",
        epilog="Authorised use only. The generated file is a draft for an engagement you are allowed to report on.",
    )
    parser.add_argument("--client", required=False, help="Client or organisation name")
    parser.add_argument("--engagement", required=False, help="Engagement title")
    parser.add_argument("--start", required=False, help="Window start date, YYYY-MM-DD")
    parser.add_argument("--end", required=False, help="Window end date, YYYY-MM-DD")
    parser.add_argument("--author", required=False, help="Report author")
    parser.add_argument(
        "--classification",
        default="Confidential",
        help="Document classification label (default Confidential)",
    )
    parser.add_argument("--output", help="Output path inside the current directory")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    missing = [
        name
        for name in ("client", "engagement", "start", "end", "author")
        if getattr(args, name) in (None, "")
    ]
    if missing:
        parser.print_help(sys.stderr)
        print("error: missing " + ", ".join(f"--{name}" for name in missing), file=sys.stderr)
        return 2
    emit_banner()
    try:
        client = clean_field(args.client, label="client", limit=200)
        engagement = clean_field(args.engagement, label="engagement", limit=200)
        author = clean_field(args.author, label="author", limit=120)
        classification = clean_field(args.classification, label="classification", limit=60)
        start = parse_date(args.start, label="start")
        end = parse_date(args.end, label="end")
        body = render(
            client=client,
            engagement=engagement,
            start=start,
            end=end,
            author=author,
            classification=classification,
        )
        output = Path(args.output) if args.output else Path(f"report-{slugify(engagement)}-{start.isoformat()}.md")
        destination = resolve_output(output, force=args.force)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(body, encoding="utf-8")
    except (ValueError, OSError) as exc:
        fail(str(exc))
    print(f"Wrote {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

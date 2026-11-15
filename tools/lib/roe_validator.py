"""Check that a rules-of-engagement file still contains the decisions a test needs.

The validator reads a local Markdown or JSON file. It does not contact a target.
A passing result means the document has the required sections and no leftover
placeholders. It does not mean a lawyer has reviewed the engagement.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path

from lib.banner import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit_banner, fail

MAX_BYTES = 1_000_000

REQUIRED_SECTIONS = (
    "authorization",
    "in-scope assets",
    "out of scope",
    "allowed methods",
    "prohibited activities",
    "schedule",
    "emergency contacts",
    "data handling",
    "acknowledgement",
)

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
# Bracketed prompts such as [Client legal name] are placeholders.
# A Markdown link [label](url) is a reference, not a prompt, and is left alone.
_PLACEHOLDER = re.compile(
    r"\b(TBD|TODO|FIXME|CHANGE_ME|lorem ipsum)\b"
    r"|\[(?![^\]]+\]\()[A-Za-z][^\]\n]{0,80}\]",
    re.IGNORECASE,
)


def _normalise(title: str) -> str:
    text = title.strip().lower()
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    aliases = {
        "in scope assets": "in-scope assets",
        "inscope assets": "in-scope assets",
        "out of scope assets": "out of scope",
        "rules of engagement acknowledgement": "acknowledgement",
        "authorization statement": "authorization",
        "authorisation": "authorization",
        "authorisation statement": "authorization",
    }
    return aliases.get(text, text)


def parse_markdown(text: str) -> dict[str, str]:
    matches = list(_HEADING.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        level = len(match.group(1))
        if level != 2:
            continue
        start = match.end()
        end = len(text)
        for later in matches[index + 1 :]:
            if len(later.group(1)) <= level:
                end = later.start()
                break
        sections[_normalise(match.group(2))] = text[start:end].strip()
    return sections


def _placeholders(text: str) -> list[str]:
    return [match.group(0) for match in _PLACEHOLDER.finditer(text)]


def validate_markdown(text: str) -> list[str]:
    """Return human-readable gaps in a Markdown rules file. An empty list passes."""
    issues: list[str] = []
    sections = parse_markdown(text)
    for name in REQUIRED_SECTIONS:
        body = sections.get(name, "")
        if not body:
            issues.append(f"missing or empty section: {name}")
            continue
        if not re.sub(r"[#>*_\-\s]", "", body):
            issues.append(f"section has no prose: {name}")
    authorisation = sections.get("authorization", "")
    if authorisation and not re.search(r"authoris|authoriz", authorisation, re.IGNORECASE):
        issues.append("authorization section does not state that testing is authorised")
    found = _placeholders(text)
    if found:
        sample = ", ".join(found[:8])
        issues.append(f"placeholders still present: {sample}")
    out_of_scope = sections.get("out of scope", "")
    meaningful = re.sub(r"[^a-z0-9/]+", " ", out_of_scope.lower()).strip()
    if meaningful in {"none", "n/a", "na", "n a"}:
        issues.append("out of scope is 'none'; name the neighbouring systems that must not be touched")
    return issues


def _parse_day(value: object, label: str, issues: list[str]) -> dt.date | None:
    if not isinstance(value, str):
        issues.append(f"{label} must be a YYYY-MM-DD string")
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        issues.append(f"{label} must be a YYYY-MM-DD string")
        return None


def validate_json(data: object) -> list[str]:
    """Return human-readable gaps in a JSON rules object. An empty list passes."""
    issues: list[str] = []
    if not isinstance(data, dict):
        return ["top-level JSON value must be an object"]
    required = (
        "engagement",
        "authorization",
        "in_scope",
        "out_of_scope",
        "allowed_methods",
        "prohibited",
        "window",
        "emergency_contacts",
        "data_handling",
        "acknowledgement",
    )
    for key in required:
        if key not in data:
            issues.append(f"missing field: {key}")
    if issues:
        return issues

    def require_text(value: object, label: str, limit: int = 4000) -> str:
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{label} must be a non-empty string")
            return ""
        if len(value) > limit:
            issues.append(f"{label} exceeds {limit} characters")
        if _PLACEHOLDER.search(value):
            issues.append(f"{label} still contains a placeholder")
        return value

    require_text(data["engagement"], "engagement", 200)
    auth = data["authorization"]
    if not isinstance(auth, dict):
        issues.append("authorization must be an object")
    else:
        statement = require_text(auth.get("statement", ""), "authorization.statement")
        if statement and not re.search(r"authoris|authoriz", statement, re.IGNORECASE):
            issues.append("authorization.statement does not state that testing is authorised")
        require_text(auth.get("approved_by", ""), "authorization.approved_by", 200)
        _parse_day(auth.get("date"), "authorization.date", issues)

    def require_list(value: object, label: str) -> list[object]:
        if not isinstance(value, list) or not value:
            issues.append(f"{label} must be a non-empty list")
            return []
        return value

    for item in require_list(data["in_scope"], "in_scope"):
        require_text(item, "in_scope entry", 500)
    for item in require_list(data["out_of_scope"], "out_of_scope"):
        require_text(item, "out_of_scope entry", 500)
    for item in require_list(data["allowed_methods"], "allowed_methods"):
        require_text(item, "allowed_methods entry", 300)
    for item in require_list(data["prohibited"], "prohibited"):
        require_text(item, "prohibited entry", 300)

    window = data["window"]
    if not isinstance(window, dict):
        issues.append("window must be an object with start and end")
    else:
        start = _parse_day(window.get("start"), "window.start", issues)
        end = _parse_day(window.get("end"), "window.end", issues)
        if start and end and end < start:
            issues.append("window.end is before window.start")

    contacts = require_list(data["emergency_contacts"], "emergency_contacts")
    for contact in contacts:
        if not isinstance(contact, dict):
            issues.append("emergency contact must be an object with name and method")
            continue
        require_text(contact.get("name", ""), "emergency contact name", 200)
        require_text(contact.get("method", ""), "emergency contact method", 300)

    require_text(data["data_handling"], "data_handling")
    acknowledgement = require_text(data["acknowledgement"], "acknowledgement")
    if acknowledgement and not re.search(r"authoris|authoriz", acknowledgement, re.IGNORECASE):
        issues.append("acknowledgement does not refer to the authorisation")
    return issues


def load_and_validate(path: Path) -> list[str]:
    """Read a local Markdown or JSON rules file and return its gaps.

    Raises:
        ValueError: the path is not an allowed file, is too large, or is not valid JSON.
    """
    if any(ord(char) < 32 for char in str(path)):
        raise ValueError("path contains control characters")
    if not path.is_file():
        raise ValueError("path is not a file")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"file exceeds {MAX_BYTES} bytes")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON: {exc.msg}") from exc
        return validate_json(data)
    if path.suffix.lower() in {".md", ".markdown", ".txt"}:
        return validate_markdown(text)
    raise ValueError("file must end in .md, .markdown, .txt, or .json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scope_roe_validator",
        description=(
            "Check a local rules-of-engagement file for required sections, empty decisions, "
            "and leftover placeholders. Does not contact any target."
        ),
        epilog=(
            "Authorised use only. A pass means the document is complete enough to read, "
            "not that the test is lawful. Exit status: 0 when the required decisions are "
            "present, 1 when the file is not ready, 2 when it could not be read."
        ),
    )
    parser.add_argument("--file", help="Path to a Markdown or JSON rules-of-engagement file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Check one local rules file. Does not contact a target."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.file or not str(args.file).strip():
        parser.print_help(sys.stderr)
        print("error: missing --file", file=sys.stderr)
        return EXIT_USAGE
    emit_banner()
    path = Path(args.file)
    try:
        issues = load_and_validate(path)
    except (OSError, UnicodeError, ValueError) as exc:
        fail(str(exc))
    if issues:
        print(f"{path} is not ready:")
        for issue in issues:
            print(f"- {issue}")
        return EXIT_FINDINGS
    print(f"{path} has the required sections and no placeholder markers.")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())

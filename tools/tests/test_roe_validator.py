"""Tests for the rules-of-engagement validator."""

from __future__ import annotations

import json
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import support  # noqa: F401
from lib.roe_validator import main, validate_json, validate_markdown

COMPLETE = textwrap.dedent(
    """\
    # Rules of engagement

    ## Authorization

    Example Corp authorises Alan to test the named assets during the schedule below.

    ## In-scope assets

    - https://app.example.com

    ## Out of scope

    - https://payments.example.com and every third-party service not listed above.

    ## Allowed methods

    - Manual web and API testing at a modest rate.

    ## Prohibited activities

    - Denial of service, data destruction, and persistence.

    ## Schedule

    2026-11-01 to 2026-11-08, 09:00-17:00 UTC.

    ## Emergency contacts

    - Alex Example, security-oncall@example.com, +1-555-0100.

    ## Data handling

    Evidence stays in the engagement vault and is deleted 90 days after the retest.

    ## Acknowledgement

    Both parties acknowledge this authorisation is limited to the assets and window above.
    """
)


class MarkdownTests(unittest.TestCase):
    def test_complete_document_passes(self) -> None:
        self.assertEqual(validate_markdown(COMPLETE), [])

    def test_british_spelling_and_missing_section(self) -> None:
        text = COMPLETE.replace("## Authorization", "## Authorisation").replace(
            "## Out of scope\n\n- https://payments.example.com and every third-party service not listed above.\n",
            "",
        )
        issues = validate_markdown(text)
        self.assertTrue(any("out of scope" in issue for issue in issues))
        self.assertFalse(any(issue.startswith("missing or empty section: authorization") for issue in issues))

    def test_placeholders_and_empty_out_of_scope(self) -> None:
        text = COMPLETE.replace("https://payments.example.com and every third-party service not listed above.", "none")
        text = text.replace("Example Corp", "[Client legal name]")
        issues = validate_markdown(text)
        self.assertTrue(any("placeholder" in issue for issue in issues))
        self.assertTrue(any("out of scope" in issue for issue in issues))


class JsonTests(unittest.TestCase):
    def sample(self) -> dict:
        return {
            "engagement": "External web assessment",
            "authorization": {
                "statement": "Example Corp authorises this test.",
                "approved_by": "Alex Example",
                "date": "2026-10-15",
            },
            "in_scope": ["https://app.example.com"],
            "out_of_scope": ["https://payments.example.com"],
            "allowed_methods": ["Manual web testing at a modest rate"],
            "prohibited": ["Denial of service"],
            "window": {"start": "2026-11-01", "end": "2026-11-08"},
            "emergency_contacts": [{"name": "Alex Example", "method": "security-oncall@example.com"}],
            "data_handling": "Delete evidence 90 days after the retest.",
            "acknowledgement": "The tester acknowledges the authorisation limits.",
        }

    def test_sample_passes(self) -> None:
        self.assertEqual(validate_json(self.sample()), [])

    def test_inverted_window_fails(self) -> None:
        data = self.sample()
        data["window"] = {"start": "2026-12-02", "end": "2026-12-01"}
        self.assertTrue(any("window.end" in issue for issue in validate_json(data)))


class CliTests(unittest.TestCase):
    def test_cli_on_files(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "roe.md"
            path.write_text(COMPLETE, encoding="utf-8")
            self.assertEqual(main(["--file", str(path)]), 0)
            broken = Path(tmp) / "broken.json"
            broken.write_text(json.dumps({"engagement": "x"}), encoding="utf-8")
            self.assertEqual(main(["--file", str(broken)]), 1)

    def test_help(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            main(["--help"])
        self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()

"""The shipped rules examples and the blank template keep the documented exit codes."""

from __future__ import annotations

import unittest
from pathlib import Path

import support  # noqa: F401
from lib.roe_validator import main
from support import exit_code

ROOT = Path(__file__).resolve().parents[2]


class RepositoryExampleTests(unittest.TestCase):
    def test_completed_examples_pass(self) -> None:
        markdown = ROOT / "templates" / "examples" / "completed-rules-of-engagement.md"
        payload = ROOT / "templates" / "examples" / "completed-rules-of-engagement.json"
        self.assertEqual(exit_code(main, ["--file", str(markdown)]), 0)
        self.assertEqual(exit_code(main, ["--file", str(payload)]), 0)

    def test_blank_template_is_not_ready(self) -> None:
        blank = ROOT / "templates" / "rules-of-engagement.md"
        self.assertEqual(exit_code(main, ["--file", str(blank)]), 1)


if __name__ == "__main__":
    unittest.main()

"""Tests for the local report skeleton generator."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import support  # noqa: F401
from lib.report_skeleton import main, resolve_output, slugify
from support import exit_code


class ReportTests(unittest.TestCase):
    def test_slug(self) -> None:
        self.assertEqual(slugify("External Web Assessment!"), "external-web-assessment")

    def test_refuses_to_escape_the_working_directory(self) -> None:
        with TemporaryDirectory() as tmp:
            outside = Path(tmp) / "elsewhere.md"
            original = Path.cwd()
            try:
                import os

                os.chdir(tmp)
                nested = Path(tmp) / "work"
                nested.mkdir()
                os.chdir(nested)
                with self.assertRaises(ValueError):
                    resolve_output(Path("../elsewhere.md"), force=False)
                with self.assertRaises(ValueError):
                    resolve_output(outside, force=False)
            finally:
                os.chdir(original)

    def test_writes_a_draft(self) -> None:
        with TemporaryDirectory() as tmp:
            original = Path.cwd()
            try:
                import os

                os.chdir(tmp)
                code = exit_code(
                    main,
                    [
                        "--client",
                        "Example Corp",
                        "--engagement",
                        "External web assessment",
                        "--start",
                        "2026-11-01",
                        "--end",
                        "2026-11-08",
                        "--author",
                        "Alan",
                        "--output",
                        "draft.md",
                    ],
                )
                self.assertEqual(code, 0)
                text = Path("draft.md").read_text(encoding="utf-8")
                self.assertIn("Example Corp", text)
                self.assertIn("Authorised-use reminder", text)
                self.assertEqual(
                    exit_code(
                        main,
                        [
                            "--client",
                            "Example Corp",
                            "--engagement",
                            "External web assessment",
                            "--start",
                            "2026-11-01",
                            "--end",
                            "2026-11-08",
                            "--author",
                            "Alan",
                            "--output",
                            "draft.md",
                        ],
                    ),
                    2,
                )
            finally:
                os.chdir(original)

    def test_rejects_inverted_dates_and_control_characters(self) -> None:
        with TemporaryDirectory() as tmp:
            original = Path.cwd()
            try:
                import os

                os.chdir(tmp)
                self.assertEqual(
                    exit_code(
                        main,
                        [
                            "--client",
                            "Example",
                            "--engagement",
                            "Test",
                            "--start",
                            "2026-12-02",
                            "--end",
                            "2026-12-01",
                            "--author",
                            "Alan",
                        ],
                    ),
                    2,
                )
                self.assertEqual(
                    exit_code(
                        main,
                        [
                            "--client",
                            "Bad\nName",
                            "--engagement",
                            "Test",
                            "--start",
                            "2026-12-01",
                            "--end",
                            "2026-12-02",
                            "--author",
                            "Alan",
                        ],
                    ),
                    2,
                )
            finally:
                os.chdir(original)

    def test_help(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            main(["--help"])
        self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()

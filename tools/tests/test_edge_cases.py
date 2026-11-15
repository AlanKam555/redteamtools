"""Edge cases and the --authorized guard. Connections, when any, stay on 127.0.0.1."""

from __future__ import annotations

import json
import os
import socket
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from test_roe_validator import COMPLETE

import support  # noqa: F401
from lib.http_headers import evaluate_headers, validate_url
from lib.http_headers import main as header_main
from lib.report_skeleton import main as report_main
from lib.report_skeleton import resolve_output
from lib.roe_validator import main as roe_main
from lib.roe_validator import validate_markdown
from lib.tls_config import cipher_assessment, protocol_assessment, validate_host
from lib.tls_config import main as tls_main
from support import exit_code


class HeaderGuardTests(unittest.TestCase):
    def test_missing_flag_does_not_fetch(self) -> None:
        err = StringIO()
        with (
            patch("lib.http_headers.fetch") as fetch,
            patch("lib.http_headers.urllib.request.build_opener") as opener,
            redirect_stderr(err),
        ):
            code = exit_code(header_main, ["--url", "https://app.example.com/"])
        self.assertEqual(code, 2)
        fetch.assert_not_called()
        opener.assert_not_called()
        text = err.getvalue()
        self.assertIn("refusing to run without --authorized", text)
        self.assertNotIn("Authorisation flag: accepted", text)

    def test_bad_url_with_flag_does_not_fetch(self) -> None:
        with (
            patch("lib.http_headers.fetch") as fetch,
            patch("lib.http_headers.urllib.request.build_opener") as opener,
        ):
            for raw in (
                "file:///etc/passwd",
                "https://user:secret@example.com/",
                "https://example.com:99999/",
                "https://example.com:0/",
                "",
            ):
                code = exit_code(header_main, ["--url", raw, "--authorized"])
                self.assertEqual(code, 2, raw)
        fetch.assert_not_called()
        opener.assert_not_called()

    def test_bad_timeout_does_not_fetch(self) -> None:
        with patch("lib.http_headers.fetch") as fetch:
            for raw in ("0", "31", "nan", "inf"):
                code = exit_code(
                    header_main,
                    ["--url", "https://app.example.com/", "--authorized", "--timeout", raw],
                )
                self.assertEqual(code, 2, raw)
        fetch.assert_not_called()

    def test_missing_url_exits_before_the_banner_claim(self) -> None:
        err = StringIO()
        with redirect_stderr(err):
            code = exit_code(header_main, [])
        self.assertEqual(code, 2)
        self.assertIn("error: missing --url", err.getvalue())
        self.assertNotIn("Authorisation flag: accepted", err.getvalue())


class HeaderEvaluationEdgeTests(unittest.TestCase):
    def test_short_hsts_and_spaced_wildcard_ancestors(self) -> None:
        headers = {
            "Strict-Transport-Security": "max-age=100",
            "Content-Security-Policy": "default-src 'self'; frame-ancestors   *",
        }
        checks = {item.name: item for item in evaluate_headers(headers, scheme="https")}
        self.assertEqual(checks["strict-transport-security"].status, "warn")
        self.assertEqual(checks["clickjacking-control"].status, "fail")

    def test_frame_ancestors_none_is_a_control(self) -> None:
        headers = {"Content-Security-Policy": "frame-ancestors 'none'"}
        checks = {item.name: item for item in evaluate_headers(headers, scheme="https")}
        self.assertEqual(checks["clickjacking-control"].status, "pass")

    def test_samesite_none_without_secure_fails(self) -> None:
        headers = {"Set-Cookie": "session=value; SameSite=None"}
        checks = evaluate_headers(headers, scheme="https")
        cookie = next(item for item in checks if item.name.startswith("cookie:"))
        self.assertEqual(cookie.status, "fail")
        self.assertNotIn("value", cookie.detail)

    def test_complete_cookie_passes_without_echoing_the_value(self) -> None:
        headers = {"Set-Cookie": "session=value; Secure; HttpOnly; SameSite=Lax"}
        checks = evaluate_headers(headers, scheme="https")
        cookie = next(item for item in checks if item.name == "cookie:session")
        self.assertEqual(cookie.status, "pass")
        self.assertNotIn("value", cookie.detail)

    def test_rejects_non_string_and_overlong_urls(self) -> None:
        with self.assertRaises(ValueError):
            validate_url(None)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            validate_url("https://example.com/" + ("a" * 3000))

    def test_accepts_query_and_ipv6_host(self) -> None:
        self.assertEqual(
            validate_url("https://[::1]/health?x=1"),
            "https://[::1]/health?x=1",
        )


class RedirectGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                self.server.request_count += 1  # type: ignore[attr-defined]
                self.send_response(302)
                host, port = self.server.server_address[:2]
                if self.path.startswith("/creds"):
                    self.send_header("Location", f"http://user:secret@{host}:{port}/landed")
                else:
                    self.send_header("Location", "/again")
                self.end_headers()

            def log_message(self, fmt: str, *args: object) -> None:
                return

        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.server.request_count = 0  # type: ignore[attr-defined]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address[:2]
        cls.base = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def test_stops_after_three_redirects(self) -> None:
        self.server.request_count = 0  # type: ignore[attr-defined]
        out = StringIO()
        with redirect_stdout(out):
            code = exit_code(
                header_main,
                ["--url", self.base + "/loop", "--authorized", "--format", "json", "--timeout", "5"],
            )
        payload = json.loads(out.getvalue())
        self.assertEqual(code, 1)
        self.assertEqual(payload["status"], 302)
        self.assertEqual(len(payload["hops"]), 4)
        self.assertLessEqual(self.server.request_count, 4)  # type: ignore[attr-defined]

    def test_credential_redirect_is_refused(self) -> None:
        self.server.request_count = 0  # type: ignore[attr-defined]
        code = exit_code(
            header_main,
            ["--url", self.base + "/creds", "--authorized", "--timeout", "5"],
        )
        self.assertEqual(code, 2)
        self.assertEqual(self.server.request_count, 1)  # type: ignore[attr-defined]


class TlsGuardTests(unittest.TestCase):
    def test_missing_flag_does_not_connect(self) -> None:
        err = StringIO()
        with (
            patch("lib.tls_config.assess") as assess,
            patch("lib.tls_config.socket.create_connection") as connect,
            patch("lib.tls_config.ssl.get_server_certificate") as certificate,
            redirect_stderr(err),
        ):
            code = exit_code(tls_main, ["--host", "127.0.0.1", "--port", "443"])
        self.assertEqual(code, 2)
        assess.assert_not_called()
        connect.assert_not_called()
        certificate.assert_not_called()
        self.assertIn("refusing to run without --authorized", err.getvalue())
        self.assertNotIn("Authorisation flag: accepted", err.getvalue())

    def test_bad_host_and_timeout_do_not_connect(self) -> None:
        with (
            patch("lib.tls_config.assess") as assess,
            patch("lib.tls_config.socket.create_connection") as connect,
        ):
            self.assertEqual(exit_code(tls_main, ["--host", "not a host", "--authorized"]), 2)
            self.assertEqual(
                exit_code(tls_main, ["--host", "127.0.0.1", "--authorized", "--timeout", "0"]),
                2,
            )
            self.assertEqual(exit_code(tls_main, ["--host", "[not-an-ip]", "--authorized"]), 2)
        assess.assert_not_called()
        connect.assert_not_called()

    def test_missing_host_names_the_error(self) -> None:
        err = StringIO()
        with redirect_stderr(err):
            code = exit_code(tls_main, [])
        self.assertEqual(code, 2)
        self.assertIn("error: missing --host", err.getvalue())

    def test_bracketed_ipv6_is_normalised(self) -> None:
        self.assertEqual(validate_host("[::1]"), "::1")
        self.assertEqual(validate_host("[2001:db8::1]"), "2001:db8::1")

    def test_more_protocol_and_cipher_edges(self) -> None:
        self.assertEqual(protocol_assessment("TLSv1.1").status, "fail")
        self.assertEqual(protocol_assessment("SSLv3").status, "warn")
        self.assertEqual(cipher_assessment(None).status, "warn")
        self.assertEqual(cipher_assessment("NULL-SHA").status, "fail")

    def test_closed_local_port_is_a_finding(self) -> None:
        probe = socket.socket()
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()
        out = StringIO()
        with redirect_stdout(out):
            code = exit_code(
                tls_main,
                [
                    "--host",
                    "127.0.0.1",
                    "--port",
                    str(port),
                    "--authorized",
                    "--timeout",
                    "2",
                    "--format",
                    "json",
                ],
            )
        self.assertEqual(code, 1)
        payload = json.loads(out.getvalue())
        self.assertEqual(payload["port"], port)
        self.assertTrue(any(item["status"] == "fail" for item in payload["checks"]))


class ReportEdgeTests(unittest.TestCase):
    def test_missing_fields_and_blank_classification(self) -> None:
        self.assertEqual(exit_code(report_main, []), 2)
        with TemporaryDirectory() as tmp:
            original = Path.cwd()
            try:
                os.chdir(tmp)
                code = exit_code(
                    report_main,
                    [
                        "--client",
                        "Example",
                        "--engagement",
                        "Edge",
                        "--start",
                        "2026-11-01",
                        "--end",
                        "2026-11-02",
                        "--author",
                        "Alan",
                        "--classification",
                        "   ",
                    ],
                )
                self.assertEqual(code, 2)
                self.assertEqual(list(Path(tmp).glob("*.md")), [])
            finally:
                os.chdir(original)

    def test_force_overwrite_and_default_name(self) -> None:
        with TemporaryDirectory() as tmp:
            original = Path.cwd()
            try:
                os.chdir(tmp)
                args = [
                    "--client",
                    "Example",
                    "--engagement",
                    "Edge Case",
                    "--start",
                    "2026-11-01",
                    "--end",
                    "2026-11-02",
                    "--author",
                    "Alan",
                ]
                self.assertEqual(exit_code(report_main, args), 0)
                drafted = Path("report-edge-case-2026-11-01.md")
                self.assertTrue(drafted.is_file())
                self.assertEqual(exit_code(report_main, [*args, "--output", "draft.md", "--force"]), 0)
                self.assertEqual(exit_code(report_main, [*args, "--output", "draft.md", "--force"]), 0)
            finally:
                os.chdir(original)

    def test_symlink_and_control_character_paths_are_refused(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside"
            outside.mkdir()
            work = root / "work"
            work.mkdir()
            original = Path.cwd()
            try:
                os.chdir(work)
                link = work / "escape"
                link.symlink_to(outside, target_is_directory=True)
                with self.assertRaises(ValueError):
                    resolve_output(Path("escape") / "out.md", force=True)
                with self.assertRaises(ValueError):
                    resolve_output(Path("bad\nname.md"), force=True)
            finally:
                os.chdir(original)


class RoeEdgeTests(unittest.TestCase):
    def test_markdown_link_is_not_a_placeholder(self) -> None:
        text = COMPLETE.replace(
            "Both parties acknowledge this authorisation is limited to the assets and window above.",
            "Both parties acknowledge this authorisation. See the [rules](https://example.com/roe).",
        )
        self.assertEqual(validate_markdown(text), [])

    def test_missing_and_unreadable_files(self) -> None:
        err = StringIO()
        with redirect_stderr(err):
            self.assertEqual(exit_code(roe_main, []), 2)
        self.assertIn("error: missing --file", err.getvalue())
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(exit_code(roe_main, ["--file", str(root / "missing.md")]), 2)
            self.assertEqual(exit_code(roe_main, ["--file", str(root)]), 2)
            wrong = root / "notes.html"
            wrong.write_text(COMPLETE, encoding="utf-8")
            self.assertEqual(exit_code(roe_main, ["--file", str(wrong)]), 2)
            binary = root / "broken.md"
            binary.write_bytes(b"\xff\xfe not utf-8")
            self.assertEqual(exit_code(roe_main, ["--file", str(binary)]), 2)
            huge = root / "huge.md"
            huge.write_bytes(b"a" * 1_000_001)
            self.assertEqual(exit_code(roe_main, ["--file", str(huge)]), 2)

    def test_json_shape_errors(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "roe.json"
            path.write_text("[]", encoding="utf-8")
            self.assertEqual(exit_code(roe_main, ["--file", str(path)]), 1)
            path.write_text("{", encoding="utf-8")
            self.assertEqual(exit_code(roe_main, ["--file", str(path)]), 2)


if __name__ == "__main__":
    unittest.main()

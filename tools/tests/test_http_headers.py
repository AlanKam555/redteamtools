"""Tests for the security-header review. Network use is limited to 127.0.0.1."""

from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import support  # noqa: F401
from lib.http_headers import evaluate_headers, main, validate_url
from support import exit_code


class ValidateUrlTests(unittest.TestCase):
    def test_accepts_https(self) -> None:
        self.assertEqual(validate_url(" https://app.example.com/health "), "https://app.example.com/health")

    def test_rejects_other_schemes_and_credentials(self) -> None:
        for raw in ("file:///etc/passwd", "ftp://example.com", "https://user:secret@example.com/a", "", "https://"):
            with self.assertRaises(ValueError):
                validate_url(raw)

    def test_rejects_control_characters(self) -> None:
        with self.assertRaises(ValueError):
            validate_url("https://example.com/\npath")


class EvaluateTests(unittest.TestCase):
    def test_strong_https_headers_pass_core_checks(self) -> None:
        headers = {
            "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'; script-src 'self'",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=()",
        }
        checks = {item.name: item for item in evaluate_headers(headers, scheme="https")}
        for name in (
            "transport",
            "strict-transport-security",
            "content-security-policy",
            "x-content-type-options",
            "clickjacking-control",
            "referrer-policy",
        ):
            self.assertEqual(checks[name].status, "pass", checks[name].detail)

    def test_missing_core_headers_fail(self) -> None:
        checks = {item.name: item for item in evaluate_headers({}, scheme="https")}
        self.assertEqual(checks["strict-transport-security"].status, "fail")
        self.assertEqual(checks["x-content-type-options"].status, "fail")
        self.assertEqual(checks["clickjacking-control"].status, "fail")
        self.assertEqual(checks["content-security-policy"].status, "warn")

    def test_cleartext_is_a_failure(self) -> None:
        checks = {item.name: item for item in evaluate_headers({}, scheme="http")}
        self.assertEqual(checks["transport"].status, "fail")

    def test_cookie_value_is_not_repeated(self) -> None:
        secret = "session=super-secret-value; HttpOnly"
        checks = evaluate_headers({"Set-Cookie": secret}, scheme="https")
        cookie = next(item for item in checks if item.name.startswith("cookie:"))
        self.assertNotIn("super-secret-value", cookie.detail)
        self.assertEqual(cookie.status, "warn")

    def test_reflected_credentialed_cors_fails(self) -> None:
        headers = {
            "Access-Control-Allow-Origin": "https://authorised-header-check.invalid",
            "Access-Control-Allow-Credentials": "true",
        }
        checks = {item.name: item for item in evaluate_headers(headers, scheme="https")}
        self.assertEqual(checks["cors"].status, "fail")

    def test_weak_csp_is_a_warning(self) -> None:
        headers = {"Content-Security-Policy": "script-src 'unsafe-inline' 'unsafe-eval' *"}
        checks = {item.name: item for item in evaluate_headers(headers, scheme="https")}
        self.assertEqual(checks["content-security-policy"].status, "warn")
        self.assertIn("unsafe-inline", checks["content-security-policy"].detail)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/go":
            self.send_response(302)
            self.send_header("Location", "/landed")
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, fmt: str, *args) -> None:
        return


class FetchCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def test_refuses_without_authorisation(self) -> None:
        self.assertEqual(exit_code(main, ["--url", self.base + "/landed"]), 2)

    def test_fetches_local_url_and_emits_json(self) -> None:
        from io import StringIO
        from contextlib import redirect_stdout

        buffer = StringIO()
        with redirect_stdout(buffer):
            code = exit_code(
                main, ["--url", self.base + "/go", "--authorized", "--format", "json", "--timeout", "5"]
            )
        payload = json.loads(buffer.getvalue())
        self.assertEqual(code, 1)  # cleartext http is a failure
        self.assertEqual(payload["status"], 200)
        self.assertTrue(payload["final_url"].endswith("/landed"))
        names = {item["name"] for item in payload["checks"]}
        self.assertIn("x-content-type-options", names)

    def test_help_does_not_require_a_target(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            main(["--help"])
        self.assertEqual(caught.exception.code, 0)


if __name__ == "__main__":
    unittest.main()

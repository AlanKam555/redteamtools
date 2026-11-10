"""Tests for TLS classification helpers. Connections stay on 127.0.0.1."""

from __future__ import annotations

import contextlib
import datetime as dt
import socket
import ssl
import subprocess
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import support  # noqa: F401
from lib.tls_config import (
    assess,
    certificate_window,
    cipher_assessment,
    extract_validity,
    main,
    parse_cert_time,
    pem_to_der,
    protocol_assessment,
    validate_host,
    validate_port,
)
from support import exit_code


class HostValidationTests(unittest.TestCase):
    def test_accepts_names_and_addresses(self) -> None:
        self.assertEqual(validate_host("App.Example.com."), "App.Example.com")
        self.assertEqual(validate_host("127.0.0.1"), "127.0.0.1")
        self.assertEqual(validate_host("2001:db8::1"), "2001:db8::1")

    def test_rejects_injection_and_urls(self) -> None:
        for raw in ("", "example.com/path", "host name", "https://example.com", "-bad.example", "a..b.com"):
            with self.assertRaises(ValueError):
                validate_host(raw)

    def test_port_bounds(self) -> None:
        self.assertEqual(validate_port(443), 443)
        for port in (0, 65536, -1):
            with self.assertRaises(ValueError):
                validate_port(port)


class ClassificationTests(unittest.TestCase):
    def test_modern_and_obsolete_protocols(self) -> None:
        self.assertEqual(protocol_assessment("TLSv1.3").status, "pass")
        self.assertEqual(protocol_assessment("TLSv1.2").status, "pass")
        self.assertEqual(protocol_assessment("TLSv1").status, "fail")
        self.assertEqual(protocol_assessment(None).status, "fail")

    def test_ciphers(self) -> None:
        self.assertEqual(cipher_assessment("TLS_AES_128_GCM_SHA256").status, "pass")
        self.assertEqual(cipher_assessment("TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA").status, "warn")
        self.assertEqual(cipher_assessment("TLS_RSA_WITH_RC4_128_SHA").status, "fail")
        self.assertEqual(cipher_assessment("TLS_RSA_WITH_3DES_EDE_CBC_SHA").status, "fail")

    def test_certificate_window(self) -> None:
        now = dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc)
        expired = certificate_window(now - dt.timedelta(days=400), now - dt.timedelta(days=1), now)
        self.assertEqual(expired[0].status, "fail")
        soon = certificate_window(now - dt.timedelta(days=10), now + dt.timedelta(days=5), now)
        self.assertEqual(soon[0].status, "warn")
        fine = certificate_window(now - dt.timedelta(days=10), now + dt.timedelta(days=90), now)
        self.assertEqual(fine[0].status, "pass")

    def test_parse_peercert_time(self) -> None:
        parsed = parse_cert_time("Jun  1 00:00:00 2026 GMT")
        self.assertEqual(parsed, dt.datetime(2026, 6, 1, tzinfo=dt.timezone.utc))


class CertificateParseTests(unittest.TestCase):
    def test_extracts_validity_from_a_local_certificate(self) -> None:
        material = ssl.create_default_context().get_ca_certs(binary_form=True)
        if not material:
            self.skipTest("system CA bundle is not available as DER")
        window = extract_validity(material[0])
        self.assertIsNotNone(window)
        assert window is not None
        not_before, not_after = window
        self.assertLess(not_before, not_after)

    def test_pem_round_trip_rejects_garbage(self) -> None:
        with self.assertRaises(ValueError):
            pem_to_der("-----BEGIN CERTIFICATE-----\n!!!!\n-----END CERTIFICATE-----\n")


class LocalServerTests(unittest.TestCase):
    def test_assess_reads_a_local_certificate(self) -> None:
        with TemporaryDirectory() as tmp:
            directory = Path(tmp)
            cert = directory / "cert.pem"
            key = directory / "key.pem"
            subprocess.run(
                [
                    "openssl",
                    "req",
                    "-x509",
                    "-newkey",
                    "rsa:2048",
                    "-keyout",
                    str(key),
                    "-out",
                    str(cert),
                    "-days",
                    "90",
                    "-nodes",
                    "-subj",
                    "/CN=localhost",
                ],
                check=True,
                capture_output=True,
            )
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert, key)
            stop = threading.Event()
            bound = socket.socket()
            bound.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bound.bind(("127.0.0.1", 0))
            bound.listen(8)
            bound.settimeout(0.2)
            port = bound.getsockname()[1]

            def serve() -> None:
                while not stop.is_set():
                    try:
                        connection, _addr = bound.accept()
                    except TimeoutError:
                        continue
                    except OSError:
                        break
                    try:
                        peer = context.wrap_socket(connection, server_side=True)
                        peer.settimeout(2)
                        with contextlib.suppress(TimeoutError):
                            peer.recv(32)
                        peer.close()
                    except ssl.SSLError:
                        connection.close()

            thread = threading.Thread(target=serve, daemon=True)
            thread.start()
            try:
                checks = {item.name: item for item in assess("127.0.0.1", port, 3)}
            finally:
                stop.set()
                bound.close()
                thread.join(timeout=3)
        self.assertEqual(checks["trust"].status, "fail")
        self.assertEqual(checks["certificate-validity"].status, "pass")
        self.assertIn("SHA-256", checks["certificate-fingerprint"].detail)
        self.assertIn(checks["protocol"].status, {"pass", "warn"})


class CliTests(unittest.TestCase):
    def test_help(self) -> None:
        with self.assertRaises(SystemExit) as caught:
            main(["--help"])
        self.assertEqual(caught.exception.code, 0)

    def test_refuses_without_authorisation(self) -> None:
        self.assertEqual(exit_code(main, ["--host", "127.0.0.1", "--port", "443"]), 2)

    def test_rejects_bad_host_before_connecting(self) -> None:
        self.assertEqual(exit_code(main, ["--host", "not a host", "--authorized"]), 2)


if __name__ == "__main__":
    unittest.main()

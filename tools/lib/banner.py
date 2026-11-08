"""Shared authorisation banner and small CLI helpers."""

from __future__ import annotations

import sys

BANNER = """\
AUTHORISED USE ONLY
This utility is a defensive aid. It does not discover hosts, attempt
logins, or send exploit payloads. Use it only on systems you own or
are explicitly authorised to test. Unauthorised access is unlawful.
The --authorized flag records your attestation. It does not grant permission.
"""


def emit_banner(stream=None) -> None:
    print(BANNER, file=stream or sys.stderr)


def fail(message: str, code: int = 2) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def require_authorized(authorized: bool) -> None:
    """Print the banner and refuse to touch a target without the flag."""
    emit_banner()
    if not authorized:
        fail(
            "refusing to run without --authorized. "
            "Pass it only when you have permission to test the target you named."
        )

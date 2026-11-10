"""Shared authorisation banner, exit codes, and small CLI helpers.

Network utilities call :func:`require_authorized` before they open a socket.
``--authorized`` records the operator's attestation. It does not grant permission.
"""

from __future__ import annotations

import math
import sys
from typing import NoReturn, TextIO

# 0: the check finished with no fail-level result (or the local file was written / accepted).
# 1: the check finished and found a fail-level gap, or a rules file is not ready.
# 2: the arguments were refused, or the check could not run.
EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2

BANNER = """\
AUTHORISED USE ONLY
This utility is a defensive aid. It does not discover hosts, attempt
logins, or send exploit payloads. Use it only on systems you own or
are explicitly authorised to test. Unauthorised access is unlawful.
The --authorized flag records your attestation. It does not grant permission.
"""


def emit_banner(stream: TextIO | None = None) -> None:
    """Write the authorised-use banner to stderr, or to ``stream``."""
    print(BANNER, file=stream or sys.stderr)


def fail(message: str, code: int = EXIT_USAGE) -> NoReturn:
    """Print ``error: ...`` to stderr and exit.

    ``code`` defaults to 2 (arguments refused or the check could not run).
    """
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def require_authorized(authorized: bool) -> None:
    """Print the banner and refuse to touch a target without the flag.

    Call this before any DNS lookup, connection, or request. A missing flag
    exits 2 and must not fall through into network code.
    """
    emit_banner()
    if not authorized:
        fail(
            "refusing to run without --authorized. "
            "Pass it only when you have permission to test the target you named."
        )


def validate_timeout(timeout: float) -> float:
    """Return a finite timeout in the closed interval from 1 to 30 seconds.

    Raises:
        ValueError: ``timeout`` is not a finite number in that interval.
    """
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise ValueError("--timeout must be a number of seconds between 1 and 30")
    if not math.isfinite(timeout) or not 1 <= float(timeout) <= 30:
        raise ValueError("--timeout must be between 1 and 30 seconds")
    return float(timeout)

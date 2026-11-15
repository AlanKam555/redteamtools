"""Put the tools directory on sys.path for unittest discovery."""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def exit_code(func: Callable[[Sequence[str]], int], argv: Sequence[str]) -> int:
    """Return a CLI status whether the tool returns it or raises SystemExit."""
    try:
        return func(argv)
    except SystemExit as exc:
        status = exc.code
        if status is None:
            return 0
        if isinstance(status, int):
            return status
        return 2

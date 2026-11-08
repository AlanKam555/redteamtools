"""Put the tools directory on sys.path for unittest discovery."""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def exit_code(func, argv):
    """Return a CLI status whether the tool returns it or raises SystemExit."""
    try:
        return func(argv)
    except SystemExit as exc:
        return exc.code

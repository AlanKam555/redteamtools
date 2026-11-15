#!/usr/bin/env python3
"""CLI: review HTTP security headers on one authorised URL.

Exit status: 0 no fail-level result, 1 a fail-level gap, 2 refused or could not run.
The process does not open a connection unless ``--url`` and ``--authorized`` are both accepted.
"""

from __future__ import annotations

from lib.http_headers import main

if __name__ == "__main__":
    raise SystemExit(main())

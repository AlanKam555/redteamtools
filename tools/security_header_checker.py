#!/usr/bin/env python3
"""CLI: review HTTP security headers on one authorised URL."""

from __future__ import annotations

import sys

from lib.http_headers import main

if __name__ == "__main__":
    sys.exit(main())

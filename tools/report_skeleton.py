#!/usr/bin/env python3
"""CLI: write a local Markdown security-report skeleton."""

from __future__ import annotations

import sys

from lib.report_skeleton import main

if __name__ == "__main__":
    sys.exit(main())

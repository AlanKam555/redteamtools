#!/usr/bin/env python3
"""CLI: check a local rules-of-engagement file for required decisions."""

from __future__ import annotations

import sys

from lib.roe_validator import main

if __name__ == "__main__":
    sys.exit(main())

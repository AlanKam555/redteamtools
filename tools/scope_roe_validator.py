#!/usr/bin/env python3
"""CLI: check a local rules-of-engagement file for required decisions.

Exit status: 0 the file is complete enough to read, 1 it is not ready, 2 it
could not be read. This program never opens a network connection.
"""

from __future__ import annotations

import sys

from lib.roe_validator import main

if __name__ == "__main__":
    sys.exit(main())

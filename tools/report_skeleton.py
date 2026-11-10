#!/usr/bin/env python3
"""CLI: write a local Markdown security-report skeleton.

Exit status: 0 the draft was written, 2 the arguments were refused or the file
could not be written. This program never opens a network connection.
"""

from __future__ import annotations

import sys

from lib.report_skeleton import main

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""CLI: review the certificate and TLS configuration of one authorised host."""

from __future__ import annotations

import sys

from lib.tls_config import main

if __name__ == "__main__":
    sys.exit(main())

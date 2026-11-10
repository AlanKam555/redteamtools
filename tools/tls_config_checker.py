#!/usr/bin/env python3
"""CLI: review the certificate and TLS configuration of one authorised host.

Exit status: 0 no fail-level result, 1 a fail-level gap, 2 refused or could not run.
The process does not open a connection unless ``--host`` and ``--authorized`` are both accepted.
"""

from __future__ import annotations

from lib.tls_config import main

if __name__ == "__main__":
    raise SystemExit(main())

"""Defensive utilities for authorised security assessments.

The command-line tools use the Python 3.10+ standard library only. The two
network tools require an explicit target and ``--authorized`` before they
open a socket. They do not crawl and they do not send exploit payloads.
"""

__version__ = "1.1.0"

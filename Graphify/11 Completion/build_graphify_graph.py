#!/usr/bin/env python3
"""Compatibility entrypoint for the authoritative directed V2 graph build.

V1 used ``directed=False`` and collapsed relationship evidence.  The actual V2
builder writes a directed parallel-preserving JSONL edge store and a separate
aggregated interactive projection.
"""

from build_graphify_v2 import main


if __name__ == "__main__":
    main()


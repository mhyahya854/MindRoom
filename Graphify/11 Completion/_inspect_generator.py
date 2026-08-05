"""Scratch: inspect write targets in generate_product_expansion.py."""
import re
from pathlib import Path

src = Path("generate_product_expansion.py").read_text(encoding="utf-8")
lines = src.splitlines()
write_lines = [
    (i + 1, line.strip())
    for i, line in enumerate(lines)
    if re.search(r"write_json\(|write_jsonl\(|atomic_write|open\(.*[\"']w[\"']", line)
]
for lineno, line in write_lines[:40]:
    print(f"L{lineno}: {line[:120]}")

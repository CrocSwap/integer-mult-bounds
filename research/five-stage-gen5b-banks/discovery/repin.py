"""Exact-string re-pinning: repin.py PKG RULES.json ; rules = [[file, old, new, expected_count]]"""
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); rules = json.load(open(sys.argv[2]))
for f, old, new, cnt in rules:
    p = root / f; s = p.read_text(); k = s.count(old)
    assert k == cnt, (f, old, k, cnt)
    p.write_text(s.replace(old, new)); print('ok', f, k, old[:50], '->', new[:50])

#!/usr/bin/env python3
"""Compare stable results, allowing recompression and different run timings."""
import argparse, json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('relocated',type=Path);a=p.parse_args()
x=json.loads(a.original.read_text());y=json.loads(a.relocated.read_text())
volatile={'started_utc','ended_utc','elapsed_seconds','base_compressed_sha256','candidate_compressed_sha256'}
for k in volatile:x.pop(k,None);y.pop(k,None)
if x!=y:
 for k in sorted(x.keys()|y.keys()):
  if x.get(k)!=y.get(k):print('MISMATCH',k,repr(x.get(k)),repr(y.get(k)))
 raise SystemExit(1)
print('PASS_STABLE_FIELDS',len(x))

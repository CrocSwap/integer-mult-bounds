#!/usr/bin/env python3
"""Exact latest submitted candidate list, serial execution of unchanged price()."""
import importlib.util
import itertools
import json
from pathlib import Path
import time

spec = importlib.util.spec_from_file_location('latest_scan', 'research/bit-ambient-quotient/scan_kernels.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
axes = [150, 102, 255, 153, 15, 240, 105, 1, 7, 9, 165, 170, 204, 90, 60]
candidates = [list(c) for k in (1, 2, 3, 4) for c in itertools.combinations(axes, k)]
assert len(candidates) == 1940
# The author's while len(candidates)<600 loop is never entered.
rows = []
start = time.monotonic()
for i, candidate in enumerate(candidates, 1):
    rows.append(m.price(candidate))
    if i % 100 == 0 or i == len(candidates):
        print(i, '/', len(candidates), 'valid', sum(r[1] == 'ok' for r in rows),
              'seconds', round(time.monotonic()-start, 1), flush=True)
Path(__file__).with_name('latest-bit-scan-results.json').write_text('[\n'+',\n'.join(json.dumps(r,separators=(',',':')) for r in rows)+'\n]\n')

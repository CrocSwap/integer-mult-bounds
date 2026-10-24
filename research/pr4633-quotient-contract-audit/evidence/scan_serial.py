#!/usr/bin/env python3
"""Call the exact submitted price function serially, preserving every result."""
import importlib.util
import json
from pathlib import Path
import sys
import time

kind = sys.argv[1]
path = Path('research') / (kind+'-ambient-quotient') / 'scan_kernels.py'
spec = importlib.util.spec_from_file_location('submitted_scan', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
if kind == 'complex':
    module.setup()
total = 255 if kind == 'bit' else 511
rows = []
start = time.monotonic()
for kernel in range(1, total+1):
    rows.append(module.price(kernel))
    if kernel % 16 == 0 or kernel == total:
        valid = [r for r in rows if r[1] == 'ok']
        best = max(valid, key=lambda r: r[-1]) if valid else None
        print(kernel, '/', total, 'valid', len(valid), 'best', best,
              'seconds', round(time.monotonic()-start, 1), flush=True)
out = Path(__file__).resolve().parent / (kind+'-scan-results.json')
out.write_text('[\n'+',\n'.join(json.dumps(r,separators=(',',':')) for r in rows)+'\n]\n')

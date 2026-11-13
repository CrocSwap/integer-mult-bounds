"""Two bounded new-boundary suites inside one enclosing guarded operation."""
import json
from pathlib import Path
import subprocess
import sys

D = Path(__file__).resolve().parent
rows = []
for mode in ('normal', 'optimized'):
    cmd = [sys.executable, *(['-O'] if mode == 'optimized' else []),
           '-S', '-s', '-P', '-B', str(D / 'test_binding_boundaries.py')]
    result = subprocess.run(cmd, check=False, timeout=8)
    rows.append(dict(mode=mode, argv=cmd, returncode=result.returncode))
print(json.dumps(rows, indent=2))
sys.exit(0 if all(row['returncode'] == 0 for row in rows) else 1)

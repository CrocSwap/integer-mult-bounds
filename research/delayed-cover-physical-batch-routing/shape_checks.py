"""Read-only test driver: child-shape and frozen recursive programs per mode.

This is verification orchestration, not part of the physical runtime program.
"""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
flags = ['-I', '-B'] + (['-O'] if sys.flags.optimize else [])
for script in ('shape/verify.py', 'shape-independent/independent.py', 'recursion_checks.py'):
    result = subprocess.run([sys.executable, *flags, str(HERE/script)],
                            cwd=HERE, timeout=60)
    if result.returncode:
        raise SystemExit(result.returncode)
print(json.dumps({'status': 'PASS_SHAPE_AND_RECURSION_FOUR_REPLAYS',
                  'optimized': bool(sys.flags.optimize)}))

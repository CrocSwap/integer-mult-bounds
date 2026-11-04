"""Read-only test driver: author and separate child-shape replays per mode.

This is verification orchestration, not part of the physical runtime program.
"""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
flags = ['-I', '-B'] + (['-O'] if sys.flags.optimize else [])
for script in ('shape/verify.py', 'shape-independent/independent.py'):
    result = subprocess.run([sys.executable, *flags, str(HERE/script)],
                            cwd=HERE, timeout=60)
    if result.returncode:
        raise SystemExit(result.returncode)
print(json.dumps({'status': 'PASS_CHILD_SHAPE_BOTH_REPLAYS',
                  'optimized': bool(sys.flags.optimize)}))

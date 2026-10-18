#!/usr/bin/env python3
"""One-command replay. Inherited assertion checks always run normally."""
from pathlib import Path
import subprocess
import sys

if sys.version_info < (3,10):
    raise SystemExit('Python 3.10+ is required by inherited int.bit_count frame checks')

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
subprocess.run([sys.executable, '-E', '-B', str(HERE/'audit.py')], cwd=ROOT, check=True)
subprocess.run([sys.executable, '-E', '-B', '-m', 'unittest', 'discover',
                '-s', str(HERE), '-p', 'test_*.py'], cwd=ROOT, check=True)
print('PASS_JOINT_ROOT_CONSTRUCTION additions=30708->30698 paid_roles_saved=10 no_new_kappa')

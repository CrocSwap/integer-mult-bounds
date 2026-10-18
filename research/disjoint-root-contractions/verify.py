#!/usr/bin/env python3
"""One-command exact replay; preserves optimized-Python mode in child checks."""
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
python=[sys.executable,'-B']
if sys.flags.optimize:python.append('-O')
subprocess.run([*python,str(HERE/'audit.py')],cwd=ROOT,check=True)
subprocess.run([*python,'-m','unittest','discover','-s',str(HERE),'-p','test_*.py'],
               cwd=ROOT,check=True)
print('PASS: disjoint-root contraction certificate, independent reconstruction, and 9 tests.')

#!/usr/bin/env python3
"""Run the exact finite census and its negative controls; standard library only.
Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent

if __name__ == '__main__':
    flags = ['-I', '-B'] + (['-O'] if sys.flags.optimize else [])
    for script in ('verify.py', 'test_verify.py'):
        subprocess.run([sys.executable, *flags, str(HERE / script)], check=True)
    print('PASS_HISTORICAL_J_RECONCILIATION_AND_CONTROLS')

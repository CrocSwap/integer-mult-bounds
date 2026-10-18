#!/usr/bin/env python3
"""One-command exact differential verification and failure controls (no timing)."""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled for the inherited audit')
    for script in ('test_packed.py', 'test_replay.py'):
        subprocess.run([sys.executable, '-I', '-B', str(HERE / script)], check=True)
    # Retain all original rational-projector, count, norm and rejection tests.
    subprocess.run([sys.executable, '-I', '-B', str(HERE.parents[1] / 'tests/test_quadratic_affine.py')],
                   check=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'replay.py'), '--compare-rows'], check=True)
    print('PASS_QUADRATIC_AFFINE_DIFFERENTIAL all_frozen_rows_equal=true cases=12')


if __name__ == '__main__':
    main()

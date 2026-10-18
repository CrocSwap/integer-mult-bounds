#!/usr/bin/env python3
"""Run the preserved PR608 verifier with its bundled gk dependency on PYTHONPATH.

The submitted constructor hard-codes an author-local search directory. This
launcher supplies the existing dependency without modifying the pinned source
or any mathematical operation. Arguments are passed to the original verifier.
"""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled')
    dependency = ROOT / 'research/complex-multicold/vendor/pr558/vendor/pr552/complex-local/static44/gk'
    if not (dependency / 'gk_common.py').is_file():
        raise SystemExit('Missing bundled gk_common dependency')
    env = dict(os.environ, PYTHONPATH=str(dependency), PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    command = [sys.executable, '-B', str(ROOT / 'research/complex-571-hpe46/verify.py'),
               '--source', 'larger_gain=' + str(ROOT / 'research/promoted-kernel-coalescing/vendor/larger_gain'),
               *sys.argv[1:]]
    raise SystemExit(subprocess.call(command, cwd=ROOT, env=env))


if __name__ == '__main__':
    main()

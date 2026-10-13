#!/usr/bin/env python3
"""Cold replay and dependency binding of the selected PR543 + PR588 composition.

Requires numpy, sympy, scipy, C++17 and Boost headers. Finite verification
retains the documented all-size, realization, hosting and analytic assumptions.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--jobs', type=int, default=2, help='parallel complex provider chains')
    a = ap.parse_args()
    work = a.work.resolve()
    if sys.flags.optimize or work.exists() or work.is_relative_to(ROOT) or a.jobs < 1:
        raise SystemExit('Use enabled assertions, positive jobs, and a fresh output directory outside the repository')
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1')
    for name in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER'):
        env.pop(name, None)
    steps = []

    def run(name, command):
        start = time.monotonic()
        log_path = work / (name + '.log')
        print('RUN', name, flush=True)
        with log_path.open('w') as log:
            p = subprocess.run(list(map(str, command)), cwd=ROOT, env=env,
                               stdout=log, stderr=subprocess.STDOUT)
        steps.append({'name': name, 'exit_code': p.returncode,
                      'seconds': time.monotonic() - start,
                      'log_sha256': hashlib.sha256(log_path.read_bytes()).hexdigest()})
        (work / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        if p.returncode:
            raise SystemExit(f'{name} failed; inspect {log_path}')
        print('PASS', name, flush=True)

    run('bit543', ['bash', ROOT / 'research/e8-bit-r420/verify.sh', work / 'bit'])
    run('complex588', [sys.executable, '-B', ROOT / 'research/complex-571-free4fc8/verify.py',
                       '--work', work / 'complex', '--jobs', a.jobs])
    run('bindings', [sys.executable, '-B', ROOT / 'scripts/verify_frontier588_bindings.py',
                     '--bit', work / 'bit', '--complex', work / 'complex',
                     '--out', work / 'RESULT.json'])
    print('PASS selected finite composition; inherited all-size and analytic assumptions remain')


if __name__ == '__main__':
    main()

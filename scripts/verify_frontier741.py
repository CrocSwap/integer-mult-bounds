#!/usr/bin/env python3
"""Cold replay of PR589 + PR741 with exact composition binding."""
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
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    a = p.parse_args()
    work = a.work.resolve()
    if sys.flags.optimize or work.exists() or work.is_relative_to(ROOT):
        raise SystemExit('Use enabled assertions and a fresh directory outside the repository')
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1',
               SW4_FRAME8_PYTHON=sys.executable)
    for name in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'SW4_PIN'):
        env.pop(name, None)
    steps = []
    def run(name, command):
        start = time.monotonic()
        log = work / (name + '.log')
        print('RUN', name, flush=True)
        with log.open('w') as stream:
            result = subprocess.run(list(map(str, command)), cwd=ROOT, env=env,
                                    stdout=stream, stderr=subprocess.STDOUT)
        steps.append(dict(name=name, exit_code=result.returncode, seconds=time.monotonic()-start,
                          log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
        (work / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        if result.returncode:
            raise SystemExit(f'{name} failed; see {log}')
        print('PASS', name, flush=True)
    run('bit589', ['bash', ROOT / 'research/e8-bit-p111-tuned/tune/verify.sh', work / 'bit'])
    run('complex741', [sys.executable, '-B', ROOT / 'research/complex-sw4-frame8/verify.py',
                       '--work', work / 'complex'])
    run('bindings', [sys.executable, '-B', ROOT / 'scripts/verify_frontier741_bindings.py',
                     '--bit', work / 'bit', '--complex', work / 'complex', '--out', work / 'RESULT.json'])
    print('PASS selected finite composition; inherited hypotheses remain')


if __name__ == '__main__':
    main()

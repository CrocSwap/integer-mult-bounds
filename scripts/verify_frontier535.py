#!/usr/bin/env python3
"""Cold finite replay of PR535+510, including the previously reviewed foundation.

Requires numpy, sympy, scipy, C++17 and Boost headers. This does not establish
the inherited all-size compiler, physical realization or analytic assumptions.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    a = ap.parse_args()
    work = a.work.resolve()
    if sys.flags.optimize or work.exists() or work.is_relative_to(ROOT):
        raise SystemExit('Use enabled assertions and a fresh directory outside the repository')
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1')
    steps = []

    def run(name, script, *args):
        start = time.monotonic()
        print('RUN', name, flush=True)
        with (work / (name + '.log')).open('w') as log:
            proc = subprocess.run([sys.executable, '-B', str(ROOT / script), *map(str, args)],
                                  cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        steps.append({'name': name, 'exit': proc.returncode, 'seconds': time.monotonic() - start})
        (work / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        if proc.returncode:
            raise SystemExit(f'{name} failed; inspect its log')
        print('PASS', name, flush=True)

    run('foundation', 'scripts/verify_frontier531.py', '--work', work / 'foundation')
    # The preceding foundation replays PR493. --light skips only that duplicate
    # parent replay; all R480 and nine-stage construction checks still execute.
    run('bit510', 'research/e8-r480-nine-stage/verify.py', work / 'bit', '--light')
    run('complex535', 'research/post-center-rank4-global/replay_delta.py',
        '--baseline', ROOT / 'research/direct-delivery504-global', '--work', work / 'complex', '--rebuild-local')
    local = work / 'local'
    local.mkdir()
    shutil.copyfile(work / 'complex/scalar/CANONICAL-WORD.json.gz', local / 'CANONICAL-WORD.json.gz')
    run('full-phases', 'research/direct504-kernel92/code/phases_full.py', local,
        ROOT / 'research/direct-delivery504-global/vendor/clifford')
    prefix = 'research/direct-delivery504-global/code/'
    run('emit-local', prefix + 'emit_local.py', local)
    run('independent-local', prefix + 'audit_local.py', local)
    run('wrappers', prefix + 'adapters_local.py', local / 'CANONICAL-WORD.json.gz',
        local / 'RESIDUAL-ADAPTERS.json', local / 'LEMMA-A.json')
    run('owners', prefix + 'audit_supplier_hosted.py', work / 'complex/base', work / 'complex/hosted',
        work / 'OWNER-CONTROLS.json', '--mutation-controls')
    run('bindings', 'scripts/verify_frontier535_bindings.py', '--bit', work / 'bit',
        '--complex', work / 'complex', '--local', local, '--out', work / 'RESULT.json')
    print('PASS finite composition; inherited all-size and analytic assumptions remain')


if __name__ == '__main__':
    main()

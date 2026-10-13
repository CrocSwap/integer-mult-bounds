#!/usr/bin/env python3
"""Rebuild the selected PR531/523 complex and PR493 bit finite construction.

Needs Python 3.11+, numpy, sympy, C++17 and Boost headers. Set CXX and
BOOST_INCLUDE when needed. Output is a new directory outside the repository.
All-size/compiler and analytic assumptions are not proved by this replay.
Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    a = p.parse_args()
    work = a.work.resolve()
    if work.exists() or work.is_relative_to(ROOT):
        raise SystemExit('Use a new output directory outside the repository')
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1')
    steps = []

    def run(name, command):
        start = time.monotonic()
        print('RUN', name, flush=True)
        with (work / (name + '.log')).open('w') as log:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        steps.append(dict(name=name, exit=result.returncode, seconds=time.monotonic()-start))
        (work / 'STEPS.json').write_text(json.dumps(steps, indent=2) + '\n')
        if result.returncode:
            raise SystemExit(f'{name} failed; see {work / (name + ".log")}')
        print('PASS', name, flush=True)

    def python(name, script, *args):
        run(name, [sys.executable, '-B', str(script), *map(str, args)])

    direct = ROOT / 'research/direct-delivery504-global'
    run('bit493', ['bash', 'research/e8-bit-carrier-skeleton/verify.sh', str(work / 'bit')])
    python('cold523', ROOT / 'research/punctured112-global/verify.py', '--work', work / 'predecessor')
    python('direct531', direct / 'verify_fast.py', '--work', work / 'direct', '--rebuild-local', '--delta-phases')
    local = work / 'direct/scalar'
    python('emit-local', direct / 'code/emit_local.py', local)
    python('audit-local', direct / 'code/audit_local.py', local)
    python('wrappers', direct / 'code/adapters_local.py', local / 'CANONICAL-WORD.json.gz',
           local / 'RESIDUAL-ADAPTERS.json', local / 'LEMMA-A.json')
    python('wrapper-swap', ROOT / 'scripts/verify_frontier531_wrapper_swap.py',
           '--local', local, '--out', work / 'WRAPPER-SWAP.json')
    python('frontier', direct / 'code/audit_same_partition_frontier.py',
           '--packets', direct / 'inputs/hamming', '--out', work / 'FRONTIER.json')
    python('owner-controls', direct / 'code/audit_supplier_hosted.py', work / 'direct/base',
           work / 'direct/hosted', work / 'OWNER-CONTROLS.json', '--mutation-controls')
    python('bindings', ROOT / 'scripts/verify_frontier531_bindings.py', '--bit', work / 'bit',
           '--predecessor', work / 'predecessor', '--direct', work / 'direct', '--out', work / 'RESULT.json')
    print('PASS reviewed finite construction; see', work / 'RESULT.json')


if __name__ == '__main__':
    main()

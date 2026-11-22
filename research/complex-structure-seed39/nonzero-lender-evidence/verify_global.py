#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Fresh FOUR428 global and outer replay using explicitly hash-bound native evidence.

To independently regenerate the expensive native evidence, first use
replay_native.py. This command verifies every retained native output hash;
it does not describe receipt reuse as fresh native compilation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
G = HERE/'global-admission'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    if not __debug__:
        raise RuntimeError('Retained assertions must be enabled')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    work = a.out.resolve()
    if work.exists():
        raise ValueError('A fresh output directory is required')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', AUDIT_FAST_SHARDS='4')
    for key in ('PYTHONOPTIMIZE','WITNESS_DISCOVER','WITNESS_RECORD','WITNESS_SPEC'):
        env.pop(key, None)
    # The preparer owns initial directory creation and verifies immutable pins.
    subprocess.run([sys.executable, '-B', str(G/'prepare_runtime.py'), '--out', str(work)], env=env, check=True)
    prep = read(work/'PREPARATION.json')
    (work/'STRICT-INPUTS.json').write_text(json.dumps(prep['runtime_files'], indent=2)+'\n')
    runtime = work/'layout/packing428'
    source = work/'layout/joint1148-round45/source/research/complex-k492-owner-repair/vendor/multicold'
    stages = []

    def run(name, command):
        start = time.monotonic()
        log = work/(name+'.log')
        with log.open('w') as stream:
            result = subprocess.run(command, env=env, stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=result.returncode, seconds=time.monotonic()-start,
                           log_sha256=sha(log), command=command))
        (work/'STAGES.json').write_text(json.dumps(stages, indent=2)+'\n')
        if result.returncode:
            raise RuntimeError(name+' failed: '+log.read_text()[-5000:])
        print('PASS', name, flush=True)

    run('strict-global', prep['commands']['strict'])
    run('geometry-controls', [sys.executable, '-B', str(runtime/'geometry_controls.py'),
        '--source', str(source), '--strict', str(work/'strict'), '--out', str(work/'GEOMETRY-CONTROLS.json')])
    run('independent-global-evidence', [sys.executable, '-B', str(G/'check_global_evidence.py'),
        '--work', str(work), '--out', str(work/'GLOBAL-EVIDENCE-CHECK.json')])
    run('modern-outer', [sys.executable, '-B', str(G/'outer-screen/run_outer_admission.py'),
        '--strict', str(work/'strict'), '--parent-admission', str(G/'retained-pr1297'), '--out', str(work/'modern-outer')])
    outer = read(work/'modern-outer/OUTER-ADMISSION.json')
    assert outer['status'] == 'PASS_STRICT_CANDIDATE_FINITE_AND_OUTER_ARITHMETIC_CONDITIONAL_BOUND'
    assert read(work/'GLOBAL-EVIDENCE-CHECK.json')['status'] == 'PASS_STRICT_FOUR428_GLOBAL_EVIDENCE_BINDINGS_NO_MODERN_OUTER_CLAIM'
    result = dict(status='PASS_FOUR428_CONDITIONAL_BOUND', kappa=outer['kappa'], kappa_decimal=outer['kappa_decimal'],
                  base_commit='7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261', assignment_seed=39,
                  native_evidence_policy='Exact archived native outputs verified by SHA256 and word payload; not a fresh native compilation.',
                  input_sha256={str(p.relative_to(HERE)):sha(p) for p in (HERE/'NATIVE-RESULT.json', G/'owners/SPEC.json', G/'GLOBAL-BUFFER-BINDING.json.gz')},
                  output_sha256={str(p.relative_to(work)):sha(p) for p in (work/'strict/RESULT.json', work/'GLOBAL-EVIDENCE-CHECK.json', work/'modern-outer/OUTER-ADMISSION.json')},
                  stages=stages, scope=outer['scope'])
    (work/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], result['kappa_decimal'])


if __name__ == '__main__':
    main()

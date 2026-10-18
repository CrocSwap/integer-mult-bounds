#!/usr/bin/env python3
"""Bounded fresh finite checks plus explicitly scoped recorded-summary checks.

Full native/controller/outer admission is the separate full-admission replay.
Prepared with substantial OpenAI Codex assistance. SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PROFILE = {'1':11747920, '2':3453480, '3':1112042, '4':486540,
           '5':103690, '8':38160, '48':202828}
LOWER = Fraction('0.001730394391813963415120')
UPPER = Fraction('0.001730394391813963415121')
KAPPA = LOWER - Fraction(1, 10**46) - Fraction(1, 10**70)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def snapshot():
    return {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in HERE.rglob('*') if p.is_file()}


def main():
    require(__debug__ and not sys.flags.optimize, 'Run with assertions enabled')
    before = snapshot()
    out = Path(tempfile.mkdtemp(prefix='staged-release-retiming-t530-'))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    stages = []

    def run(name, relative, *args):
        start = time.monotonic()
        command = [sys.executable, '-B', str(HERE / relative), *map(str, args)]
        result = subprocess.run(command, cwd=REPO, env=env,
                                capture_output=True, text=True, timeout=240)
        (out / (name + '.log')).write_text(result.stdout + result.stderr)
        require(result.returncode == 0, name + ' failed: ' + str(out / (name + '.log')))
        stages.append({'stage':name, 'exit_code':0, 'seconds':time.monotonic()-start})
        print('PASS ' + name, flush=True)
        return result.stdout

    run('local', 'local-audit/verify.py', '--out', out / 'local')
    run('owner', 'owner-audit/run.py', '--repo', REPO, '--out', out / 'owner')
    run('numerics', 'numerics/run.py', '--out', out / 'numerics')
    run('packing', 'packing-cap/check_retimed_cap.py', '--out', out / 'packing')
    summary = json.loads(run('recorded-summary', 'full-admission/check_recorded_summary.py'))

    local = read(out / 'local/VERIFY.json')
    owner = read(out / 'owner/RESULT.json')
    owner_run = read(out / 'owner/RUN.json')
    moment = read(out / 'numerics/MOMENT.json')
    outer = read(out / 'numerics/outer/RESULT.json')
    cap = read(out / 'packing/RETIMED-PACKING-CAP.json')
    require(local['status'] == 'PASS_PORTABLE_LOCAL_RETIMING_AUDIT', 'local status')
    require(owner_run['status'] == 'PASS_LEAN_REGENERATED_OWNER_AUDIT', 'fresh owner status')
    require(owner['profile'] == moment['new_profile'] == cap['literal_T530_profile']
            == summary['profile'] == PROFILE, 'all components bind the same full profile')
    require(owner['roles'] == 1946160 and owner['calls'] == moment['calls'] == 4770,
            'complete literal role/call coverage')
    require(owner['physical'] == summary['physical'] == 475389, 'physical stock')
    require(moment['status'] == 'PASS_TWO_ENGINE_EXACT_MOMENT', 'two-engine moment status')
    require(list(map(Fraction, moment['root_interval'])) == [LOWER, UPPER], 'exact root interval')
    require(list(map(Fraction, cap['literal_root'])) == [LOWER, UPPER], 'independent literal root')
    require(outer['status'] == 'PASS_RETIMED_MODERN_OUTER_ARITHMETIC'
            and outer['strict_inequalities'] == 63 and outer['rejected_controls'] == 17,
            'complete bounded outer arithmetic')
    require(Fraction(outer['kappa']) == Fraction(summary['kappa']) == KAPPA, 'exact endpoint binding')
    require(cap['status'] == 'PASS_RETIMED_ALL_2551_FIXED_INVENTORY_PATTERNS'
            and (cap['patterns'], cap['strict'], cap['symbolically_zero']) == (2551, 2539, 12),
            'all fixed-inventory patterns')
    require(summary['status'] == 'PASS_PUBLIC_RECORDED_SUMMARY_BINDINGS', 'narrow summary status')
    require(snapshot() == before, 'package files changed during replay')
    receipt = {
        'status':'PASS_STAGED_RELEASE_RETIMING_T530_BOUNDED_CHECKS',
        'kappa':str(KAPPA), 'profile':PROFILE, 'stages':stages,
        'package_files_unchanged':True,
        'scope':'Fresh finite local/operator, regenerated ownership/invoice, exact arithmetic and scoped packing checks; full native/controller/outer admission is retained evidence only in this command. Inherited general assumptions remain.'}
    (out / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    print('Fresh evidence: ' + str(out))


if __name__ == '__main__':
    main()

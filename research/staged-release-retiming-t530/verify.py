#!/usr/bin/env python3
"""Bounded fresh finite checks plus explicitly scoped recorded-summary checks.

Full native/controller/outer admission is the separate full-admission replay.
Prepared with substantial OpenAI Codex assistance. SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import copy
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


def check_recorded_cache(evidence, native):
    observed = evidence['local_byte_checks']
    require(observed['runtime_file_count'] == 658
            and observed['native_cache_files'] == len(native['cache_files']) == 63,
            'complete recorded runtime/native inventory')
    require(set(native['providers']) == {'base', 'extra'}, 'recorded native providers')
    for provider in native['providers'].values():
        prefix = provider['word_sha256'] + '/'
        subset = {name.removeprefix(prefix): digest
                  for name, digest in native['cache_files'].items()
                  if name.startswith(prefix) and name != prefix + 'CACHE.json'}
        require(len(subset) == 12 and provider['complete_native_files'] == subset,
                'complete recorded provider cache subset')


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
    full_run = read(HERE / 'PUBLIC-FULL-REPLAY.json')
    fresh_dir = HERE / 'full-admission/fresh-replay'
    attempt = read(fresh_dir / 'ATTEMPT.json')
    wrapper_result = read(fresh_dir / 'WRAPPER-RESULT.json')
    admission_result = read(fresh_dir / 'ADMISSION-RESULT.json')
    native_receipt = read(fresh_dir / 'NATIVE-RECEIPT.json')
    fresh_evidence = read(fresh_dir / 'EVIDENCE.json')
    require(full_run['status'] == 'PASS_PUBLIC_FULL_WRAPPER_END_TO_END'
            and Fraction(full_run['kappa']) == KAPPA and full_run['profile'] == PROFILE,
            'separate full-wrapper headline agrees with fresh finite checks')
    require(full_run['executed_publication_commit'] == attempt['publication_commit']
            and full_run['executed_wrapper_sha256'] == attempt['wrapper_sha256']
            and full_run['wall_seconds'] == attempt['seconds']
            and full_run['exit_code'] == attempt['exit_code'] == 0
            and full_run['package_files_unchanged'] is attempt['package_files_unchanged'] is True,
            'separate full-wrapper execution identity')
    for field in ('started_at', 'finished_at', 'environment'):
        require(full_run[field] == attempt[field], 'full-wrapper index ' + field)
    require(full_run['source_manifest_sha256'] == wrapper_result['source_manifest_sha256']
            and full_run['runtime_manifest_sha256'] == admission_result['package_manifest_sha256']
            and full_run['original_release_receipt_sha256'] == admission_result['release_receipt_sha256'],
            'full-wrapper source/runtime/terminal index')
    for field, result in [('wrapper_stages', wrapper_result), ('admission_stages', admission_result)]:
        require(full_run[field] == [{key: row[key] for key in ('name', 'exit_code', 'seconds')}
                                   for row in result['stages']], 'full-wrapper index ' + field)
    check_recorded_cache(fresh_evidence, native_receipt)
    for field in ('cache_files', 'complete_native_files'):
        mutant = copy.deepcopy(native_receipt)
        if field == 'cache_files':
            mutant[field] = {}
        else:
            mutant['providers']['base'][field] = {}
        try:
            check_recorded_cache(fresh_evidence, mutant)
        except ValueError:
            pass
        else:
            raise ValueError('incomplete recorded cache accepted: ' + field)
    for field, path in [('fresh_evidence_sha256', 'full-admission/fresh-replay/EVIDENCE.json'),
                        ('evidence_checker_sha256', 'full-admission/fresh_replay_evidence.py')]:
        require(full_run[field] == hashlib.sha256((HERE / path).read_bytes()).hexdigest(),
                'separate full-wrapper evidence binding: ' + field)
    require(snapshot() == before, 'package files changed during replay')
    receipt = {
        'status':'PASS_STAGED_RELEASE_RETIMING_T530_BOUNDED_CHECKS',
        'kappa':str(KAPPA), 'profile':PROFILE, 'stages':stages,
        'package_files_unchanged':True,
        'rejected_recorded_cache_controls':['empty cache inventory', 'empty provider cache subset'],
        'scope':'Fresh finite local/operator, regenerated ownership/invoice, exact arithmetic and scoped packing checks; full native/controller/outer admission is retained evidence only in this command. Inherited general assumptions remain.'}
    (out / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))
    print('Fresh evidence: ' + str(out))


if __name__ == '__main__':
    main()

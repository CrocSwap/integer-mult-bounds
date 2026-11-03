#!/usr/bin/env python3
"""Parent serial wrapper for exact NEW owned-fixture constructor checks only."""
from pathlib import Path
import hashlib
import json
import resource
import shutil
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'implementation'
INVENTORY_SHA = '0e71e65d832b077b21929d6cc7c18e520cc49f807124569720d945bc1e5f5308'
ORACLE_SHA = 'a8fbd525891ab4fced935c4bf97651d44ec369dc8d23acfbfbeb311f9714c7d1'
PLAN_SHA = '895e8e0e90b8c03a44ee1aa06f8ab3ab41f6b94b47edabe8c4c88039b92d8871'


def need(value, message):
    if value is not True:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked_inventory(root):
    raw = (HERE / 'EXECUTION-INVENTORY-v1.json').read_bytes()
    need(sha(raw) == INVENTORY_SHA, 'frozen exact inventory identity')
    entries = json.loads(raw)['files']
    expected = {r['path'] for r in entries}
    need(len(expected) == len(entries) == 28, 'frozen28 files')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    need(actual == expected and not any(p.is_symlink() for p in root.rglob('*')), 'inventory/link drift')
    for row in entries:
        data = (root / row['path']).read_bytes()
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'frozen file ' + row['path'])


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))
    resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 ** 2, 1024 ** 2))


def main():
    oracle_raw = (HERE.parent / 'review/CONTROL-ORACLE-v1.json').read_bytes()
    need(sha(oracle_raw) == ORACLE_SHA, 'independent oracle identity')
    oracle = json.loads(oracle_raw)
    need(oracle['control_count'] == 17, 'reviewed17 cases')
    checked_inventory(SOURCE)
    plan_raw = (SOURCE / 'controls/CONTROL-PLAN-v1.json').read_bytes()
    need(sha(plan_raw) == PLAN_SHA, 'exact reviewed plan')
    plan = json.loads(plan_raw)
    need([{'id': x['id'], 'outcome': x['expected']} for x in plan['cases']] == oracle['controls'], 'independent ordered plan oracle')
    cold = HERE / 'cold-exact-v1'
    need(not cold.exists(), 'fresh cold destination; no retry')
    shutil.copytree(SOURCE, cold, symlinks=True)
    checked_inventory(cold)
    nonce = uuid.uuid4().hex
    (HERE / 'RUN-NONCE-v1.json').write_text(json.dumps({'nonce': nonce, 'created_by_parent': True}) + '\n')
    expected = {'status': oracle['expected_status'], 'controls': oracle['controls'],
                'claims': oracle['expected_claims'], 'original_definitions_executed': False}
    runs = []
    for mode in ('normal', 'optimized'):
        checked_inventory(cold)
        fixture = HERE / ('retained-fixtures-' + mode + '-' + nonce)
        need(not fixture.exists(), 'fresh retained fixture root')
        command = [sys.executable, '-B'] + (['-O'] if mode == 'optimized' else []) + [str(cold / 'controls/owned_fixture_controls.py'), str(fixture)]
        prior = resource.getrusage(resource.RUSAGE_CHILDREN)
        start = time.monotonic()
        with (HERE / (mode + '.stdout')).open('xb') as out, (HERE / (mode + '.stderr')).open('xb') as err:
            process = subprocess.Popen(command, cwd=cold, stdin=subprocess.DEVNULL, stdout=out, stderr=err, preexec_fn=limits)
            timed_out = False
            try:
                code = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.kill()
                code = process.wait()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        raw = (HERE / (mode + '.stdout')).read_bytes()
        stderr = (HERE / (mode + '.stderr')).read_bytes()
        runs.append({'mode': mode, 'command': command, 'fixture_root': str(fixture), 'returncode': code,
                     'timeout': timed_out, 'wall_seconds': time.monotonic() - start,
                     'cpu_seconds': after.ru_utime + after.ru_stime - prior.ru_utime - prior.ru_stime,
                     'cumulative_child_peak_rss_kib': after.ru_maxrss,
                     'stdout_sha256': sha(raw), 'stderr_sha256': sha(stderr)})
        (HERE / 'RESULTS-v1.json').write_text(json.dumps({'runs': runs, 'nonce': nonce,
            'claim': 'NEW owned-fixture constructor only; full joined prerequisite HOLD',
            'original_credit': 0, 'outside_costs': 'OPEN_NOT_ZERO'}, indent=2) + '\n')
        need(code == 0 and not timed_out and stderr == b'', 'failed attempt retained; no rerun')
        need(json.loads(raw) == expected, 'exact independent stdout oracle and scope')
        checked_inventory(cold)
    checked_inventory(SOURCE)
    print(json.dumps({'status': 'PASS_EXACT_REVIEWED_NEW_CONSTRUCTOR_FIXTURES', 'unique_cases': 17,
                      'mode_observations': 34, 'joined_prerequisite': 'HOLD', 'original_credit': 0}))


if __name__ == '__main__':
    main()

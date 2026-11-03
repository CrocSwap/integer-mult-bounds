#!/usr/bin/env python3
"""Parent-only serial execution of independently reviewed NEW source/DATA checks."""
from pathlib import Path
import hashlib
import json
import resource
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent / 'package/research/h25-full-owner-bootstrap-selection'
FREEZE_SHA = '6489a45662473b642cdc12309456ed8401b9a6ecffeb4cb28c09925a72c82894'
PLAN_SHA = 'ddff3faf956d27bc98655625668ccaed61bdd86b11edc861b0da206eca5b32b5'
IDS = ('corrected_positive', 'old_basename', 'arbitrary_output', 'omit_group01',
       'precreated_output', 'old_domain', 'omit_provider', 'omit_receiver',
       'unknown_claim_complete', 'signature_as_caller', 'fake_authority',
       'prefix_as_full', 'graph_pass_runtime', 'graph_pass_c07', 'graph_pass_credit')
EXPECTED = [{'id': key, 'outcome': 'ACCEPT_SOURCE_PROPOSAL_ONLY' if i == 0 else 'REJECT'}
            for i, key in enumerate(IDS)]


def need(value, message):
    if value is not True:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory(root):
    raw = (root / 'AUTHOR-FREEZE-v1.json').read_bytes()
    need(sha(raw) == FREEZE_SHA, 'independent frozen package receipt')
    receipt = json.loads(raw)
    paths = {r['path'] for r in receipt['files']}
    need(len(paths) == len(receipt['files']), 'duplicate frozen path')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    need(actual == paths | {'AUTHOR-FREEZE-v1.json'}, 'exact package inventory')
    need(not any(p.is_symlink() for p in root.rglob('*')), 'package symlink')
    for row in receipt['files']:
        data = (root / row['path']).read_bytes()
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'frozen bytes: ' + row['path'])
    plan = (root / 'CONTROL-PLAN-v1.json').read_bytes()
    need(sha(plan) == PLAN_SHA, 'independent plan identity')
    cases = json.loads(plan)['cases']
    need([{'id': x['id'], 'outcome': x['expected']} for x in cases] == EXPECTED,
         'independent exact ordered15 oracle')
    return len(actual)


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS, (1024 ** 3, 1024 ** 3))
    resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 ** 2, 1024 ** 2))


def main():
    count = inventory(PACKAGE)
    cold = HERE / 'cold-exact-v1'
    need(not cold.exists(), 'fresh cold copy required; no retry')
    shutil.copytree(PACKAGE, cold, symlinks=True)
    inventory(cold)
    results = []
    for mode in ('normal', 'optimized'):
        inventory(cold)
        command = [sys.executable, '-B'] + (['-O'] if mode == 'optimized' else []) + [str(cold / 'verify.py'), '--controls']
        began = time.monotonic()
        prior = resource.getrusage(resource.RUSAGE_CHILDREN)
        with (HERE / (mode + '.stdout')).open('xb') as out, (HERE / (mode + '.stderr')).open('xb') as err:
            process = subprocess.Popen(command, cwd=cold, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                       preexec_fn=child_limits)
            timeout = False
            try:
                rc = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                timeout = True
                process.kill()
                rc = process.wait()
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        elapsed = time.monotonic() - began
        raw = (HERE / (mode + '.stdout')).read_bytes()
        stderr = (HERE / (mode + '.stderr')).read_bytes()
        row = {'mode': mode, 'command': command, 'returncode': rc, 'timeout': timeout,
               'wall_seconds': elapsed, 'cpu_seconds': after.ru_utime + after.ru_stime - prior.ru_utime - prior.ru_stime,
               'cumulative_child_peak_rss_kib': after.ru_maxrss,
               'stdout_sha256': sha(raw), 'stderr_sha256': sha(stderr)}
        results.append(row)
        (HERE / 'RESULTS-v1.json').write_text(json.dumps({'runs': results, 'original_credit': 0,
             'outside_costs': 'OPEN_NOT_ZERO', 'claim': 'NEW exact finite source/DATA checks only'}, indent=2) + '\n')
        need(rc == 0 and not timeout and stderr == b'', 'failed mode retained; no rerun')
        actual = json.loads(raw)
        need(actual == {'status': 'PASS_FINITE_SOURCE_AUDIT_ONLY_GRAPH_INCOMPLETE', 'original_credit': 0,
             'runtime_admission': False, 'C07': False, 'full_C05': False, 'full_V03': False,
             'controls': EXPECTED}, 'independent result and non-admission oracle')
        inventory(cold)
    inventory(PACKAGE)
    print(json.dumps({'status': 'PASS_REVIEWED_COLD_EXACT_NEW_DATA_CHECKS', 'modes': 2,
                      'cases_per_mode': 15, 'files': count, 'original_credit': 0, 'graph_complete': False}))


if __name__ == '__main__':
    main()

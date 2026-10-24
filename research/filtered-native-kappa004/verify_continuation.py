#!/usr/bin/env python3
"""Authenticate and replay the scoped continuation without editing evidence.

Apache-2.0; substantial OpenAI Codex assistance. Passing this verifier is
not an admission of a new kappa construction.
"""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def scientific(x):
    if isinstance(x, dict):
        return {k: scientific(v) for k, v in x.items() if k != 'elapsed_seconds'}
    if isinstance(x, list):
        return [scientific(v) for v in x]
    return x


def read(p):
    return json.loads(p.read_text())


def main():
    ap = argparse.ArgumentParser()
    bundled_archive = HERE/'inputs/original-packet.tar.gz'
    ap.add_argument('--archive', type=Path,
                    default=bundled_archive if bundled_archive.is_file()
                    else ROOT/'original-packet.tar.gz')
    ap.add_argument('--replay-predecessor', action='store_true')
    ap.add_argument('--with-milp', action='store_true')
    ap.add_argument('--receipt', type=Path)
    args = ap.parse_args()
    sources = read(HERE/'SOURCES.json')
    manifest = read(HERE/'MANIFEST.json')
    for name, pin in manifest['files'].items():
        raw = (HERE/name).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
             'Package source binding: '+name)
    for row in sources['repository_dependencies']:
        need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
             'Dependency binding: '+row['path'])
    need(sha256(args.archive.read_bytes()).hexdigest() == sources['original_archive']['sha256'],
         'Original packet archive binding')
    commands = []
    begin = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='filtered-native-k004-') as temporary:
        temp = Path(temporary)
        packet_dir = temp/'original'
        packet_dir.mkdir()
        with tarfile.open(args.archive) as archive:
            archive.extractall(packet_dir, filter='data')
        packet = packet_dir/'filtered_native_implementation'
        need(packet.is_dir(), 'Original archive layout')
        work = temp/'repo'
        package = work/'research/filtered-native-kappa004'
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns('__pycache__'))
        for row in sources['repository_dependencies']:
            dest = work/row['path']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT/row['path'], dest)
        environment = dict(os.environ)
        environment.pop('PYTHONOPTIMIZE', None)
        environment['PYTHONPYCACHEPREFIX'] = str(temp/'bytecode')
        environment['PYTHONHASHSEED'] = '0'

        def run(script, extra=(), cwd=work, timeout=600):
            path = package/script
            command = [sys.executable, '-B', str(path), *map(str, extra)]
            started = time.monotonic()
            result = subprocess.run(command, cwd=cwd, env=environment,
                                    capture_output=True, text=True, timeout=timeout)
            commands.append({'script': script, 'arguments': list(map(str, extra)),
                             'returncode': result.returncode,
                             'elapsed_seconds': round(time.monotonic()-started, 3),
                             'stdout': result.stdout, 'stderr': result.stderr})
            need(result.returncode == 0, script+' failed:\n'+result.stdout+result.stderr)
            print('PASS', script, flush=True)

        if args.replay_predecessor:
            # Fresh extraction: original verification rewrites its own receipts.
            command = [sys.executable, '-B', str(packet/'verify_delivery.py')]
            started = time.monotonic()
            result = subprocess.run(command, cwd=packet, env=environment,
                                    capture_output=True, text=True, timeout=600)
            commands.append({'script': 'predecessor/verify_delivery.py',
                             'returncode': result.returncode,
                             'elapsed_seconds': round(time.monotonic()-started, 3),
                             'stdout': result.stdout, 'stderr': result.stderr})
            need(result.returncode == 0, 'Predecessor replay failed:\n'+result.stdout+result.stderr)
            print('PASS predecessor fourteen focused checks', flush=True)
        for script in ['history_grade_probe.py', 'snapshot_probe.py', 'observer_probe.py',
                       'paired_observer_probe.py']:
            run(script, ['--packet', packet])
        for script in ['exact_pair_check.py', 'acceptance_budget.py', 'independent_budget_check.py', 'repeated_head_probe.py']:
            run(script)
        run('exact_pair_check.py', ['--maximum-cost', 8])
        names = ['history-grades.json', 'snapshot-probe.json', 'observer-probe.json',
                 'paired-observer-probe.json', 'acceptance-budget.json',
                 'independent-budget.json', 'repeated-head-probe.json', 'exact-pair-check.json',
                 'exact-pair-check-budget8.json']
        for name in names:
            need(scientific(read(HERE/'evidence'/name)) == scientific(read(package/'evidence'/name)),
                 'Recomputed scientific evidence differs: '+name)
        need((HERE/'evidence/observer-subspaces.json.gz').read_bytes() ==
             (package/'evidence/observer-subspaces.json.gz').read_bytes(),
             'Recomputed exact observer subspaces differ')
        budget = read(package/'evidence/acceptance-budget.json')
        need(not budget['admitted_construction'] and not budget['new_kappa_claimed'],
             'Missing physical words must block admission')
        history = read(package/'evidence/history-grades.json')
        need(history['maximum_snapshot_source_grade'] == 8 and
             set(history['target_source_grades']) == {9} and
             history['all_original_endpoints'] and history['owned_final_zero'],
             'Physical history endpoint and support controls')
        snap = read(package/'evidence/snapshot-probe.json')
        need(all(not r['recovered'] and r['native_Y_exit_control'] for r in snap['results']),
             'Bounded snapshot negative and positive controls')
        if args.with_milp:
            for mode in range(8):
                run('observer_milp.py', ['--mode', mode, '--maximum-cost', 8, '--seconds', 60])
                result = read(package/f'evidence/observer-milp-mode{mode}-budget8.json')
                need(result['solver_status'] == 2, 'Expected bounded solver search result')
            run('observer_milp.py', ['--mode', 0, '--maximum-cost', 9, '--seconds', 60])
            positive = read(package/'evidence/observer-milp-mode0-budget9.json')
            need(positive['rational_residual_terms'] == 0 and positive['solver_objective'] <= 9,
                 'Rational budget-nine positive control')
    receipt = {'status': 'PASS_SCOPED_CONTINUATION_NO_NEW_KAPPA',
               'new_kappa_claimed': False, 'admitted_construction': False,
               'source_manifest_sha256': sha256((HERE/'MANIFEST.json').read_bytes()).hexdigest(),
               'python': sys.version, 'commands': commands,
               'elapsed_seconds': round(time.monotonic()-begin, 3)}
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(receipt, indent=2)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()

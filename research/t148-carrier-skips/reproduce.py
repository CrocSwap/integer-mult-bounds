#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Full PR3042 source/native release with only three allocation arguments changed.

Requires the completed PR3030 baseline. All predecessor scripts and predicates
remain unchanged. Credit dcharb78, Nick Petalas and the retained source lineage.
"""
import argparse
import importlib.util
import io
import os
import subprocess
import sys
import tarfile
from fractions import Fraction as Q
from pathlib import Path, PurePosixPath

import verify as v

PREFIX = 'research/rank7-restore-carrier-skips'


def export(repo, destination):
    raw = subprocess.run(['git', '-C', str(repo), 'archive', v.HEAD, PREFIX],
                         check=True, capture_output=True, timeout=120).stdout
    v.need(len(raw) < 50_000_000, 'bounded exact source archive')
    destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        items = archive.getmembers()
        v.need(len(items) <= 512, 'bounded source entries')
        for item in items:
            name = PurePosixPath(item.name)
            v.need(not name.is_absolute() and '..' not in name.parts and
                   (item.isfile() or item.isdir()), 'regular bounded source path')
            if item.isdir():
                continue
            v.need(name.is_relative_to(PurePosixPath(PREFIX)), 'exact source prefix')
            target = destination / name.relative_to(PurePosixPath(PREFIX))
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = archive.extractfile(item)
            v.need(stream is not None, 'source stream')
            with stream:
                target.write_bytes(stream.read())
    v.need(v.sha(destination / 'MANIFEST.json') == v.sha(v.P / 'vendor/PR3042-MANIFEST.json'),
           'exact published PR3042 manifest')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--baseline-work', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    repo, baseline, work = args.repo.resolve(), args.baseline_work.resolve(), args.work.resolve()
    v.need(os.name == 'posix' and not sys.flags.optimize, 'POSIX and enabled assertions required')
    v.need(not work.exists() and not work.is_relative_to(v.P), 'fresh external work required')
    v.authenticate()
    v.baseline_modules()
    path = v.ROOT / 'research/rank7-t740-release/reproduce.py'
    spec = importlib.util.spec_from_file_location('original_baseline_harness', path)
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    previous = v.read(baseline / 'RESULT.json')
    v.need(previous['status'] == 'PASS_T740_R1_COMPLETE_RELEASE', 'completed PR3030 baseline release gate')
    previous_stages = v.read(baseline / 'STAGES.json')
    for stage in previous_stages:
        v.need(stage['exit_code'] == 0 and v.sha(baseline / (stage['stage'] + '.log')) == stage['log_sha256'],
               'every completed baseline stage/log binding')
    v.need(harness.check_release(baseline, baseline / 'pr3015', previous['fill_sha256'], previous_stages)
           == previous, 'entire completed baseline rederived')
    work.mkdir()
    source = work / 'pr3042'
    export(repo, source)
    harness.authenticate_tree(source)
    producer = v.load(v.ROOT / 'research/rank7-t148-restore-release/verify.py', 'credited_t148_allocation')
    _, _, _, order, _, fill, dispatch = producer.allocation()
    import gzip
    for name, value in [('COMPOSED-FILL.json.gz', fill), ('ORDER.json', order), ('DISPATCH.json', dispatch)]:
        raw = producer.canonical(value)
        (work / name).write_bytes(gzip.compress(raw, compresslevel=1, mtime=0) if name.endswith('.gz') else raw)
    materialized = dict(fill_sha256=v.sha(work / 'COMPOSED-FILL.json.gz'), roles=543456, replicas=148)
    harness.save(work / 'MATERIALIZED.json', materialized)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for key in ['PYTHONOPTIMIZE', 'PYTHONPATH', 'WITNESS_SPEC', 'WITNESS_RECORD', 'WITNESS_DISCOVER']:
        env.pop(key, None)
    stages = []
    command = [sys.executable, '-B', str(source / 'reproduce.py'), '--repo', str(repo),
               '--work', str(work / 'run'), '--retained', str(baseline / 'run/retained'),
               '--jobs', '1', '--dry-run']
    harness.run_stage('source-preflight', command, work, env, stages, 300)
    recipe = v.read(work / 'run/PREFLIGHT.json')['commands']
    expected = [name for name in harness.RECIPE_NAMES if name != 'fresh-retained-bootstrap']
    v.need([name for name, _ in recipe] == expected, 'complete original retained-cache recipe')
    edits = []
    for name, command in recipe:
        if name == 'complete-admission':
            for flag, old, new in [('--fill', 'FILL.json.gz', 'COMPOSED-FILL.json.gz'),
                                   ('--order', 'ORDER.json', 'ORDER.json'),
                                   ('--dispatch', 'DISPATCH.json', 'DISPATCH.json')]:
                i = command.index(flag) + 1
                v.need(command[i] == str(source / 'allocation' / old), 'exact allocation argument preimage')
                edits.append(dict(argument=flag, old=command[i], new=str(work / new)))
                command[i] = str(work / new)
    v.need(len(edits) == 3, 'only three allocation arguments changed')
    harness.save(work / 'RECIPE.json', dict(commands=recipe, allocation_changes=edits))
    for name, command in recipe:
        harness.run_stage(name, command, work, env, stages, 7200)
    admission = v.read(work / 'run/candidate/RESULT.json')
    receipt = v.read(work / 'run/candidate/release/RELEASE-RECEIPT.json')
    v.need(admission['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and
           receipt['status'] == 'PASS_RELEASE', 'completed supplier and modern outer release')
    v.need(admission['source_manifest_sha256'] == v.SOURCE_SHA, 'exact new-word source')
    v.need({int(r): n for r, n in admission['profile'].items()} == v.PROFILE, 'complete actual composed profile')
    arithmetic = v.calculate(include_owners=False)
    v.need(Q(admission['kappa']) == Q(receipt['kappa_decimal']) == arithmetic['kappa'], 'exact composed endpoint')
    v.need(Q(admission['kappa']) > Q(v.read(source / 'CLAIM.json')['kappa']), 'strict improvement over PR3042')
    v.need(admission['fill_sha256'] == v.sha(work / 'COMPOSED-FILL.json.gz'), 'actual admitted T148 fill')
    v.need(admission['release_receipt_sha256'] == v.sha(work / 'run/candidate/release/RELEASE-RECEIPT.json'),
           'terminal release receipt bound by admission')
    native = v.read(work / 'run/native/NATIVE-RECEIPT.json')
    v.need(native['fresh_current_provider_count'] == 2 and native['manifest_sha256'] == v.SOURCE_SHA,
           'both changed native providers freshly verified')
    harness.authenticate_tree(source)
    harness.authenticate_tree(work / 'run/source-edits')
    result = dict(status='PASS_T148_CARRIER_SKIPS_COMPLETE_RELEASE',
                  **{k: str(arithmetic[k]) for k in ['kappa', 'complex_lower', 'previous', 'gain']},
                  source_manifest_sha256=v.SOURCE_SHA, profile=admission['profile'],
                  fill_sha256=admission['fill_sha256'], native_receipt_sha256=admission['native_receipt_sha256'],
                  release_sha256=admission['release_receipt_sha256'],
                  baseline_result_sha256=v.sha(baseline / 'RESULT.json'),
                  package_manifest_sha256=receipt['manifest_sha256'], stages=stages,
                  native_scope='Two fresh changed providers; unchanged retained bootstrap explicitly authenticated and reused.')
    harness.save(work / 'RESULT.json', result)
    print(result['status'], result['kappa'], flush=True)


if __name__ == '__main__':
    main()

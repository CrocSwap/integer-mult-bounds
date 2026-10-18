#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Portable complete T248 replay from exact read-only PR2833 source.

Default: four fresh native chains and retained parent, then full admission.
Explicit --prepared-native reuses authenticated native evidence; this is labelled.
Install requirements-reproduction.txt first. No dependency/source guard is patched.
"""
import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from materialize_source import authenticate_source, MANIFEST_SHA, need

HERE = Path(__file__).resolve().parent
EXPECTED_KAPPA = Fraction('0.001718658508304930004819') - Fraction(1, 10**46) - Fraction(1, 10**70)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def commands(source, work, jobs, prepared_native=None):
    native = prepared_native if prepared_native is not None else work / 'native'
    helper = HERE / 'vendor/pr2839'
    result = []
    if prepared_native is None:
        result.append(('fresh-native', [sys.executable, '-B',
                       str(HERE / 'prepare_dirtentry_native_portable.py'),
                       '--source', str(source), '--out', str(native), '--jobs', str(jobs)]))
    result.append(('complete-admission', [sys.executable, '-B',
                   str(HERE / 'admit_dirtentry_replica_latest.py'),
                   '--source', str(source), '--fill', str(HERE / 'FILL.json.gz'),
                   '--order', str(HERE / 'ORDER.json'), '--dispatch', str(HERE / 'DISPATCH.json'),
                   '--native-cache', str(native / 'native-cache'),
                   '--native-receipt', str(native / 'NATIVE-RECEIPT.json'),
                   '--work', str(work / 'candidate'), '--replica-helper-dir', str(helper),
                   '--reconstructor', str(helper / 'reconstruct_replica.py'),
                   '--blocknorm-checker', str(helper / 'blocknorm_certificate.py'),
                   '--comparison-claim', str(HERE / 'sources/PR2843-CLAIM.json'),
                   '--source-profile', 'pr2833', '--comparison-profile', 'pr2843',
                   '--jobs', str(jobs)]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Exact immutable PR2833 package')
    parser.add_argument('--work', type=Path, required=True, help='Fresh external output directory')
    parser.add_argument('--jobs', type=int, default=4, choices=range(1, 5))
    parser.add_argument('--prepared-native', type=Path,
                        help='Explicit reuse of a completed source-bound native preparation')
    parser.add_argument('--dry-run', action='store_true',
                        help='Authenticate inputs and print argv; do not run or create output')
    args = parser.parse_args()
    need(not sys.flags.optimize, 'assertions must be enabled')
    need(not args.source.is_symlink(), 'source must not be a symlink')
    source, work = args.source.resolve(), args.work.resolve()
    need(not work.exists() and not work.is_symlink(), 'fresh work directory required')
    need(not work.is_relative_to(source) and not source.is_relative_to(work),
         'source and work must be disjoint')
    need(not work.is_relative_to(HERE) and not HERE.is_relative_to(work),
         'published package and work must be disjoint')
    pins = authenticate_source(source)
    prepared = args.prepared_native.resolve() if args.prepared_native else None
    if prepared is not None:
        need(prepared.is_dir() and not work.is_relative_to(prepared)
             and not prepared.is_relative_to(work), 'native reuse and work must be disjoint')
        result = read(prepared / 'RESULT.json')
        receipt = read(prepared / 'NATIVE-RECEIPT.json')
        need(result['status'] == 'PASS_PR2833_FRESH_NATIVE_PREPARATION'
             and result['source_manifest_sha256'] == MANIFEST_SHA
             and result['native_receipt_sha256'] == sha(prepared / 'NATIVE-RECEIPT.json'),
             'completed prepared-native result binding')
        need(receipt['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
             and receipt['source_commit'] == 'pr2833-dirtentry'
             and receipt['manifest_sha256'] == MANIFEST_SHA,
             'prepared-native source binding')
        # The unchanged admission driver checks the entire cache and every stage.
    recipe = commands(source, work, args.jobs, prepared)
    if args.dry_run:
        print(json.dumps({'status': 'PREFLIGHT_ONLY_NOT_A_REPLAY',
                          'explicit_native_reuse': prepared is not None,
                          'commands': [{'stage': name, 'argv': argv} for name, argv in recipe]},
                         sort_keys=True, indent=2))
        return
    claim_path = HERE / 'CLAIM.json'
    claim = read(claim_path)
    need(Fraction(claim['kappa']) == EXPECTED_KAPPA, 'stored exact T248 headline')
    claim_hash = sha(claim_path)
    work.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONINTMAXSTRDIGITS='0', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for name in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(name, None)
    stages = []
    for name, argv in recipe:
        start = time.monotonic()
        log = work / (name + '.log')
        with log.open('w', encoding='utf-8') as output:
            process = subprocess.run(argv, cwd=work, env=env, stdin=subprocess.DEVNULL,
                                     stdout=output, stderr=subprocess.STDOUT)
        stages.append({'stage': name, 'argv': argv, 'exit_code': process.returncode,
                       'seconds': time.monotonic() - start, 'log_sha256': sha(log)})
        (work / 'STAGES.json').write_text(json.dumps(stages, sort_keys=True, indent=2) + '\n')
        need(process.returncode == 0, 'failed ' + name + '; inspect ' + str(log))
        print('PASS', name, flush=True)
    result = read(work / 'candidate/RESULT.json')
    release = read(work / 'candidate/release/RELEASE-RECEIPT.json')
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and release['status'] == 'PASS_RELEASE', 'complete source-bound release statuses')
    need(Fraction(result['kappa']) == Fraction(release['kappa_decimal'])
         == Fraction(claim['kappa']) == EXPECTED_KAPPA, 'exact stored/replayed T248 target')
    need(result['release_receipt_sha256'] == sha(work / 'candidate/release/RELEASE-RECEIPT.json')
         and result['package_manifest_sha256'] == release['manifest_sha256'],
         'release receipt and generated package binding')
    need(authenticate_source(source) == pins and sha(claim_path) == claim_hash,
         'read-only source and published claim unchanged')
    final = {'status': 'PASS_T248_PORTABLE_COMPLETE_REPLAY', 'kappa': result['kappa'],
             'explicit_prepared_native_reuse': prepared is not None,
             'fresh_native_preparation_this_invocation': prepared is None,
             'stored_claim_sha256': claim_hash, 'candidate_result_sha256': sha(work / 'candidate/RESULT.json'),
             'stages': stages,
             'scope': 'Conditional finite supplier and modern outer release; inherited all-size assumptions remain.'}
    (work / 'RESULT.json').write_text(json.dumps(final, sort_keys=True, indent=2) + '\n')
    print('PASS_T248_PORTABLE_COMPLETE_REPLAY', result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

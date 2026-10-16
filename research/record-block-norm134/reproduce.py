#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reproduce the complete source-bound block-norm T134 construction.

Default: four fresh native chains, fresh retained parent and complete changed
admission. Explicit --prepared-native authenticates and reuses all native files.
"""
import argparse
from fractions import Fraction
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from verify_sources import HERE, ROOT, check, need, read, sha, tree

SOURCE_HEAD = 'e9307b48d7d1b690939935ecef0f8e524e6d92f4'
SOURCE_MANIFEST = 'c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
PARENT_MANIFEST = 'e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4'
NATIVE_PROTOCOL = 'cb32e36f3e435652b7fab857c94e0dbb925b56ce7bb5daeecc223b0fc6993012'


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2)+'\n', encoding='utf8', newline='\n')


def native_protocol():
    utility = ROOT/'research/replica-tail-gain/portable_prepare_native.py'
    need(sha(utility) == NATIVE_PROTOCOL, 'native protocol implementation')
    spec = importlib.util.spec_from_file_location('pinned_native_protocol', utility)
    auth = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auth)
    return auth


def child_environment(work):
    # The same process-scoped LF adapter must reach admission and its children,
    # including the explicit prepared-native path, on every supported platform.
    adapter = work/'process-lf-adapter'
    adapter.mkdir()
    (adapter/'sitecustomize.py').write_text(native_protocol().LF_SHIM,
                                          encoding='utf8', newline='\n')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONINTMAXSTRDIGITS='0', PYTHONUTF8='1',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    env['PYTHONPATH'] = str(adapter)+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    for name in ('PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD'):
        env.pop(name, None)
    return env


def authenticate_native(native):
    result = read(native/'RESULT.json')
    receipt = read(native/'NATIVE-RECEIPT.json')
    source, cache = native/'source', native/'native-cache'
    need(result['status'] == 'PASS_PORTABLE_NATIVE_PREPARATION' and
         result['native_receipt_sha256'] == sha(native/'NATIVE-RECEIPT.json'), 'complete native preparation receipt')
    need(receipt['status'] == 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE' and
         receipt['source_commit'] == SOURCE_HEAD and receipt['manifest_sha256'] == SOURCE_MANIFEST, 'native source/protocol binding')
    need(result['source_file_count'] == 541 and sha(source/'MANIFEST.json') == SOURCE_MANIFEST and
         len(read(source/'MANIFEST.json')) == 541 and tree(source, ('MANIFEST.json',)) == read(source/'MANIFEST.json'), 'complete exact native source')
    need(tree(cache) == receipt['cache_files'], 'complete exact native cache')
    need(receipt['fresh_current_provider_count'] == 2 and
         receipt['fresh_retained_native_count'] + receipt['reused_retained_native_count'] == 2 and
         receipt['fresh_retained_parent'] != receipt['reused_retained_parent'], 'explicit complete native coverage')
    auth = native_protocol()
    for tag in ('base','extra'):
        word = source/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'
        need(receipt['providers'][tag]['word_sha256'] == sha(word), 'current word binding')
        entry = cache/sha(word)
        auth.bind_native(entry, word)
        need(tree(entry, ('CACHE.json',)) == receipt['providers'][tag]['complete_native_files'], 'complete current native files')
    old = source/'vendor/pr1297'
    need(sha(old/'MANIFEST.json') == PARENT_MANIFEST and
         tree(old, ('MANIFEST.json',)) == read(old/'MANIFEST.json'), 'complete retained parent source')
    retained = {tag:old/name for tag,name in
                (('base','gauge44-word.json.gz'),('extra','extra-word.json.gz'))}
    for word in retained.values():
        auth.bind_native(cache/sha(word), word)
    parent_dir = cache/'_receipts'/PARENT_MANIFEST
    need(sha(parent_dir/'RECEIPT.json') == receipt['retained_parent_receipt_sha256'], 'retained parent receipt binding')
    parent_receipt = read(parent_dir/'RECEIPT.json')
    need(parent_receipt['schema'] == 'parent-receipt/1' and
         parent_receipt['vendor_manifest_sha256'] == PARENT_MANIFEST and
         parent_receipt['claim_sha256'] == sha(old/'CLAIM.json') and
         parent_receipt['words'] == {tag:sha(word) for tag,word in retained.items()}, 'retained parent source/claim/word binding')
    need(set(parent_receipt['files']) == {'RESULT.json','STAGES.json'} and
         set(tree(parent_dir)) == {'RECEIPT.json','RESULT.json','STAGES.json'}, 'complete retained parent receipt files')
    need(all(sha(parent_dir/name) == digest for name,digest in parent_receipt['files'].items()), 'retained parent receipt file hashes')
    parent_stages = read(parent_dir/'STAGES.json')
    expected_stages = {name+'-'+tag for tag in ('base','extra') for name in
                       ('literal-word','independent-local','fusion-controls','x54-controls',
                        'kernel543-controls','kernel-controls','leaver-premise')}
    expected_stages.update(('literal-construct','strict-global'))
    need(len(parent_stages) == 16 and
         {stage['name'] for stage in parent_stages} == expected_stages and
         all(stage['exit_code'] == 0 for stage in parent_stages), 'sixteen successful retained parent stages')
    parent = read(parent_dir/'RESULT.json')
    need(parent['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and
         parent['kappa'] == read(old/'CLAIM.json')['kappa'] and parent['stages'] == parent_stages and
         parent['base_native_reuse'] is True and parent['extra_native_reuse'] is True, 'retained parent PASS/claim/stage binding')
    # Complete admission independently recounts canonical programs and primitive
    # work and checks the changed supplier, reserve, and outer construction.
    return dict(native_receipt_sha256=sha(native/'NATIVE-RECEIPT.json'),
                result_sha256=sha(native/'RESULT.json'),source_manifest_sha256=SOURCE_MANIFEST,
                cache_files=receipt['cache_files'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--source', type=Path, help='Optional exact541-file PR2833 source; default is the merged predecessor package.')
    ap.add_argument('--prepared-native', type=Path, help='Explicit reuse of a completely authenticated PR2833 native preparation.')
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    need(not sys.flags.optimize and 1 <= a.jobs <= 80, 'enabled assertions and1..80jobs')
    pins = check()
    claim = read(HERE/'CLAIM.json')
    previous = read(HERE/'PR2843-CLAIM.json')
    need(Fraction(previous['kappa']) == Fraction(previous.get('kappa_rational',previous['kappa'])) == Fraction(previous['kappa_decimal']), 'all incumbent digits bound')
    work = a.work.resolve()
    need(not work.exists() and not work.is_relative_to(ROOT), 'fresh output outside repository')
    for p in (a.source,a.prepared_native):
        need(p is None or not work.is_relative_to(p.resolve()), 'output/read-only input separation')
    work.mkdir(parents=True)
    env = child_environment(work)
    stages, started = [], time.monotonic()

    def run(name, script, *args):
        command = [sys.executable,'-B',str(script),*map(str,args)]
        log, begin = work/(name+'.log'), time.monotonic()
        with log.open('w',encoding='utf8',newline='\n') as f:
            result = subprocess.run(command, env=env, cwd=work, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT)
        stages.append(dict(name=name,command=command,exit_code=result.returncode,seconds=time.monotonic()-begin,
                           script_sha256=sha(script),log_sha256=sha(log)))
        write(work/'STAGES.json', stages)
        need(result.returncode == 0, 'failed '+name+'; see '+str(log))
        print('PASS',name,flush=True)

    if a.prepared_native:
        native = a.prepared_native.resolve()
    else:
        native = work/'native'
        args = ['--work',native,'--jobs',min(4,a.jobs)]
        if a.source:
            args += ['--source',a.source.resolve()]
        run('fresh-native-preparation',HERE/'prepare_native.py',*args)
    binding = authenticate_native(native)
    run('native-block-premises',HERE/'check_native_norm.py','--native',native,'--out',work/'NATIVE-PREMISES.json')
    run('complete-admission',HERE/'admit.py',
        '--source',native/'source','--native-cache',native/'native-cache',
        '--native-receipt',native/'NATIVE-RECEIPT.json','--fill',HERE/'data/FILL.json.gz',
        '--order',HERE/'data/ORDER.json','--dispatch',HERE/'data/DISPATCH.json',
        '--work',work/'admission','--replica-helper-dir',HERE,
        '--reconstructor',ROOT/'research/replica-tail-gain/reconstruct_replica.py',
        '--comparison-claim',HERE/'PR2843-CLAIM.json',
        '--source-profile','pr2833','--comparison-profile','pr2843',
        '--blocknorm-checker',HERE/'blocknorm_certificate.py','--jobs',a.jobs)
    result = read(work/'admission/RESULT.json')
    need(result['status'] == 'PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE', 'complete finite release')
    need(result['replicas'] == claim['replicas'] and Fraction(result['kappa']) == Fraction(claim['kappa']) > Fraction(previous['kappa']), 'exact new headline and strict gain')
    need(authenticate_native(native) == binding and check() == pins, 'no input drift')
    report = dict(status='PASS_BLOCK_NORM_T134_COMPLETE_RELEASE',replicas=claim['replicas'],kappa=result['kappa'],
                  explicit_native_reuse=bool(a.prepared_native),fresh_native_preparation=not bool(a.prepared_native),
                  native_binding=binding,candidate_result_sha256=sha(work/'admission/RESULT.json'),
                  release_receipt_sha256=result['release_receipt_sha256'],stages=stages,seconds=time.monotonic()-started,
                  scope='Conditional finite supplier and modern outer release. Inherited all-size compiler/source-access/hosting/precision/tape/recovery/BIT/analytic hypotheses remain.')
    write(work/'RESULT.json', report)
    print(report['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

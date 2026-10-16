#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fresh PR2833 native preparation with optional authenticated retained reuse.

Uses the unchanged PR2824 native receipt protocol and retains its attribution.
No full supplier or outer admission is inferred from this preparation.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import threading
import time

HEAD = 'e9307b48d7d1b690939935ecef0f8e524e6d92f4'
MANIFEST = 'c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
UTILITY = 'cb32e36f3e435652b7fab857c94e0dbb925b56ce7bb5daeecc223b0fc6993012'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=Path(__file__).resolve().parent.parent/'gmx-t74-borrow43-handoff')
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--reuse-retained-baseline', type=Path)
    ap.add_argument('--utilities', type=Path, default=Path(__file__).resolve().parent.parent/'replica-tail-gain/portable_prepare_native.py')
    ap.add_argument('--jobs', type=int, choices=range(1, 5), default=4)
    a = ap.parse_args()
    need(not sys.flags.optimize, 'enabled assertions required')
    sys.dont_write_bytecode = True
    need(sha(a.utilities) == UTILITY, 'immutable predecessor native protocol')
    spec = importlib.util.spec_from_file_location('retained_native_protocol', a.utilities)
    u = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(u)
    source_input, work = a.source.resolve(), a.work.resolve()
    baseline = a.reuse_retained_baseline.resolve() if a.reuse_retained_baseline else None
    need(not work.exists() and not work.is_relative_to(source_input) and
         not work.is_relative_to(Path(__file__).resolve().parent) and
         (baseline is None or not work.is_relative_to(baseline)), 'fresh external work')
    need(sha(source_input/'MANIFEST.json') == MANIFEST, 'exact PR2833 source manifest')
    pins = u.read(source_input/'MANIFEST.json')
    need(len(pins) == 541 and u.tree(source_input, ('MANIFEST.json',)) == pins, 'complete PR2833 source inventory')
    versions = {k: str(importlib.import_module(k).__version__) for k in ('numpy','scipy','sympy','mpmath')}
    need(versions == {'numpy':'1.26.4','scipy':'1.15.3','sympy':'1.14.0','mpmath':'1.3.0'}, 'explicit Python3.12 dependency pins')
    work.mkdir(parents=True)
    source = work/'source'
    shutil.copytree(source_input, source)
    cache = work/'native-cache'
    cache.mkdir()
    old = source/'vendor/pr1297'
    retained = {tag:old/name for tag,name in [('base','gauge44-word.json.gz'),('extra','extra-word.json.gz')]}
    reuse = u.reuse_retained(baseline, source, cache, retained) if baseline else None
    if reuse:
        u.write(work/'RETAINED-REUSE.json', reuse)
    words = {tag:source/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz' for tag in ('base','extra')}
    runtime = work/'runtime-adapter'
    runtime.mkdir()
    (runtime/'sitecustomize.py').write_text(u.LF_SHIM, encoding='utf8', newline='\n')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               PYTHONPATH=str(runtime), PYTHONPYCACHEPREFIX=str(work/'unused-pycache-prefix'),
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1', BW_IDLE='0')
    for name in ('PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD'):
        env.pop(name, None)
    u.write(work/'ENVIRONMENT.json', dict(python=platform.python_version(),versions=versions,
            jobs=a.jobs,preparer_sha256=sha(Path(__file__)),utility_sha256=UTILITY,
            current_native_fresh=2,retained_native_fresh=0 if reuse else 2,
            retained_native_reused=2 if reuse else 0,retained_parent_reused=bool(reuse)))
    stages, mutex = [], threading.Lock()
    started = time.monotonic()
    retained_driver = None
    if not reuse:
        layout = work/'retained-layout'
        layout.mkdir()
        with tarfile.open(old/'upstream-layout.tar.gz') as archive:
            for member in archive.getmembers():
                u.safe(member.name)
                need(member.isfile(), 'regular retained archive member')
            archive.extractall(layout, filter='data')
        retained_driver = layout/'joint1148-round45/source/research/k8-eight-ends/replay_native.py'
        need(retained_driver.is_file(), 'retained native driver')
    jobs = dict(words)
    if not reuse:
        jobs.update({'retained-'+tag:word for tag,word in retained.items()})

    def fresh(tag):
        word = jobs[tag]
        entry = cache/sha(word)
        # PR2833's current verifier selects PR2768's exact sparse native driver.
        # Its frozen legacy driver predates the repaired centre mutation fixture.
        is_retained = tag.startswith('retained-')
        driver = retained_driver if is_retained else source/'new/fastnative/run_native.py'
        fast = None if is_retained else work/('fresh-fast-'+tag)
        command = [sys.executable,'-B',str(driver),str(word),str(entry if is_retained else fast)]
        begin = time.monotonic()
        log = work/f'native-{tag}.log'
        with log.open('w', encoding='utf8', newline='\n') as f:
            done = subprocess.run(command, env=env, cwd=work, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT)
        with mutex:
            stages.append(dict(name='native-'+tag,command=command,exit_code=done.returncode,
                               seconds=time.monotonic()-begin,script_sha256=sha(driver),log_sha256=sha(log)))
            u.write(work/'STAGES.json', stages)
        need(done.returncode == 0, 'native failure: '+str(log))
        if not is_retained:
            fresh_result = u.read(fast/'RESULT.json')
            need(fresh_result['status'] == 'PASS_COMPLETE_T74_NATIVE_REPLAY' and
                 fresh_result['engine'] == 'sparse' and fresh_result['word_sha256'] == sha(word),
                 'complete fresh sparse-native receipt')
            shutil.copytree(fast/'native', entry)
            shutil.copy2(fast/'RESULT.json', entry/'FRESH-REPLAY.json')
            shutil.copy2(fast/'COMMANDS.json', entry/'FRESH-COMMANDS.json')
        u.bind_native(entry, word)
        u.write(entry/'CACHE.json', dict(word_sha256=sha(word),files=u.tree(entry)))
        print('PASS_FRESH_NATIVE', tag, flush=True)

    with ThreadPoolExecutor(max_workers=a.jobs) as pool:
        list(pool.map(fresh, jobs))
    receipts = cache/'_receipts'/sha(old/'MANIFEST.json')
    if not reuse:
        parent_work = work/'retained-parent'
        command = [sys.executable,'-B',str(old/'verify.py'),'--work',str(parent_work),
                   '--base-native-from',str(cache/sha(retained['base'])),
                   '--extra-native-from',str(cache/sha(retained['extra']))]
        log = work/'retained-parent.log'
        begin = time.monotonic()
        with log.open('w', encoding='utf8', newline='\n') as f:
            done = subprocess.run(command, env=env, cwd=work, stdin=subprocess.DEVNULL, stdout=f, stderr=subprocess.STDOUT)
        stages.append(dict(name='retained-parent',command=command,exit_code=done.returncode,
                           seconds=time.monotonic()-begin,script_sha256=sha(old/'verify.py'),log_sha256=sha(log)))
        u.write(work/'STAGES.json', stages)
        need(done.returncode == 0, 'retained parent failure: '+str(log))
        parent = u.read(parent_work/'RESULT.json')
        parent_stages = u.read(parent_work/'STAGES.json')
        need(len(parent_stages) == 16 and all(s['exit_code'] == 0 for s in parent_stages), 'sixteen complete retained stages')
        need(parent['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and
             parent['kappa'] == u.read(old/'CLAIM.json')['kappa'], 'retained parent claim')
        receipts.mkdir(parents=True)
        for name in ('RESULT.json','STAGES.json'):
            shutil.copy2(parent_work/name, receipts/name)
        u.write(receipts/'RECEIPT.json', dict(schema='parent-receipt/1',vendor_manifest_sha256=sha(old/'MANIFEST.json'),
                claim_sha256=sha(old/'CLAIM.json'),words={tag:sha(word) for tag,word in retained.items()},
                files={name:sha(receipts/name) for name in ('RESULT.json','STAGES.json')}))
        print('PASS_FRESH_RETAINED_PARENT', flush=True)
    need(u.tree(source, ('MANIFEST.json',)) == pins and sha(source/'MANIFEST.json') == MANIFEST, 'source unchanged')
    need(u.tree(source_input, ('MANIFEST.json',)) == pins, 'input source unchanged')
    receipt = dict(status=u.PROTOCOL_STATUS,source_commit=HEAD,manifest_sha256=MANIFEST,
                   providers={tag:dict(word_sha256=sha(word),complete_native_files=u.tree(cache/sha(word),('CACHE.json',))) for tag,word in words.items()},
                   retained_parent_receipt_sha256=sha(cache/'_receipts'/sha(old/'MANIFEST.json')/'RECEIPT.json'),
                   cache_files=u.tree(cache),fresh_current_provider_count=2,fresh_retained_native_count=0 if reuse else 2,
                   reused_retained_native_count=2 if reuse else 0,fresh_retained_parent=not bool(reuse),reused_retained_parent=bool(reuse),
                   retained_reuse_receipt_sha256=sha(work/'RETAINED-REUSE.json') if reuse else None)
    u.write(work/'NATIVE-RECEIPT.json', receipt)
    need(u.tree(cache) == receipt['cache_files'], 'complete cache binding')
    u.write(work/'RESULT.json', dict(status='PASS_PORTABLE_NATIVE_PREPARATION',source_file_count=541,
            source_commit=HEAD,manifest_sha256=MANIFEST,native_receipt_sha256=sha(work/'NATIVE-RECEIPT.json'),
            fresh_current_provider_count=2,fresh_retained_native_count=0 if reuse else 2,reused_retained_native_count=2 if reuse else 0,
            fresh_retained_parent=not bool(reuse),reused_retained_parent=bool(reuse),seconds=time.monotonic()-started,
            scope='Fresh PR2833 changed providers. Retained native/parent checks are fresh by default or explicitly authenticated reuse. No global/outer admission.'))
    print('PASS_PORTABLE_NATIVE_PREPARATION', flush=True)


if __name__ == '__main__':
    main()

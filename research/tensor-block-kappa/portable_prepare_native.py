#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate PR2802 and prepare native receipts, without a redundant T74 admission.

Default: four fresh native chains and a fresh retained-parent check. Explicit
--reuse-retained-baseline reuses only unchanged, completely hash-bound retained
chains and their retained-parent receipt. Current providers always run freshly.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tarfile
import threading
import time

HEAD = '17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd'
DOWNLOAD_SHA = 'fae7e9161707d3627c7ba444543b1bdd0d736df57b8495ea112bb221a2693497'
DERIVED_SHA = '9c72b4301057a6c204c40bb6584eb74b779e06618bcd98d706d726c3e2c92451'
PROTOCOL_STATUS = 'PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE'
STEPS = ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']
LF_SHIM = """from pathlib import Path
_original_write_text = Path.write_text
def _task_write_text(self, data, encoding=None, errors=None, newline=None):
    return _original_write_text(self, data, encoding=encoding, errors=errors,
                                newline='\\n' if newline is None else newline)
Path.write_text = _task_write_text
"""


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n',
                    encoding='utf-8', newline='\n')


def safe(name):
    p = PurePosixPath(name)
    need(isinstance(name, str) and p.parts and not p.is_absolute() and
         '..' not in p.parts and '\\' not in name and p.as_posix() == name,
         'unsafe path: ' + str(name))


def tree(root, exclude=()):
    result = {}
    for p in sorted(root.rglob('*')):
        need(not p.is_symlink(), 'symlink in authenticated tree: ' + str(p))
        name = p.relative_to(root).as_posix()
        if p.is_file() and name not in exclude:
            result[name] = sha(p)
    return result


def authenticate_vendor(vendor):
    manifest = vendor / 'DOWNLOAD-MANIFEST.json'
    need(sha(manifest) == DOWNLOAD_SHA, 'pinned download manifest')
    data = read(manifest)
    need(data['head'] == HEAD and len(data['files']) == 124, '124 pinned vendor files')
    expected = {}
    for item in data['files']:
        name = item['path']
        safe(name)
        need(name not in expected, 'duplicate vendor path')
        body = (vendor / name).read_bytes()
        need(len(body) == item['bytes'] and hashlib.sha256(body).hexdigest() == item['sha256'],
             'vendor SHA256/size: ' + name)
        blob = hashlib.sha1(('blob ' + str(len(body)) + '\0').encode() + body).hexdigest()
        need(blob == item['git_blob'] and blob.startswith(item['diff_blob']), 'vendor Git blob: ' + name)
        expected[name] = item['sha256']
    need(tree(vendor, ('DOWNLOAD-MANIFEST.json',)) == expected, 'complete vendor inventory')
    return expected


def source_guard(source):
    need(sha(source / 'MANIFEST.json') == DERIVED_SHA, 'derived source manifest')
    pins = read(source / 'MANIFEST.json')
    need(len(pins) == 506 and tree(source, ('MANIFEST.json',)) == pins,
         'complete506-file derived source inventory')
    return pins


def bind_native(entry, word):
    need(gzip.decompress((entry / 'local/FULL-WORD.json.gz').read_bytes()) ==
         gzip.decompress(word.read_bytes()), 'complete native word binding')
    stages = read(entry / 'STEPS.json')
    need([s['step'] for s in stages] == STEPS and all(s['exit_code'] == 0 for s in stages),
         'five successful native stages')


def reuse_retained(baseline, source, cache, retained):
    prior = read(baseline / 'NATIVE-RECEIPT.json')
    need(prior['status'] == PROTOCOL_STATUS, 'completed baseline native protocol')
    previous_source = baseline / 'source'
    need(sha(previous_source / 'MANIFEST.json') == prior['manifest_sha256'] and
         tree(previous_source, ('MANIFEST.json',)) == read(previous_source / 'MANIFEST.json'),
         'complete baseline source inventory')
    oldcache = baseline / 'native-cache'
    need(tree(oldcache) == prior['cache_files'], 'complete baseline cache inventory')
    old = source / 'vendor/pr1297'
    need(tree(old) == tree(previous_source / 'vendor/pr1297'), 'exact retained vendor source identity')
    records = {}
    for tag, word in retained.items():
        digest = sha(word)
        entry = oldcache / digest
        expected = {k[len(digest)+1:]: v for k, v in prior['cache_files'].items()
                    if k.startswith(digest + '/')}
        need(expected and tree(entry) == expected, 'retained native exact pins: ' + tag)
        bind_native(entry, word)
        shutil.copytree(entry, cache / digest)
        need(tree(cache / digest) == expected, 'retained native exact copy: ' + tag)
        records[tag] = dict(word_sha256=digest, files=expected)
    pm = sha(old / 'MANIFEST.json')
    relative = '_receipts/' + pm
    expected = {k[len(relative)+1:]: v for k, v in prior['cache_files'].items()
                if k.startswith(relative + '/')}
    receipt_dir = oldcache / relative
    need(expected and tree(receipt_dir) == expected, 'retained parent exact pins')
    receipt = read(receipt_dir / 'RECEIPT.json')
    need(receipt['schema'] == 'parent-receipt/1' and
         receipt['vendor_manifest_sha256'] == pm and
         receipt['claim_sha256'] == sha(old / 'CLAIM.json') and
         receipt['words'] == {tag: sha(w) for tag, w in retained.items()},
         'retained parent source/claim/word binding')
    need(set(receipt['files']) == {'RESULT.json', 'STAGES.json'}, 'complete retained parent receipt files')
    parent_stages = read(receipt_dir / 'STAGES.json')
    need(len(parent_stages) == 16 and all(s['exit_code'] == 0 for s in parent_stages),
         'sixteen successful retained parent stages')
    need(all(sha(receipt_dir / name) == digest for name, digest in receipt['files'].items()),
         'retained parent receipt file hashes')
    parent = read(receipt_dir / 'RESULT.json')
    need(parent['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and
         parent['kappa'] == read(old / 'CLAIM.json')['kappa'], 'retained parent PASS/claim')
    shutil.copytree(receipt_dir, cache / relative)
    need(tree(cache / relative) == expected, 'retained parent exact copy')
    return dict(status='PASS_EXACT_HASH_BOUND_RETAINED_REUSE',
                baseline_native_receipt_sha256=sha(baseline / 'NATIVE-RECEIPT.json'),
                baseline_source_manifest_sha256=prior['manifest_sha256'],
                baseline_source_commit=prior['source_commit'],
                retained_vendor_manifest_sha256=pm, native_entries=records,
                retained_parent_receipt_sha256=sha(cache / relative / 'RECEIPT.json'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work', type=Path, required=True, help='Fresh external output directory.')
    ap.add_argument('--source', type=Path, help='Exact original491-file PR2679 source; otherwise use pinned upstream download.')
    ap.add_argument('--vendor-frontier', type=Path, default=Path(__file__).resolve().parent / 'vendor/frontier')
    ap.add_argument('--jobs', type=int, choices=range(1, 5), default=4)
    ap.add_argument('--reuse-retained-baseline', type=Path,
                    help='Explicit unchanged retained2-native/parent reuse from a completed baseline.')
    ap.add_argument('--prepare-only', action='store_true',
                    help='Authenticate/copy source and optional retained reuse; do not run native checks or issue a native receipt.')
    args = ap.parse_args()
    need(not sys.flags.optimize, 'assertions must remain enabled')
    sys.dont_write_bytecode = True
    vendor = args.vendor_frontier.resolve()
    authenticate_vendor(vendor)
    versions = {name: str(importlib.import_module(name).__version__)
                for name in ('numpy', 'sympy', 'scipy', 'mpmath')}
    pinned = dict(line.split('==') for line in (vendor / 'requirements.txt').read_text().splitlines() if line)
    need(versions == pinned, 'install the exact pinned requirements.txt in the invoking Python environment')
    work = args.work.resolve()
    need(not work.exists(), 'fresh work directory required')
    need(not work.is_relative_to(Path(__file__).resolve().parent) and not work.is_relative_to(vendor),
         'external work directory required')
    for p in (args.source, args.reuse_retained_baseline):
        need(p is None or (p.is_dir() and not work.is_relative_to(p.resolve())), 'input/work separation')
    work.mkdir(parents=True)
    lockpath = work / 'native.lock'
    with lockpath.open('x', encoding='utf-8') as lock:
        lock.write(str(os.getpid()) + '\n')
    successful = False
    try:
        spec = importlib.util.spec_from_file_location('_pinned_full_replay', vendor / 'full_replay.py')
        upstream = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(upstream)
        write(work / 'INPUT-BINDING.json', dict(upstream_head=HEAD, download_manifest_sha256=DOWNLOAD_SHA,
              vendor_files=124, preparer_sha256=sha(Path(__file__)),
              source_pins_sha256=sha(vendor / 'SOURCE-FILES.json'), overlay_pins_sha256=sha(vendor / 'OVERLAY-PINS.json')))
        source = work / 'source'
        pins = read(vendor / 'SOURCE-FILES.json')
        upstream.source_copy(args.source.resolve() if args.source else None, source, pins, args.jobs)
        overlay = read(vendor / 'OVERLAY-PINS.json')
        need(sha(source / 'MANIFEST.json') == overlay['original_manifest_sha256'], 'original source manifest')
        need(sha(vendor / 'DERIVATIVE-OVERLAY.tar.gz') == overlay['archive_sha256'], 'overlay archive')
        with tarfile.open(vendor / 'DERIVATIVE-OVERLAY.tar.gz') as archive:
            members = archive.getmembers()
            need(set(m.name for m in members) == set(overlay['files']) and len(members) == len(overlay['files']), 'exact overlay paths')
            for member in members:
                safe(member.name)
                need(member.isfile(), 'regular overlay member')
                body = archive.extractfile(member).read()
                need(hashlib.sha256(body).hexdigest() == overlay['files'][member.name], 'overlay member hash')
                target = source / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
        need(overlay['derived_manifest_sha256'] == DERIVED_SHA, 'pinned derived identity')
        source_guard(source)
        cache = work / 'native-cache'
        cache.mkdir()
        old = source / 'vendor/pr1297'
        words = {tag: source / ('new/borrow/words/BORROW-WORD-43' + tag + '.json.gz') for tag in ('base', 'extra')}
        retained = {tag: old / name for tag, name in (('base', 'gauge44-word.json.gz'), ('extra', 'extra-word.json.gz'))}
        reuse = None
        if args.reuse_retained_baseline:
            reuse = reuse_retained(args.reuse_retained_baseline.resolve(), source, cache, retained)
            write(work / 'RETAINED-REUSE.json', reuse)
        runtime = work / 'runtime-adapter'
        runtime.mkdir()
        shim = runtime / 'sitecustomize.py'
        shim.write_text(LF_SHIM, encoding='utf-8', newline='\n')
        inherited = [str(Path(p or os.getcwd()).resolve()) for p in sys.path]
        inherited.extend(os.environ.get('PYTHONPATH', '').split(os.pathsep))
        paths = list(dict.fromkeys([str(runtime), *[p for p in inherited if p]]))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
                   OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', BW_IDLE='0', PYTHONPATH=os.pathsep.join(paths))
        for name in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
            env.pop(name, None)
        write(work / 'ENVIRONMENT.json', dict(python=platform.python_version(), versions=versions,
              lf_adapter_sha256=sha(shim), jobs=args.jobs, planned_fresh_current_provider_count=2,
              planned_fresh_retained_native_count=0 if reuse else 2,
              reused_retained_native_count=2 if reuse else 0,
              reused_retained_parent=bool(reuse), scope='Task process environment; no global configuration changes.'))
        if args.prepare_only:
            source_guard(source)
            authenticate_vendor(vendor)
            write(work / 'RESULT.json', dict(status='PASS_AUTHENTICATED_NATIVE_SOURCE_PREPARATION_ONLY',
                  source_file_count=506, manifest_sha256=DERIVED_SHA, native_receipt_issued=False,
                  explicit_retained_reuse=bool(reuse)))
            successful = True
            print('PASS_AUTHENTICATED_NATIVE_SOURCE_PREPARATION_ONLY', flush=True)
            return
        stages = []
        mutex = threading.Lock()
        started = time.monotonic()

        def run(name, script, *arguments):
            begin = time.monotonic()
            log = work / (name + '.log')
            command = [sys.executable, '-B', str(script), *map(str, arguments)]
            with log.open('w', encoding='utf-8', newline='\n') as output:
                result = subprocess.run(command, env=env, cwd=work, stdin=subprocess.DEVNULL,
                                        stdout=output, stderr=subprocess.STDOUT)
            with mutex:
                stages.append(dict(name=name, exit_code=result.returncode, command=command,
                                   seconds=time.monotonic()-begin, script_sha256=sha(script), log_sha256=sha(log)))
                write(work / 'STAGES.json', stages)
            need(result.returncode == 0, 'failed ' + name + '; see ' + str(log))
            print('PASS', name, flush=True)

        retained_driver = None
        if not reuse:
            layout = work / 'retained-layout'
            layout.mkdir()
            with tarfile.open(old / 'upstream-layout.tar.gz') as archive:
                members = archive.getmembers()
                for member in members:
                    safe(member.name)
                    need(member.isfile(), 'regular retained archive member')
                archive.extractall(layout, filter='data')
            retained_driver = layout / 'joint1148-round45/source/research/k8-eight-ends/replay_native.py'
            need(retained_driver.is_file(), 'retained native driver')
        jobs = {**words, **({'retained-' + tag: word for tag, word in retained.items()} if not reuse else {})}

        def fresh_native(tag):
            word = jobs[tag]
            entry = cache / sha(word)
            driver = retained_driver if tag.startswith('retained-') else source / 'new/run_native_borrow.py'
            run('native-' + tag, driver, word, entry)
            bind_native(entry, word)
            write(entry / 'CACHE.json', dict(word_sha256=sha(word), files=tree(entry)))

        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            list(pool.map(fresh_native, jobs))
        pm = sha(old / 'MANIFEST.json')
        receipts = cache / '_receipts' / pm
        if not reuse:
            run('retained-parent', old / 'verify.py', '--work', work / 'retained-parent',
                '--base-native-from', cache / sha(retained['base']),
                '--extra-native-from', cache / sha(retained['extra']))
            parent = read(work / 'retained-parent/RESULT.json')
            parent_stages = read(work / 'retained-parent/STAGES.json')
            need(len(parent_stages) == 16 and all(s['exit_code'] == 0 for s in parent_stages),
                 'sixteen successful fresh retained parent stages')
            need(parent['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION' and
                 parent['kappa'] == read(old / 'CLAIM.json')['kappa'], 'fresh retained parent PASS/claim')
            receipts.mkdir(parents=True)
            for name in ('RESULT.json', 'STAGES.json'):
                shutil.copy2(work / 'retained-parent' / name, receipts / name)
            write(receipts / 'RECEIPT.json', dict(schema='parent-receipt/1', vendor_manifest_sha256=pm,
                  claim_sha256=sha(old / 'CLAIM.json'), words={tag: sha(word) for tag, word in retained.items()},
                  files={name: sha(receipts / name) for name in ('RESULT.json', 'STAGES.json')}))
        source_guard(source)
        authenticate_vendor(vendor)
        providers = {tag: dict(word_sha256=sha(word), complete_native_files=tree(cache / sha(word), ('CACHE.json',)))
                     for tag, word in words.items()}
        result = dict(status=PROTOCOL_STATUS, source_commit='local-joint12-pr2733', manifest_sha256=DERIVED_SHA,
                      providers=providers, retained_parent_receipt_sha256=sha(receipts / 'RECEIPT.json'),
                      cache_files=tree(cache), fresh_current_provider_count=2,
                      fresh_retained_native_count=0 if reuse else 2,
                      reused_retained_native_count=2 if reuse else 0,
                      fresh_retained_parent=not bool(reuse), reused_retained_parent=bool(reuse),
                      retained_reuse_receipt_sha256=sha(work / 'RETAINED-REUSE.json') if reuse else None)
        write(work / 'NATIVE-RECEIPT.json', result)
        need(tree(cache) == result['cache_files'], 'final complete cache identity')
        write(work / 'RESULT.json', dict(status='PASS_PORTABLE_NATIVE_PREPARATION',
              native_receipt_sha256=sha(work / 'NATIVE-RECEIPT.json'), source_file_count=506,
              manifest_sha256=DERIVED_SHA, fresh_current_provider_count=2,
              fresh_retained_native_count=result['fresh_retained_native_count'],
              reused_retained_native_count=result['reused_retained_native_count'],
              fresh_retained_parent=result['fresh_retained_parent'], reused_retained_parent=bool(reuse),
              seconds=time.monotonic()-started, scope='Native preparation only; no T74 admission or T94 admission asserted.'))
        successful = True
        print('PASS_PORTABLE_NATIVE_PREPARATION', flush=True)
    finally:
        # The lock handle was closed immediately after its exclusive creation.
        # Failures retain a closed diagnostic lock; there are no hidden retries.
        if successful:
            lockpath.unlink()


if __name__ == '__main__':
    main()

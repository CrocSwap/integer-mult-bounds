#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Derived from Tekalign / PR2751 full_replay.py, with substantial OpenAI Codex assistance.
# This derivative composes Marius-Paul Dumitrean / PR2733's exact frame refit.
"""Cold reproduction of the twelve-source / five-frame composition.

Default: authenticated source download, fresh native providers and retained
parent admission, then the complete original supplier/release verifier. An
explicit --prepared-native-cache must match every published reuse file hash.
All large/generated artifacts remain under a fresh external --work directory.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as Q
import gzip
import hashlib
import importlib
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
from urllib.parse import quote
from urllib.request import Request, urlopen

from derive_runtime import derive_runtime

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
STEPS = ['native', 'ledgers', 'local-replay', 'wrappers', 'phases']


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def tree(root, exclude=()):
    result = {}
    for path in sorted(root.rglob('*')):
        need(not path.is_symlink(), 'unauthenticated symlink: ' + str(path))
        name = path.relative_to(root).as_posix()
        if path.is_file() and name not in exclude:
            result[name] = sha(path)
    return result


def safe(name):
    path = PurePosixPath(name)
    need(isinstance(name, str) and '\\' not in name and path.parts and not path.is_absolute()
         and '..' not in path.parts and path.as_posix() == name, 'unsafe source path')


def download(url, expected):
    for attempt in range(3):
        try:
            req = Request(url, headers={'User-Agent': 'integer-mult-prelife-priority/1', 'Accept-Encoding': 'identity'})
            with urlopen(req, timeout=90) as response:
                body = response.read()
            need(hashlib.sha256(body).hexdigest() == expected, 'download hash mismatch')
            return body
        except (OSError, RuntimeError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def source_copy(source, destination, pins, jobs):
    destination.mkdir()
    entries = {'MANIFEST.json': pins['manifest_sha256'], **pins['files']}
    need(len(pins['files']) == pins['count'] == 491, 'source file count')

    def copy(item):
        name, digest = item
        safe(name)
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source:
            need(not (source / name).is_symlink(), 'source symlink')
            body = (source / name).read_bytes()
            need(hashlib.sha256(body).hexdigest() == digest, 'source bytes: ' + name)
        else:
            body = download(pins['base_url'] + quote(name, safe='/'), digest)
        target.write_bytes(body)

    with ThreadPoolExecutor(max_workers=min(jobs, 8)) as pool:
        for _ in pool.map(copy, sorted(entries.items())):
            pass
    need(read(destination / 'MANIFEST.json') == pins['files']
         and tree(destination) == entries, 'complete source authentication')


def bind_native(entry, word):
    need(gzip.decompress((entry / 'local/FULL-WORD.json.gz').read_bytes()) == gzip.decompress(word.read_bytes()),
         'native complete word binding')
    stages = read(entry / 'STEPS.json')
    need([s['step'] for s in stages] == STEPS and all(s['exit_code'] == 0 for s in stages), 'native stage coverage')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, help='Exact original PR2679 package directory; otherwise download pinned files.')
    ap.add_argument('--work', type=Path, required=True)
    ap.add_argument('--composition-source', type=Path, help='Exact PR2751 package; otherwise fetch four pinned composition files.')
    ap.add_argument('--prepared-native-cache', type=Path, help='Explicit reuse of the complete published pinned cache.')
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    need(not sys.flags.optimize and a.jobs > 0, 'enabled assertions and positive jobs required')
    versions = {}
    for name in ('numpy', 'sympy', 'scipy', 'mpmath'):
        try:
            versions[name] = str(importlib.import_module(name).__version__)
        except ImportError as exc:
            raise RuntimeError('install requirements.txt in this Python environment before full replay') from exc
    need(versions['sympy'] == '1.14.0', 'pinned predecessor evidence requires sympy==1.14.0')
    work = a.work.resolve()
    need(not work.exists() and not work.is_relative_to(REPOSITORY), 'fresh external work required')
    for path in (a.source, a.composition_source, a.prepared_native_cache):
        need(path is None or (path.is_dir() and not work.is_relative_to(path.resolve())), 'input/work separation')
    config, claim = read(HERE / 'FULL-REPLAY-PINS.json'), read(HERE / 'CLAIM.json')
    reuse = read(HERE / 'evidence/NATIVE-RECEIPT.json') if a.prepared_native_cache else None
    work.mkdir(parents=True)
    composition = work / 'composition'
    composition.mkdir()
    for name, expected in config['files'].items():
        safe(name)
        body = ((a.composition_source / name).read_bytes() if a.composition_source
                else download(config['base_url'] + quote(name, safe='/'), expected))
        need(hashlib.sha256(body).hexdigest() == expected, 'composition source bytes: ' + name)
        destination = composition / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(body)
    pins = read(composition / 'SOURCE-FILES.json')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    for name in ('PYTHONOPTIMIZE', 'WITNESS_SPEC', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(name, None)
    stages, lock = [], threading.Lock()
    started = time.monotonic()

    def run(name, script, *args):
        begin = time.monotonic()
        log = work / (name + '.log')
        command = [sys.executable, '-B', str(script), *map(str, args)]
        with log.open('w') as output:
            result = subprocess.run(command, env=env, cwd=work, stdin=subprocess.DEVNULL,
                                    stdout=output, stderr=subprocess.STDOUT)
        with lock:
            stages.append(dict(name=name, command=command, exit_code=result.returncode,
                               script_sha256=sha(script), seconds=time.monotonic()-begin, log_sha256=sha(log)))
            write(work / 'STAGES.json', stages)
        need(result.returncode == 0, 'failed ' + name + '; see ' + str(log))
        print('PASS', name, flush=True)

    run('literal-review', HERE / 'verify.py')
    source = work / 'source'
    source_copy(a.source.resolve() if a.source else None, source, pins, a.jobs)
    overlay = read(composition / 'OVERLAY-PINS.json')
    need(sha(source/'MANIFEST.json') == overlay['original_manifest_sha256'], 'overlay base manifest')
    need(sha(composition/'DERIVATIVE-OVERLAY.tar.gz') == overlay['archive_sha256'], 'overlay archive')
    with tarfile.open(composition/'DERIVATIVE-OVERLAY.tar.gz') as archive:
        members=archive.getmembers()
        need(set(m.name for m in members)==set(overlay['files']) and len(members)==len(overlay['files']), 'exact overlay paths')
        for member in members:
            safe(member.name);need(member.isfile(), 'regular overlay file')
            body=archive.extractfile(member).read()
            need(hashlib.sha256(body).hexdigest()==overlay['files'][member.name], 'overlay member hash')
            (source/member.name).write_bytes(body)
    need(sha(source/'MANIFEST.json')==overlay['derived_manifest_sha256'] and
         tree(source,('MANIFEST.json',))==read(source/'MANIFEST.json'), 'complete derived source tree')
    changes = derive_runtime(source, HERE)
    need(sha(source/'MANIFEST.json') == config['derived_manifest_sha256']
         and tree(source, ('MANIFEST.json',)) == read(source/'MANIFEST.json'), 'complete refit source tree')
    write(work/'DERIVATION.json', changes)
    pins=dict(pins,commit=config['source_commit'],manifest_sha256=config['derived_manifest_sha256'])
    # Only source bindings and the strict predecessor comparison change in the
    # authenticated admission driver. Its physical costs and controls remain.
    admission = (composition/'workflow/admit.py').read_text()
    edits = [("SOURCE_COMMIT = 'local-joint12-pr2733'", "SOURCE_COMMIT = " + repr(config['source_commit'])),
             ("SOURCE_MANIFEST = '7980dbde79b63de4093cde89d1564a18c6bf16a2e35d810e38cf9797fe09e0cf'",
              "SOURCE_MANIFEST = " + repr(config['derived_manifest_sha256'])),
             ("previous = Q('0.0017161404259974415161889999999999999999999998999999999999999999999999')",
              "previous = Q(" + repr(read(HERE/'vendor/pr2751/CLAIM.json')['kappa']) + ")")]
    for before, after in edits:
        need(admission.count(before) == 1, 'exact admission patch preimage')
        admission = admission.replace(before, after)
    (work/'admit.py').write_text(admission)
    write(work/'ADMISSION-CHANGES.json', edits)

    cache = work / 'native-cache'
    if a.prepared_native_cache:
        need(tree(a.prepared_native_cache.resolve()) == reuse['cache_files'], 'published complete cache pins')
        shutil.copytree(a.prepared_native_cache.resolve(), cache)
        native_receipt = reuse
    else:
        cache.mkdir()
        layout = work / 'retained-layout'
        layout.mkdir()
        old = source / 'vendor/pr1297'
        with tarfile.open(old / 'upstream-layout.tar.gz') as archive:
            need(all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
                     for m in archive.getmembers()), 'retained archive paths')
            archive.extractall(layout, filter='data')
        retained_driver = layout / 'joint1148-round45/source/research/k8-eight-ends/replay_native.py'
        words = {'base': source / 'new/borrow/words/BORROW-WORD-43base.json.gz',
                 'extra': source / 'new/borrow/words/BORROW-WORD-43extra.json.gz',
                 'retained-base': old / 'gauge44-word.json.gz', 'retained-extra': old / 'extra-word.json.gz'}

        def fresh_native(tag):
            word = words[tag]
            entry = cache / sha(word)
            script = retained_driver if tag.startswith('retained-') else source / 'new/run_native_borrow.py'
            run('native-' + tag, script, word, entry)
            bind_native(entry, word)
            write(entry / 'CACHE.json', dict(word_sha256=sha(word), files=tree(entry)))

        with ThreadPoolExecutor(max_workers=min(a.jobs, 4)) as pool:
            for _ in pool.map(fresh_native, words):
                pass
        run('retained-parent', old / 'verify.py', '--work', work / 'retained-parent',
            '--base-native-from', cache / sha(words['retained-base']),
            '--extra-native-from', cache / sha(words['retained-extra']))
        parent = read(work / 'retained-parent/RESULT.json')
        need(parent['status'] == 'PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION'
             and parent['kappa'] == read(old / 'CLAIM.json')['kappa'], 'fresh retained parent admission')
        pm = sha(old / 'MANIFEST.json')
        receipts = cache / '_receipts' / pm
        receipts.mkdir(parents=True)
        for name in ('RESULT.json', 'STAGES.json'):
            shutil.copy2(work / 'retained-parent' / name, receipts / name)
        write(receipts / 'RECEIPT.json', dict(schema='parent-receipt/1', vendor_manifest_sha256=pm,
              claim_sha256=sha(old / 'CLAIM.json'), words={tag:sha(words['retained-'+tag]) for tag in ('base','extra')},
              files={name:sha(receipts / name) for name in ('RESULT.json','STAGES.json')}))
        providers = {tag:dict(word_sha256=sha(words[tag]), complete_native_files=tree(cache / sha(words[tag]), ('CACHE.json',)))
                     for tag in ('base','extra')}
        native_receipt = dict(status='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE',
                              source_commit=pins['commit'], manifest_sha256=pins['manifest_sha256'], providers=providers,
                              retained_parent_receipt_sha256=sha(receipts / 'RECEIPT.json'), cache_files=tree(cache))
    write(work / 'NATIVE-RECEIPT.json', native_receipt)
    run('complete-admission', work / 'admit.py', '--source', source,
        '--fill', HERE / 'vendor/pr2751/inputs/FILL.json.gz', '--order', HERE / 'vendor/pr2751/inputs/ORDER.json',
        '--native-cache', cache, '--native-receipt', work / 'NATIVE-RECEIPT.json',
        '--work', work / 'admission', '--jobs', a.jobs)
    result = read(work / 'admission/RESULT.json')
    need(result['status'] == 'PASS_COMPOSED_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'
         and Q(result['kappa']) == Q(claim['kappa']) and Q(result['complex_lower']) == Q(claim['complex_lower']),
         'published complete claim binding')
    need(result['profile'] == {str(k):v for k,v in read(HERE / 'CLAIM.json')['profile'].items()}, 'published complete profile binding')
    result.update(status='PASS_T74_JOINT_TWELVE_REFIT_COLD_COMPLETE_RELEASE', explicit_native_cache_reuse=bool(a.prepared_native_cache),
                  source_files_sha256=sha(composition / 'SOURCE-FILES.json'), native_receipt_sha256=sha(work / 'NATIVE-RECEIPT.json'),
                  cold_stages=stages, cold_seconds=time.monotonic()-started,
                  environment=dict(python=platform.python_version(), executable=sys.executable, versions=versions))
    write(work / 'RESULT.json', result)
    print(result['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

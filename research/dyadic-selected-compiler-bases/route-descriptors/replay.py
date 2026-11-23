"""Replay old and new exact checks in disposable, byte-identical copies."""
from __future__ import annotations

import argparse
from hashlib import sha1, sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
REMOTE_BASE = '67d18a45fdf3f675bd88cb6f52e7d0356a9ace36'
REMOTE_VERIFY_SHA = '75446c748694f13221146addb5446f3c8c4c23b1b8019c634a826be055e957d7'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def blob(data):
    return sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def snapshot():
    return {path.relative_to(PACKAGE).as_posix(): (digest(path), path.stat().st_mode & 0o777)
            for path in PACKAGE.rglob('*') if path.is_file()}


def authenticate():
    inventory = json.loads((HERE/'FROZEN-ADDITIONS.json').read_text())
    for name, expected in inventory['files'].items():
        need(digest(HERE/name) == expected, 'frozen added input changed: '+name)
    frozen = json.loads((HERE/'FROZEN.json').read_text())
    for name, expected in frozen['files'].items():
        need(digest(HERE/name) == expected, 'original author inventory changed: '+name)
    remote = HERE/'reconciliation/REMOTE-VERIFY.json'
    need(digest(remote) == REMOTE_VERIFY_SHA, 'original registered commands changed')
    preserved = json.loads((HERE/'reconciliation/PRESERVED-BASE.json').read_text())
    need(preserved['commit'] == REMOTE_BASE, 'wrong remote predecessor')
    need(preserved['mutable_metadata_only'] == ['README.md', 'TASK.json', 'VERIFY.json'],
         'preserved-source boundary changed')
    actual = {path.relative_to(PACKAGE).as_posix() for path in PACKAGE.rglob('*')
              if path.is_file() and not path.is_relative_to(HERE)}
    need(actual == set(preserved['files']), 'old package path set changed')
    checked = 0
    for name, item in preserved['files'].items():
        if item['allowed_metadata_update']:
            need(name in preserved['mutable_metadata_only'], 'unexpected mutable base file')
            continue
        path = PACKAGE/name
        data = path.read_bytes()
        need(len(data) == item['bytes'] and sha256(data).hexdigest() == item['sha256']
             and blob(data) == item['git_blob'], 'published scientific bytes changed: '+name)
        need(bool(path.stat().st_mode & 0o111) == (item['mode'] == '100755'),
             'published file mode changed: '+name)
        checked += 1
    old_readme = (HERE/'reconciliation/REMOTE-README.md').read_bytes()
    need((PACKAGE/'README.md').read_bytes().startswith(old_readme), 'parent README prefix changed')
    old_task = json.loads((HERE/'reconciliation/REMOTE-TASK.json').read_text())
    task = json.loads((PACKAGE/'TASK.json').read_text())
    need(task['original_card'] == old_task['original_card'], 'original task card changed')
    publication = json.loads((HERE/'PUBLICATION-ORIGINS.json').read_text())
    need(len(publication['files']) == 2, 'two supplemental predecessor origins required')
    for item in publication['files']:
        data = (HERE/item['local']).read_bytes()
        need(item['commit'] == '2fa1ba900f88ec6d32829eb69986cf585e3006af', 'predecessor publication pin changed')
        need(len(data) == item['bytes'] and sha256(data).hexdigest() == item['sha256']
             and blob(data) == item['git_blob'], 'published predecessor input changed')
    return {'preserved_scientific_files': checked, 'frozen_added_files': len(inventory['files']),
            'predecessor_publication_bindings': 2}


def compare_json(actual, expected, *, elapsed=False):
    need(actual.is_file(), 'checker did not create its fresh output: '+str(actual))
    left = json.loads(actual.read_text())
    right = json.loads(expected.read_text())
    if elapsed:
        need('seconds' in left and 'seconds' in right, 'expected elapsed-time receipt field missing')
        left.pop('seconds')
        right.pop('seconds')
    need(left == right, 'fresh scientific receipt differs: '+str(expected))
    return left.get('status', 'PASS_EXACT_JSON_COMPARISON')


def execute(argv, cwd, timeout):
    result = subprocess.run(argv, cwd=cwd, check=False, capture_output=True,
                            text=True, timeout=timeout,
                            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    if result.returncode:
        raise RuntimeError('Replay failed: '+repr(argv)+'\n'+result.stdout[-6000:]+'\n'+result.stderr[-6000:])


def legacy(index):
    manifest = json.loads((HERE/'reconciliation/REMOTE-VERIFY.json').read_text())
    need(0 <= index < len(manifest['commands']), 'legacy command index out of range')
    original = manifest['commands'][index]
    with tempfile.TemporaryDirectory(prefix='dyadic-legacy-', dir=os.environ.get('TMPDIR', '/tmp')) as name:
        temporary = Path(name)
        copied = temporary/'package'
        shutil.copytree(PACKAGE, copied)
        argv = [sys.executable if value == '{python}' else value.replace('{package}', str(copied))
                for value in original['argv']]
        if index in (0, 1):
            actual = copied/'EVIDENCE.json'
            expected = PACKAGE/'EVIDENCE.json'
        elif index in (2, 3):
            actual = temporary/'fresh-review/EVIDENCE.json'
            expected = PACKAGE/'review/EVIDENCE.json'
        elif index in (4, 5):
            actual = copied/'routing/EVIDENCE.json'
            expected = PACKAGE/'routing/EVIDENCE.json'
        else:
            actual = temporary/('finite-review-'+str(index)+'.json')
            expected = PACKAGE/'routing/review'/('EVIDENCE.json' if index == 6 else 'EVIDENCE-OPTIMIZED.json')
        actual.parent.mkdir(parents=True, exist_ok=True)
        if '--output' in argv:
            argv[argv.index('--output')+1] = str(actual)
        actual.unlink(missing_ok=True)
        execute(argv, copied, original['timeout_seconds'])
        marker = compare_json(actual, expected, elapsed=index in (6, 7))
        if index in (2, 3):
            need((actual.parent/'INDEPENDENT-BASES.json').read_bytes()
                 == (PACKAGE/'review/INDEPENDENT-BASES.json').read_bytes(),
                 'fresh independent complete basis catalogue differs')
        print(json.dumps({'legacy_index': index, 'status': marker,
                          'original_scientific_flags_preserved': True,
                          'fresh_output_checked': True, 'ignored_only_elapsed_seconds': index in (6, 7)}, sort_keys=True), flush=True)


def supplement():
    with tempfile.TemporaryDirectory(prefix='dyadic-descriptors-', dir=os.environ.get('TMPDIR', '/tmp')) as name:
        temporary = Path(name)
        copied = temporary/'package'
        shutil.copytree(PACKAGE, copied)
        source = copied/'route-descriptors'
        for filename in ('DESCRIPTORS.json.gz', 'EXAMPLES.json'):
            (source/filename).unlink()
        execute([sys.executable, '-I', '-W', 'error', '-B', str(source/'routes.py')], source, 90)
        for filename in ('DESCRIPTORS.json.gz', 'EXAMPLES.json'):
            need((source/filename).read_bytes() == (HERE/filename).read_bytes(),
                 'fresh deterministic constructor output differs: '+filename)
        print('PASS_EXACT_DESCRIPTOR_AND_EXAMPLE_REGENERATION', flush=True)
        for optimized in (False, True):
            flags = ['-I']+(['-O'] if optimized else [])+['-W', 'error', '-B']
            mode = 'optimized' if optimized else 'normal'
            expected_name = 'EVIDENCE-OPTIMIZED.json' if optimized else 'EVIDENCE.json'
            output = temporary/('author-'+mode+'.json')
            need(not output.exists(), 'author output must start absent')
            execute([sys.executable, *flags, str(source/'check.py'), '--output', str(output)], source, 90)
            marker = compare_json(output, HERE/expected_name)
            print(json.dumps({'new_author': mode, 'status': marker, 'fresh_output_checked': True}), flush=True)
            output = temporary/('review-'+mode+'.json')
            need(not output.exists(), 'review output must start absent')
            execute([sys.executable, *flags, str(source/'review/independent.py'),
                     '--source', str(source), '--output', str(output)], source, 90)
            marker = compare_json(output, HERE/'review'/expected_name)
            print(json.dumps({'new_independent_review': mode, 'status': marker,
                              'fresh_output_checked': True}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', required=True, choices=['legacy', 'finite-review', 'supplement'])
    parser.add_argument('--index', type=int)
    args = parser.parse_args()
    before = snapshot()
    bindings = authenticate()
    try:
        if args.mode == 'legacy':
            need(args.index is not None and 0 <= args.index <= 5, 'legacy mode needs index 0..5')
            legacy(args.index)
        elif args.mode == 'finite-review':
            need(args.index is None, 'finite review has no index')
            for index in (6, 7):
                legacy(index)
        else:
            need(args.index is None, 'supplement has no index')
            supplement()
    finally:
        need(snapshot() == before, 'replay modified the published package')
    need(authenticate() == bindings, 'post-replay source bindings changed')
    print(json.dumps({'status': 'PASS_DISPOSABLE_DYADIC_REPLAY', 'mode': args.mode,
                      'package_bytes_and_modes_unchanged': True, **bindings}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()

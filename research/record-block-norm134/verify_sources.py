# SPDX-License-Identifier: Apache-2.0
"""Verify the exact source inventory and executable derivations, without Git."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree(root, exclude=()):
    root = Path(root)
    result = {}
    for path in sorted(root.rglob('*')):
        need(not path.is_symlink(), 'symlink in authenticated tree')
        if path.is_file():
            name = path.relative_to(root).as_posix()
            if name not in exclude:
                result[name] = sha(path)
    return result


def check():
    need(not sys.flags.optimize, 'assertions enabled for inherited checkers')
    manifest = read(HERE/'MANIFEST.json')
    need(tree(HERE, ('MANIFEST.json',)) == manifest, 'exact package source inventory')
    sources = read(HERE/'SOURCES.json')
    for record in sources['files']:
        if record['usage'] != 'input':
            continue
        name = PurePosixPath(record['path'])
        need(not name.is_absolute() and '..' not in name.parts, 'safe source path')
        path = ROOT/record['path']
        need(path.resolve().is_relative_to(ROOT) and not path.is_symlink(), 'contained source')
        need(sha(path) == record['sha256'], 'external source pin: '+record['path'])
    derivation = read(HERE/'DERIVATION.json')
    need(derivation['precision_source_head'] == '2fdd289fcd0896f4691f9dd78a8bf1511573e434', 'precision source head')
    need(derivation['scientific_source_head'] == 'e9307b48d7d1b690939935ecef0f8e524e6d92f4', 'native source head')
    need(derivation['comparison_head'] == '47a7227c044cd0cabb1432a06c61dd5d60c07f5a', 'incumbent source head')
    for record in derivation['changes']:
        source, target = HERE/'reference'/record['source'], HERE/record['target']
        need(sha(source) == record['source_sha256'], 'retained source bytes')
        body = source.read_bytes().decode('utf-8')
        for before, after in record['replacements']:
            need(body.count(before) == 1, 'unique derivation preimage')
            body = body.replace(before,after)
        need(body.encode('utf-8') == target.read_bytes() and sha(target) == record['target_sha256'], 'exact executable derivation')
    producer = read(HERE/'PRODUCER-DERIVATION.json')
    source = HERE/'reference/build_allocation.py'
    need(sha(source) == producer['source_sha256'] == sha(ROOT/producer['source_path']), 'producer scientific source')
    body = source.read_bytes().decode('utf-8')
    for change in producer['changes']:
        need(body.count(change['before']) == change['occurrences'], 'producer derivation occurrence')
        body = body.replace(change['before'],change['after'])
    need(body.encode('utf-8') == (HERE/'build_allocation.py').read_bytes() and
         sha(HERE/'build_allocation.py') == producer['target_sha256'], 'exact final producer')
    for name, digest in producer['warm_inputs'].items():
        need(sha(ROOT/'research/replica-integer-prefix/data'/name) == digest, 'actual inherited T124 allocation')
    for folder in ('solution','data'):
        for name, digest in producer[folder].items():
            need(sha(HERE/folder/name) == digest, 'exact constructed '+folder)
    need(sha(HERE/'PR2843-CLAIM.json') == derivation['comparison_claim_sha256'], 'full exact comparison claim')
    return {'status':'PASS_T134_SOURCE_AND_EXECUTABLE_DERIVATIONS',
            'package_files':len(manifest),'external_inputs':sum(r['usage']=='input' for r in sources['files']),
            'manifest_sha256':sha(HERE/'MANIFEST.json')}


if __name__ == '__main__':
    print(json.dumps(check(),sort_keys=True))

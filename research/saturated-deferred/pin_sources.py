#!/usr/bin/env python3
"""Explicitly freeze the credited source closure; ordinary verification is read-only."""
import sys
if not __debug__:
    raise RuntimeError('Assertions required')
sys.dont_write_bytecode = True
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVES = ROOT/'references/signed-recursion'
RECEIPTS = {'SOURCE.json', 'validation.json', 'independent-audit.json',
            'integration-validation.json'}

def paths():
    files = {p for p in HERE.rglob('*') if p.is_file() and
             p.name not in RECEIPTS and p.suffix not in ('.log', '.pyc', '.pyo')
             and '__pycache__' not in p.parts}
    for folder in ('pr97', 'pr99', 'pr100'):
        base = ARCHIVES/folder
        manifest = json.loads((base/'ARCHIVE.json').read_text())
        files |= {base/p for p in manifest['files']} | {base/'ARCHIVE.json'}
    for name in ('research/copied-fixed/balanced_assembly.py',
                 'research/copied-fixed/PROOF.md',
                 'research/deferred-span-frames/independent_check.py'):
        files.add(ROOT/name)
    return sorted(files)

def check():
    manifest = json.loads((HERE/'SOURCE.json').read_text())
    assert {str(p.relative_to(ROOT)) for p in paths()} <= set(manifest['files'])
    for name, digest in manifest['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    for name in ('pr97', 'pr99', 'pr100'):
        folder = ARCHIVES/name
        archive = json.loads((folder/'ARCHIVE.json').read_text())
        assert set(archive['files']) == set(archive['git_blobs'])
        for path, digest in archive['files'].items():
            raw = (folder/path).read_bytes()
            assert sha256(raw).hexdigest() == digest, (name, path)
            assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == archive['git_blobs'][path], (name, path)
    return manifest

if __name__ == '__main__':
    manifest = dict(files={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths()},
                    scope='Immutable credited PR97/99/100 Git blobs, selected saturated schedule, complete ledgers, bridge, exact arithmetic, and verification sources. Run receipts are separate.')
    (HERE/'SOURCE.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    check()
    print('PASS frozen saturated-deferred source closure')

#!/usr/bin/env python3
"""Freeze or check the complete selected source closure; no automatic repinning."""
import sys
if not __debug__:
    raise RuntimeError('Assertions required')
sys.dont_write_bytecode = True
from hashlib import sha1, sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVES = ('references/stopped-recursion/pr107', 'references/signed-recursion/pr100')
RECEIPTS = {'SOURCE.json','validation.json','independent-audit.json',
            'physical-audit.json','interface-audit.json','literal-audit.json','integration-validation.json'}

def paths():
    files = {p for p in HERE.rglob('*') if p.is_file() and p.name not in RECEIPTS
             and p.suffix not in ('.log','.pyc','.pyo') and '__pycache__' not in p.parts}
    for relative in ARCHIVES:
        base = ROOT/relative
        files |= {base/p for p in json.loads((base/'ARCHIVE.json').read_text())['files']}
        files.add(base/'ARCHIVE.json')
    files |= {ROOT/'research/deferred-span-frames/independent_check.py',
              ROOT/'research/copied-fixed/balanced_assembly.py'}
    return sorted(files)

def check():
    manifest = json.loads((HERE/'SOURCE.json').read_text())
    assert {str(p.relative_to(ROOT)) for p in paths()} <= set(manifest['files'])
    for name,digest in manifest['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    for relative in ARCHIVES:
        base = ROOT/relative
        archive = json.loads((base/'ARCHIVE.json').read_text())
        assert set(archive['files'])==set(archive['git_blobs'])
        for name,digest in archive['files'].items():
            raw=(base/name).read_bytes()
            assert sha256(raw).hexdigest()==digest,name
            assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==archive['git_blobs'][name],name
    parent=ROOT/ARCHIVES[0]
    for name,digest in json.loads((parent/'research/reversed-rational-centers/SOURCE.json').read_text())['files'].items():
        assert sha256((parent/name).read_bytes()).hexdigest()==digest,name
    return manifest

if __name__=='__main__':
    manifest=dict(files={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest()for p in paths()},
                  scope='Complete credited PR107/104 and exact arithmetic source closures, selected producer/matching/certificate and independent finite checks. Run receipts are separate.')
    (HERE/'SOURCE.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    check();print('PASS stopped-pairtree source closure frozen')

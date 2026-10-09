#!/usr/bin/env python3
"""Explicit source-freezing operation; never invoked by ordinary verification."""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def paths():
    files = [p for p in HERE.rglob('*') if p.is_file() and p.suffix in ('.py', '.md', '.json', '.gz')
             and p.name not in ('SOURCE.json', 'validation.json', 'integration-validation.json',
                                'independent-audit.json', 'endpoint-check.json', 'corner-audit.json')
             and '__pycache__' not in p.parts]
    for name in ('pr91', 'pr96'):
        folder = ROOT / 'references/frame-compiler' / name
        manifest = json.loads((folder / 'SOURCE.json').read_text())
        files += [folder / path for path in manifest['files']] + [folder / 'SOURCE.json']
    parent = ROOT / 'research/deferred-span-frames'
    manifest = json.loads((parent / 'SOURCE.json').read_text())
    files += [ROOT / path for path in manifest['files']] + [parent / 'SOURCE.json', parent / 'independent_check.py', parent / 'certificate.json']
    files += [ROOT / 'research/copied-fixed/reversed' / name for name in ('geometry-source.json', 'pr34/independent_controls.py')]
    for name in ('pr69', 'pr71', 'pr82', 'pr84'):
        folder = ROOT / 'references/frame-compiler' / name
        manifest = json.loads((folder / 'SOURCE.json').read_text())
        files += [folder / path for path in manifest['files']] + [folder / 'SOURCE.json']
    return sorted(set(files))

def check():
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    required = {str(path.relative_to(ROOT)) for path in paths()}
    assert required <= set(manifest['files']), 'Incomplete frozen source/evidence closure'
    for name, digest in manifest['files'].items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    for name in ('pr91', 'pr96'):
        folder = ROOT / 'references/frame-compiler' / name
        original = json.loads((folder / 'SOURCE.json').read_text())
        for path, digest in original['files'].items():
            raw = (folder / path).read_bytes()
            assert sha256(raw).hexdigest() == digest
            from hashlib import sha1
            assert sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == original['git_blobs'][path]
    return manifest

if __name__ == '__main__':
    manifest = dict(files={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths()},
                    scope='Immutable credited upstream Git blobs, frozen parent construction, complete selected words/profiles/ledgers and independent verification sources. Timing/log receipts excluded.')
    (HERE / 'SOURCE.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    check()
    print('PASS reviewed source and evidence closure frozen')

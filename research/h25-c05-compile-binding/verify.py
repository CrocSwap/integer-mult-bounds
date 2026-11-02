#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the complete package archive without executing any archived source."""
from pathlib import Path, PurePosixPath
import hashlib
import json


def verify():
    package = Path(__file__).resolve().parent
    manifest = json.loads((package / 'ARTIFACTS.json').read_text(encoding='utf-8'))
    expected = set()
    for row in manifest['files']:
        spelling = row['path']
        path = PurePosixPath(spelling)
        if path.is_absolute() or any(p in ('', '.', '..') for p in path.parts) or spelling in expected:
            raise RuntimeError('invalid or duplicate archive path: ' + spelling)
        expected.add(spelling)
        target = package / spelling
        if any(part.is_symlink() for part in [target, *target.parents] if part.is_relative_to(package)):
            raise RuntimeError('archive link: ' + spelling)
        data = target.read_bytes()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise RuntimeError('archive byte mismatch: ' + spelling)
    actual = {str(p.relative_to(package)) for p in package.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if actual != expected | {'ARTIFACTS.json'}:
        raise RuntimeError('archive inventory differs: ' + repr(sorted(actual ^ (expected | {'ARTIFACTS.json'}))))
    print('PASS_BINDING_ARCHIVE_BYTES_ONLY files=' + str(len(expected)), flush=True)


if __name__ == '__main__':
    verify()

# SPDX-License-Identifier: Apache-2.0
"""Validate the immutable T37 package and declared predecessor source closure."""
import argparse
import hashlib
import json
from pathlib import Path
from common import P, ROOT, T21, load


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(package=P, root=ROOT):
    manifest = package/'MANIFEST.json'
    expected = json.loads(manifest.read_text())
    actual = {p.relative_to(package).as_posix(): sha(p)
              for p in package.rglob('*')
              if p.is_file() and p != manifest and '__pycache__' not in p.parts}
    if actual != expected:
        raise ValueError('T37 package manifest mismatch')
    dependencies = package/'DEPENDENCY-PINS.json'
    for relative, digest in json.loads(dependencies.read_text()).items():
        path = (root/relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
            raise ValueError('Invalid dependency path: '+relative)
        if sha(path) != digest:
            raise ValueError('Changed dependency: '+relative)
    predecessor = load(T21/'verify.py', 't37_predecessor_pins').validate_pins()
    return dict(manifest_sha256=sha(manifest), dependencies_sha256=sha(dependencies),
                predecessor=predecessor)


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))

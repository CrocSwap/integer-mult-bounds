#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Raw-source authentication and canonical artifact helpers."""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def read(p):
    p = Path(p)
    data = p.read_bytes()
    return json.loads(gzip.decompress(data) if p.suffix == '.gz' else data)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def check_inputs():
    for entry in read(HERE / 'PREDECESSORS.json')['hosting_source']['files']:
        require(sha(HERE / entry['local']) == entry['sha256'], 'Changed hosting source: ' + entry['local'])

def check_source(package, number):
    pin = read(HERE / 'PREDECESSORS.json')['sources'][number]
    manifest = package / 'MANIFEST.json'
    require(sha(manifest) == pin['manifest_sha256'], 'Wrong source manifest ' + number)
    expected = read(manifest)
    actual = {p.relative_to(package).as_posix() for p in package.rglob('*')
              if p.is_file() and p != manifest}
    require(actual == set(expected), 'Source inventory changed ' + number)
    for name, digest in expected.items():
        require(sha(package / name) == digest, 'Changed source ' + number + ': ' + name)

def write(p, value):
    Path(p).write_text(json.dumps(value, indent=2) + '\n')

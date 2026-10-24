#!/usr/bin/env python3
"""Read-only launcher for the unchanged retained-helper science checker.

Apache-2.0; substantial OpenAI Codex assistance. All mathematical and source
checks are in science/check.py; this launcher authenticates its frozen tree.
"""
from hashlib import sha256
from pathlib import Path
import json
import runpy
import sys

HERE = Path(__file__).resolve().parent
SCIENCE = HERE / 'science'
MANIFEST_SHA256 = '49e5479fc694533b4b73bb94effb5c9284e5decc4dc95dbabb6cf89df31c0fc1'
REVIEW_SHA256 = {
    'REVIEW.md': '010c22b8d745e54783ce4d5f220bf16dbd906e5dbc1db62a3cad81101fd168a7',
    'REVIEW.json': '7db590df8aa4a02db8d35e58bf17095791c5432d7af8b0a1e287a8f920d06420',
    'INPUTS.json': 'fe2b94468e3a016eecdc12f4e0911a8022ee7776ab9f791aaad0e2324d580117',
}


def need(test, why):
    if not test:
        raise ValueError(why)


def authenticate():
    for name, digest in REVIEW_SHA256.items():
        need(sha256((HERE / 'independent' / name).read_bytes()).hexdigest() == digest,
             'Frozen independent review record: ' + name)
    raw = (SCIENCE / 'FILES.json').read_bytes()
    need(sha256(raw).hexdigest() == MANIFEST_SHA256, 'Frozen science manifest')
    rows = json.loads(raw)['files']
    expected = {row['path'] for row in rows} | {'FILES.json'}
    actual = {p.relative_to(SCIENCE).as_posix() for p in SCIENCE.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts}
    need(expected == actual, 'Exact frozen science inventory')
    for row in rows:
        need(sha256((SCIENCE / row['path']).read_bytes()).hexdigest() == row['sha256'],
             'Frozen science file: ' + row['path'])
    return {row['path']: row['sha256'] for row in rows}


if __name__ == '__main__':
    need(len(sys.argv) == 1, 'Read-only launcher accepts no generation arguments')
    before = authenticate()
    runpy.run_path(str(SCIENCE / 'check.py'), run_name='__main__')
    need(authenticate() == before, 'Read-only science replay')

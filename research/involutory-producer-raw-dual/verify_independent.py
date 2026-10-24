#!/usr/bin/env python3
"""Authenticate and replay the unchanged independent packet, read-only.

Independent scripts are already Git-free. Their printed scientific output is
compared to the retained receipt. Apache-2.0; substantial Codex assistance.
"""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'independent'
MANIFEST_SHA = 'fb4e1ca6ebc1e03b071cb8e49159a235a107d5a5fc86ff67afe6220e48366ef9'
PARTS = {'derive': ('derive.py', 'DERIVATION.json'),
         'audit': ('audit.py', 'REVIEW.json'),
         'ceiling': ('check_ceiling.py', 'CEILING.json')}


def need(test, why):
    if not test:
        raise ValueError(why)


def authenticate():
    raw = (ROOT / 'FILES.json').read_bytes()
    need(sha256(raw).hexdigest() == MANIFEST_SHA, 'Exact independent archive manifest')
    files = json.loads(raw)['files']
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(actual == set(files) | {'FILES.json'}, 'Exact independent file inventory')
    for path, digest in files.items():
        need(sha256((ROOT / path).read_bytes()).hexdigest() == digest, 'Independent frozen file: ' + path)
    return files


def run(part):
    before = authenticate()
    script, receipt = PARTS[part]
    captured = io.StringIO()
    saved = sys.argv[:]
    try:
        sys.argv = [str(ROOT / script)]
        with redirect_stdout(captured):
            runpy.run_path(str(ROOT / script), run_name='__main__')
    finally:
        sys.argv = saved
    need(json.loads(captured.getvalue()) == json.loads((ROOT / receipt).read_text()), 'Exact independent scientific receipt: ' + receipt)
    need(authenticate() == before, 'Read-only independent replay')
    return {'status': 'PASS_PORTABLE_INDEPENDENT_RAWDUAL_' + part.upper(),
            'receipt': receipt, 'new_kappa': False, 'complete_caller': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('part', choices=sorted(PARTS))
    args = parser.parse_args()
    print(json.dumps(run(args.part), sort_keys=True))

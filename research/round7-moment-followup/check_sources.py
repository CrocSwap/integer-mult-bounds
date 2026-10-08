#!/usr/bin/env python3
"""Check the frozen local source closure before evaluating any certificate."""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def check_sources():
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    for name,digest in manifest['files'].items():
        path=ROOT/name
        assert path.is_file() and sha256(path.read_bytes()).hexdigest()==digest,name
    return len(manifest['files'])

if __name__=='__main__':
    print('PASS source pins',check_sources())

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild the final 680-owner BIT word from the pinned #7781 source cache."""

import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
FINAL = 'd3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d'
PINS = {
    'BIRTHS.json': '7fa07209cee23b15d9bbd178bab4bed7bb01b7ce2da743744e6ddbd9d3f5920c',
    'WITHDRAWALS.json': '82d0ad19182d248f075022860b5ef441c24cd85b71bd514b01c36b64ba3a3f02',
    'REPLAY.json': '0c90174cef40c742972296f306eaf0dc1eadfb04b3f2cfa3feaa49c368d7480b',
    'ROOT411-CONTROL.json': '1fa2bd65dd8779e76865cd7a0922ecd5e97d85e8cc56e6ecb3fdeebeb47e8782',
    'WORD.json.gz': 'd28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9',
}
LITERAL_SHA = '4021766d87fa791a43a78a6665c9260b7ba3772d8b2db6e9c84b6a3d51a1305c'


def pinned(path, digest):
    contents = path.read_bytes()
    if sha256(contents).hexdigest() != digest:
        raise ValueError(f'SHA-256 pin for {path}')
    return contents


def run(script, *arguments):
    subprocess.run([sys.executable, '-I', '-B', str(HERE / script), *map(str, arguments)], check=True)


def rebuild(cache, out):
    supplied = {name: pinned(HERE / name, digest) for name, digest in PINS.items()}
    parent = cache / 'parent' / 'binary'
    source = cache / 'source'
    literal = parent / 'independent' / 'literal.py'
    pinned(literal, LITERAL_SHA)

    out.mkdir(parents=True, exist_ok=True)
    contact = out / 'contact'
    run('replay.py', '--source-root', source, '--parent-word', parent / 'WORD.json.gz',
        '--journal', HERE / 'BIRTHS.json', '--out', contact)
    result = out / 'WORD.json.gz'
    control = out / 'ROOT411-CONTROL.json'
    run('replay_quotients.py', '--contact', contact / 'WORD.json.gz',
        '--withdrawals', HERE / 'WITHDRAWALS.json', '--tree411', HERE / 'REPLAY.json',
        '--edge', source / 'research/p104-dual-supplier-lift/bit_native.py',
        '--literal', literal, '--root-control-out', control, '--out', result)
    if control.read_bytes() != supplied['ROOT411-CONTROL.json']:
        raise ValueError('rooted owner-411 control differs from the independent receipt')
    wire = gzip.decompress(result.read_bytes())
    word = json.loads(wire)
    canonical = json.dumps(word, separators=(',', ':'), sort_keys=True).encode()
    if sha256(canonical).hexdigest() != FINAL or wire != gzip.decompress(supplied['WORD.json.gz']):
        raise ValueError('emitted candidate differs from frozen canonical word or decompressed bytes')
    return word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True, help='Prepared source cache')
    parser.add_argument('--out', type=Path, required=True, help='Rebuilt word and contact checkpoint directory')
    args = parser.parse_args()
    word = rebuild(args.cache.resolve(), args.out.resolve())
    print('PASS_BINARY_CONSTRUCTION', FINAL, word['public'])


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Move helper 757's update through two existing contacts with helper 1255.

Ali Romman, with substantial OpenAI Codex assistance.
The word and application retain Hao Yan/7604 and all predecessor credit.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / 'retained/pr7604/word.json.gz'
CLAIM = '0.0036504442446'
BEGIN, FIRST, UPDATE, SECOND = 33518, 38584, 42714, 42716


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCE-VERSIONS.json').read_bytes())
    expected = set()
    for entry in manifest['files']:
        path = HERE / entry['path']
        require(entry['path'] not in expected, 'duplicate retained source')
        expected.add(entry['path'])
        require(not path.is_symlink() and path.resolve().is_relative_to(HERE / 'retained'),
                'retained source path')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'],
                'retained source mismatch: ' + entry['path'])
    present = {p.relative_to(HERE).as_posix() for p in (HERE / 'retained').rglob('*')
               if p.is_file() and '__pycache__' not in p.parts}
    require(present == expected, 'complete retained source inventory')


def build_word():
    authenticate()
    word = json.loads(gzip.decompress(BASE.read_bytes()))
    program = word['program']
    required = {
        BEGIN - 1: ['ADD', 1143, 757, '-1', 3],
        FIRST: ['MOVE', 757, 3, 595, False],
        FIRST + 1: ['ADD', 757, 902, '-1', 595],
        UPDATE: ['ADD', 757, 1557, '-2/3', 595],
        SECOND: ['MOVE', 757, 595, 603, False],
        SECOND + 1: ['ADD', 1255, 757, '-1', 603],
    }
    require(all(program[i] == e for i, e in required.items()), 'literal source contacts')
    uses = []
    for i in range(BEGIN, SECOND):
        event = program[i]
        operands = event[1:3] if event[0] in ('ADD', 'COPY') else event[1:2]
        if 757 in operands:
            uses.append(i)
    require(uses == [FIRST, FIRST + 1, UPDATE], 'receive-only interval')
    result = []
    for i, event in enumerate(program):
        if i == BEGIN:
            result.append(['ADD', 757, 1255, '-1', 3])
        if i == SECOND:
            result.extend([['MOVE', 757, 3, 603, False],
                           ['ADD', 757, 1255, '1', 603]])
        elif i not in (FIRST, FIRST + 1, UPDATE):
            result.append(event)
    word['program'] = result
    return word


def invoice():
    source = json.loads((HERE / 'retained/pr7604/invoice-new.json').read_bytes())
    result = copy.deepcopy(source)
    result['paid']['1'] -= 34
    result['paid']['2'] += 17
    require(sum(result['paid'].values()) == 110366, 'complete paid count')
    require(sum(result['targets'].values()) == 22461, 'complete target count')
    mass = lambda h: sum(int(r) * n for r, n in h.items())
    require(mass(result['targets']) - mass(result['paid']) == 1424, 'rank surplus')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    word, bill = build_word(), invoice()
    if args.write:
        payload = json.dumps(word, separators=(',', ':')).encode()
        (HERE / 'data/word.json.gz').write_bytes(gzip.compress(payload, mtime=0))
        (HERE / 'data/invoice-new.json').write_text(json.dumps(bill, indent=2) + '\n')
    require(json.loads(gzip.decompress((HERE / 'data/word.json.gz').read_bytes())) == word,
            'exact constructed word')
    require(json.loads((HERE / 'data/invoice-new.json').read_bytes()) == bill,
            'exact complete invoice')
    print(json.dumps(dict(status='PASS_HELPER757_CONSTRUCTION', claim=CLAIM,
                         events=len(word['program']), paid_delta={'1': -34, '2': 17})))


if __name__ == '__main__':
    main()

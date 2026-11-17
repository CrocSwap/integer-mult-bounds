# SPDX-License-Identifier: Apache-2.0
"""Extract DreamingOfClouds' coupled chart-1062 component on Ali Romman's original word."""
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE / 'retained/pr7605'
DATA = HERE / 'data'
CANONICAL = '86bc8a1d1276c5b8d80a19704f90279e85b24b9490a02b9afa67c1a5b119c114'
CLAIM = '0.0036512866636'
PINS = {
    '7605-closure.json': 'd4c2500703fd651d5eee8ae9dfd64439703716d1c43656f3455d66157a1912fd',
    'peer7611.json': '64f096802f328cac7e51c655c2c5a1aa6c011dd33ea278c53a05caaa598594df',
    'edits.json': '70318dfdd760104c07d8c0c45b57bd05bee47499b01767180aaf563ea195bac7',
    'caller.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'word.json.gz': '1b0efdc59fe3f8056f3dbfdd618c7f5b4b4f0ed4063689f182ae3dbd1138fede',
    'invoice.json': '5ea13a376c00be2363e9508f23d9ceaf299fb297fb54c82a6cd2b8559aa92bac',
}


def require(ok, label):
    if not ok:
        raise ValueError(label)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def verify_sources():
    for name, expected in PINS.items():
        require(sha256((DATA/name).read_bytes()).hexdigest() == expected, name)
    closure = read(DATA/'7605-closure.json')
    paths = {p.relative_to(BASE).as_posix() for p in BASE.rglob('*') if p.is_file()}
    require(len(closure) == 138 and paths == set(closure), 'Complete #7605 package inventory')
    for name, expected in closure.items():
        require(sha256((BASE/name).read_bytes()).hexdigest() == expected, name)


def build():
    verify_sources()
    old = read(BASE/'data/word.json.gz')
    peer = read(DATA/'peer7611.json')
    tape = old['program']
    require(not peer['append'] and len(tape) == peer['base_events'] + 5, 'Exact predecessor displacement')
    for i, event in peer['delete']:
        require(tape[i+5] == event, 'Original operation at peer deletion ' + str(i))
    ops = dict(peer['insert_before'])
    entrance = [e for e in ops[0] if e[1] in (185, 196)]
    def operands(e):
        return set(e[1:3] if e[0] in ('ADD','COPY') else e[1:2])
    left = set().union(*(operands(e) for e in entrance))
    other = set().union(*(operands(e) for e in ops[0] if e[1] not in (185,196)))
    require(len(entrance) == 16 and left.isdisjoint(other), 'Separable entrance operands')
    deletes = [[i+5,e] for i,e in peer['delete'] if i in (42105,42106,42107,42189,43579)]
    inserts = [[0,entrance]] + [[i+5, ops[i]] for i in (42189,43579,43581)]
    edits = dict(base_events=len(tape), delete=deletes, insert_before=inserts, append=[])
    require(edits == read(DATA/'edits.json'), 'Exact literal edit on #7605')
    removed, added = dict(deletes), dict(inserts)
    program = []
    for i, event in enumerate(tape):
        program.extend(added.get(i, []))
        if i not in removed:
            program.append(event)
    word = dict(old, program=program)
    require(len(program) == 76651 and sha256(canonical(word)).hexdigest() == CANONICAL, 'Canonical candidate')
    require(word == read(DATA/'word.json.gz'), 'Independent reconstruction equals frozen word')
    old_ops, new_ops = (Counter(e[0] for e in rows) for rows in (tape,program))
    new_ops.subtract(old_ops)
    require({k:v for k,v in new_ops.items() if v} == {'ADD':17,'MOVE':-2}, 'Changed operations')
    return word


if __name__ == '__main__':
    require(__debug__ and sys.version_info[:2] == (3,12), 'Use CPython 3.12 -I -B')
    word = build()
    print('PASS_CHART1062_FROZEN_WORD', len(word['program']), CANONICAL)

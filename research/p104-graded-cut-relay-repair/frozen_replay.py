#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent list-based interpreter for a source and explicit edit list.

This checker does not import or call repair.py. The edit list is attached to
original clocks and records the expected old instruction for every edit.
"""
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SHA = '74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'


def source(path):
    raw = Path(path).read_bytes()
    assert sha256(raw).hexdigest() == SHA
    return json.loads(gzip.decompress(raw))


def apply(program, doc):
    assert doc['source_sha256'] == SHA
    indexed = {}
    for entry in doc['edits']:
        clock = entry['original_clock']
        assert isinstance(clock, int) and 0 <= clock < len(program)
        assert clock not in indexed and program[clock] == entry['old']
        indexed[clock] = entry['replacement']
    new = []
    for clock, row in enumerate(program):
        new.extend(indexed.get(clock, [row]))
    return new


def forward(g, program):
    where = list(g['start']) + [None] * g['owned_fields']
    vals = [1 << i for i in range(g['public'])] + [0] * g['owned_fields']
    clears = []
    for row in program:
        code, i, *a = row
        if code == 'INIT':
            assert where[i] is None
            where[i], vals[i] = a[0], 0
        elif code == 'ADD':
            j, c = a
            assert where[i] == where[j] == c
            vals[i] ^= vals[j]
        elif code == 'MOVE':
            c, d = a
            assert where[i] == c
            where[i] = d
        elif code == 'SWAP':
            j, = a
            vals[j], vals[i] = vals[i], vals[j]
            where[j], where[i] = where[i], where[j]
        elif code == 'CLEAR':
            assert where[i] == a[0] and i >= g['public']
            clears.append((i, where[i], vals[i]))
            where[i], vals[i] = None, 0
        else:
            raise AssertionError(code)
    assert where[:g['public']] == g['final'] and all(x is None for x in where[g['public']:])
    return vals[:g['public']], clears


def adjoint(g, program):
    where = list(g['final']) + [None] * g['owned_fields']
    vals = [1 << i for i in range(g['public'])] + [0] * g['owned_fields']
    for row in reversed(program):
        op, i, *a = row
        if op == 'INIT':
            assert where[i] == a[0]
            where[i], vals[i] = None, 0
        elif op == 'CLEAR':
            assert where[i] is None
            where[i], vals[i] = a[0], 0
        elif op == 'ADD':
            j, c = a
            assert where[i] == where[j] == c
            vals[j] ^= vals[i]
        elif op == 'MOVE':
            c, d = a
            assert where[i] == d
            where[i] = c
        elif op == 'SWAP':
            j, = a
            vals[j], vals[i] = vals[i], vals[j]
            where[j], where[i] = where[i], where[j]
        else:
            raise AssertionError(op)
    assert where[:g['public']] == g['start'] and all(x is None for x in where[g['public']:])
    return vals[:g['public']]


def check(graph_path, edit_path):
    assert not sys.flags.optimize
    g = source(graph_path)
    doc = json.loads(Path(edit_path).read_text())
    original = g['program']
    changed = apply(original, doc)
    old_moves = Counter(tuple(r[1:]) for r in original if r[0] == 'MOVE')
    new_moves = Counter(tuple(r[1:]) for r in changed if r[0] == 'MOVE')
    removed = Counter({(2327,326,1):1, (2862,531,1):1, (3152,328,8):1})
    inserted = Counter({(2327,531,1):1, (2862,326,1):1, (3152,328,0):1})
    assert old_moves - new_moves == removed and new_moves - old_moves == inserted
    a, ca = forward(g, original)
    b, cb = forward(g, changed)
    assert a == b and all(a[i] == (1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0)
                          for i in range(630))
    assert len(ca) == len(cb) == 3433 and all(x[2] for x in cb)
    va, vb = adjoint(g, original), adjoint(g, changed)
    assert va == vb and all(((b[j] >> i) & 1) == ((vb[i] >> j) & 1)
                            for i in range(630) for j in range(630))
    ca = {i:(c,x) for i,c,x in ca}
    cb = {i:(c,x) for i,c,x in cb}
    changed_clears = sorted(i for i in ca if ca[i] != cb[i])
    assert changed_clears == [2326,3152,3298,3299,3300]
    return {'source_sha256': SHA, 'original_records':len(original),
            'edited_records':len(changed), 'original_clock_edits':len(doc['edits']),
            'matched_public_rows':len(b), 'independent_transpose_matches':True,
            'removed_moves':[list(x) for x in sorted(removed)],
            'inserted_moves':[list(x) for x in sorted(inserted)],
            'dirty_clears':len(cb), 'changed_clear_owners':changed_clears}


if __name__ == '__main__':
    print(json.dumps(check(sys.argv[1], sys.argv[2]), indent=2, sort_keys=True))

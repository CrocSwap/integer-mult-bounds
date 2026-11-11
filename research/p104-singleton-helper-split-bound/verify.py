"""Independently verify the fixed-word singleton exclusion."""
import argparse
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from pathlib import Path

DIGEST = '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756'
MOD = 1000000007


def read_json(raw):
    def unique(entries):
        result = dict(entries)
        assert len(result) == len(entries), 'Duplicate JSON keys'
        return result

    return json.loads(raw, object_pairs_hook=unique)


def basis(rows):
    pivots = {}
    for row in rows:
        while row and row.bit_length() in pivots:
            row ^= pivots[row.bit_length()]
        assert row
        pivots[row.bit_length()] = row
    return pivots


def contains(pivots, vectors):
    for row in vectors:
        while row and row.bit_length() in pivots:
            row ^= pivots[row.bit_length()]
        if row:
            return False
    return True


def decoded(program):
    for event in program:
        op, dst = event[:2]
        src = event[2] if op in ('ADD', 'COPY') else dst
        coefficient = Fraction(event[-2]) if op in ('ADD', 'COPY', 'SCALE') else None
        if op == 'COPY':
            assert src != dst
        yield op, dst, src, coefficient


def adjust(values, role, amount):
    new = values.get(role, 0) + amount
    if new:
        values[role] = new
    else:
        values.pop(role, None)


def exact(tape, n, cut, role):
    row = {role: Fraction(1)}
    for op, dst, src, q in reversed(tape[:cut+1]):
        c = row.get(dst, 0)
        if not c:
            continue
        if op in ('INIT', 'CLEAR', 'COPY', 'SCALE'):
            del row[dst]
        if q is not None:
            adjust(row, src, c*q)
    row = {r:q for r,q in row.items() if r < n}
    column = {role: Fraction(1)}
    for op, dst, src, q in tape[cut+1:]:
        c = column.get(src, 0)
        if op in ('INIT', 'CLEAR', 'COPY', 'SCALE'):
            column.pop(dst, None)
        if q is not None and c:
            adjust(column, dst, c*q)
    return row, column


def control():
    def singleton(program, cut=0):
        row, column = exact(list(decoded(program)), 2, cut, 0)
        return row == {0:Fraction(2)} and column == {0:Fraction(1,2)}

    pre = ['SCALE', 0, '2', 0]
    post = ['SCALE', 0, '1/2', 0]
    assert singleton([pre, post])
    assert not singleton([['ADD', 1, 0, '1', 0], pre, post, ['ADD', 1, 0, '-1', 0]], 1)
    assert not singleton([['ADD', 0, 1, '1', 0], pre, post, ['ADD', 0, 1, '-1', 0]], 1)
    return ['UNIT_RECIPROCAL_POSITIVE', 'SUFFIX_CONTAMINATION_REJECTED',
            'PREFIX_CONTAMINATION_REJECTED']


def run(word, expected):
    program, n = word['program'], word['public']
    tape = list(decoded(program))
    main = set(word['live']) | {r+112 for r in word['live']}
    main.update(word['hosted']['X2'])
    main.update(word['hosted']['Y2'])
    charts = word['frames']
    pivots = list(map(basis, charts))
    dims = list(map(len, charts))

    @cache
    def strict(a, b):
        return dims[a] < dims[b] and contains(pivots[b], charts[a])

    @cache
    def probe(role):
        raw = sha256(f'singleton independent {role}'.encode()).digest()
        return int.from_bytes(raw[:8], 'big') % MOD

    @cache
    def reduced(q):
        return q.numerator * pow(q.denominator, -1, MOD) % MOD

    def update(vector, entry):
        op, d, s, q = entry
        if op in ('CLEAR', 'INIT'):
            vector[d] = 0
        elif op in ('ADD', 'COPY', 'SCALE'):
            extra = vector[d] if op == 'ADD' else 0
            vector[d] = (extra + vector[s]*reduced(q)) % MOD

    owned = word['owned_fields']
    values = [probe(role) for role in range(n)] + [0]*owned
    ones = [1]*n + [0]*owned
    chart = word['initial'] + [None]*owned
    marked = []
    signatures = set()
    cuts = 0
    for t, (event, entry) in enumerate(zip(program,tape,strict=True)):
        op, d, s, _ = entry
        if op == 'MOVE':
            assert chart[d] == event[2]
            chart[d] = event[3]
        elif op == 'INIT':
            assert chart[d] is None
            chart[d] = event[2]
        elif op == 'CLEAR':
            assert chart[d] == event[2]
            chart[d] = None
        else:
            assert chart[d] == chart[s] == event[-1]
        update(values, entry)
        update(ones, entry)
        for role in {d,s}:
            if role in main or role >= n:
                continue
            u, f, v = word['initial'][role], chart[role], word['final'][role]
            if strict(u,f) and strict(f,v):
                signatures.add((u,f,v))
                cuts += 1
                if values[role] == ones[role]*probe(role) % MOD:
                    marked.append((t,role))
    assert chart == word['final'] + [None]*owned
    assert len(main) == 400 and n-len(main) == 1101
    assert len(signatures) == expected['selected_signatures'] == expected['signatures'] == 1396
    assert cuts == expected['selected_cuts'] == expected['representative_cuts'] == 11489
    assert expected['projection_survivors'] == expected['unresolved_exact'] == 0

    bad_prefix = bad_suffix = 0
    for t, role in marked:
        row, column = exact(tape, n, t, role)
        if set(row) != {role}:
            bad_prefix += 1
        else:
            assert column != {role:1/row[role]}, (t,role)
            bad_suffix += 1
    return {'dependencies':{'complex/source/inputs/WORD.json.gz':DIGEST},
            'status':'PASS_FIXED_WORD_SINGLETON_EXCLUSION',
            'representatives':cuts,'signatures':len(signatures),'different_prime':MOD,
            'rational_reject_prefix':bad_prefix,'rational_reject_suffix':bad_suffix,
            'rational_checks':len(marked),'controls':control()}


if __name__ == '__main__':
    assert __debug__
    parser = argparse.ArgumentParser()
    parser.add_argument('word', type=Path)
    parser.add_argument('receipt', type=Path)
    a = parser.parse_args()
    raw = a.word.read_bytes()
    assert sha256(raw).hexdigest() == DIGEST, 'Changed source word'
    receipt = a.receipt.read_bytes()
    answer = run(read_json(gzip.decompress(raw)),read_json(receipt))
    answer['dependencies']['interface/CONTINUATION.json'] = sha256(receipt).hexdigest()
    print(json.dumps(answer,sort_keys=True,indent=2))

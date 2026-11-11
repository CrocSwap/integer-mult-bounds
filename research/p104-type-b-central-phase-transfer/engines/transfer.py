"""Exact column and row transport for Type B central-axis transfers."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
from json import dumps, loads
from pathlib import Path
from time import monotonic

CALLER_SHA = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'


def basis(count, role):
    return [Fraction(i == role) for i in range(count)]


def odd_sign(exponent):
    return Fraction(1 if exponent % 2 == 0 else -1)


def at_unit_body(event, offset):
    if event[0] == 'J':
        s, t, alpha, beta = event[3]
        a, b = -Fraction(alpha), -Fraction(beta)
        return 'plane', s - offset, t - offset, (Fraction(1), a, b, 1 + a * b)
    if event[0] != 'B':
        return None
    _, op, r, *args = event
    r -= offset
    if op == 'SWAP':
        return 'swap', r, args[0] - offset, None
    if op in {'QUERY', 'ADD'}:
        coeff = odd_sign(args[1]) if op == 'QUERY' else Fraction(args[1])
        return 'add', r, args[0] - offset, coeff
    if op == 'IDLE_ODD':
        return 'scale', r, None, odd_sign(args[1])
    if op == 'SCALE':
        return 'scale', r, None, Fraction(args[0])
    assert op in {'IDLE_ONE', 'LAMBDA'}
    return None


def apply(vector, gate, transpose=False):
    op, r, s, coeff = gate
    if op == 'swap':
        vector[r], vector[s] = vector[s], vector[r]
    elif op == 'scale':
        vector[r] *= coeff
    elif op == 'add':
        dest, source = (s, r) if transpose else (r, s)
        vector[dest] += coeff * vector[source]
    else:
        assert op == 'plane'
        a, b, c, d = coeff
        if transpose:
            b, c = c, b
        vector[r], vector[s] = a * vector[r] + b * vector[s], c * vector[r] + d * vector[s]


def cross_support(gates, count, source, target):
    column = basis(count, source)
    row = basis(count, target)
    for gate in gates:
        apply(column, gate)
    for gate in reversed(gates):
        apply(row, gate, transpose=True)
    assert row[source] == column[target]
    return (
        tuple(i for i, x in enumerate(column) if i != target and x),
        tuple(i for i, x in enumerate(row) if i != source and x),
    )


def controls():
    assert cross_support([('swap', 0, 1, None)], 2, 0, 1) == ((), ())
    assert cross_support([('add', 1, 0, Fraction(-2))], 2, 0, 0) == ((1,), ())
    assert cross_support([('add', 0, 1, Fraction(2))], 2, 0, 0) == ((), (1,))
    assert cross_support([('scale', 1, None, Fraction(-1))], 2, 0, 1) == ((0,), (1,))


def run(caller, seconds):
    start = monotonic()
    kind = caller['types']['B']
    offset, count = kind['offset'], kind['roles']
    events = caller['events']
    gates = [at_unit_body(e, offset) for e in events]
    odd = [(i, e[2] - offset, tuple(e[3])) for i, e in enumerate(events) if e[:2] == ['B', 'IDLE_ODD']]
    even = [(i, e[2] - offset, tuple(e[3])) for i, e in enumerate(events)
            if e[:2] == ['B', 'IDLE_ONE'] and len(e[3]) >= 2]
    assert len(odd) == 4 and len(even) == 26 and len(kind['ports']) == 8
    assert all(len(mask) == 1 for _, _, mask in odd)
    cases = list(product(odd, even))
    all_gates = tuple(gate for gate in gates if gate is not None)
    assert len(cases) == 104
    for role, diagonal in enumerate(kind['diagonal']):
        column = basis(count, role)
        for gate in all_gates:
            apply(column, gate)
        assert column == [v * odd_sign(diagonal[0]) for v in basis(count, role)]
    rows = []
    for first, second in cases:
        if monotonic() - start >= seconds:
            break
        (lo, source, _), (hi, target, _) = sorted((first, second))
        interior = [gate for gate in gates[lo+1:hi] if gate is not None]
        column, row = cross_support(interior, count, source, target)
        rows.append({
            'odd': first[0], 'even': second[0], 'supports': not column and not row,
            'column_off_axis': [i + offset for i in column], 'row_off_axis': [i + offset for i in row],
            'disjoint_stage_masks': set(first[2]).isdisjoint(second[2]),
        })
    return {
        'caller_sha256': CALLER_SHA,
        'tested': len(rows),
        'survivors': sum(row['supports'] for row in rows),
        'controls': 4,
        'counts_by_support': dict(Counter(str(row['supports']).lower() for row in rows)),
        'records': rows,
        'unvisited': [[a[0], b[0]] for a, b in cases[len(rows):]],
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('caller', nargs='?', type=Path)
    parser.add_argument('--seconds', type=float, default=25)
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    controls()
    if args.controls_only:
        return
    raw = args.caller.read_bytes()
    if sha256(raw).hexdigest() != CALLER_SHA:
        raise ValueError('Changed signed caller')
    print(dumps(run(loads(raw), args.seconds), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

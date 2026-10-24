#!/usr/bin/env python3
"""Check the three-call unit interface and a three-field dyadic code."""

from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIN = '86c87e8080c305c605541d70afc523b8ff65a94cbf2bc9e134289984d86f1f6e'
PROGRAM = [('F', 1), ('X', 1), ('Y', -2), ('B', 2),
           ('X', -2), ('Y', 3), ('F', 3), ('X', 2)]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def word(items):
    out = []
    for item in items:
        if out and out[-1] == -item:
            out.pop()
        else:
            out.append(item)
    return tuple(out)


def left(symbol, row):
    return {(source, word((symbol,) + path)): value
            for (source, path), value in row.items()}


def add(a, b, scale=1):
    out = dict(a)
    for key, value in b.items():
        value = out.get(key, 0) + scale * value
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    return out


def replay(program, raw=False):
    x, y = {(0, (-4,) if raw else ()): F(1)}, {(1, ()): F(1)}
    for kind, symbol in program:
        if kind == 'F':
            y = add(y, left(symbol, x))
        elif kind == 'B':
            x = add(x, left(symbol, y), -1)
        elif kind == 'X':
            x = left(symbol, x)
        else:
            need(kind == 'Y', 'Known code kind')
            y = left(symbol, y)
    return x, y


GATES = [('add', 0, 1, F(1)), ('add', 0, 2, F(1)),
         ('add', 1, 0, F(-1)), ('add', 2, 0, F(-1)),
         ('scale', 0, 0, F(-2)), ('add', 0, 1, F(-1)),
         ('add', 0, 2, F(-1))]


def apply(gates, rows=None):
    rows = [{i: F(1)} for i in range(3)] if rows is None else list(rows)
    for kind, target, source, coefficient in gates:
        if kind == 'scale':
            rows[target] = {j: coefficient * c for j, c in rows[target].items()}
        else:
            rows[target] = add(rows[target], rows[source], coefficient)
    return rows


def main():
    prior = HERE.parent / 'one-pair-current-codes-20261018/ONE-PAIR.md'
    need(sha256(prior.read_bytes()).hexdigest() == PIN, 'Frozen predecessor scope')
    expected = ({(1, ()): -1}, {(0, (3, -2, 1)): 1})
    need(replay(PROGRAM) == expected, 'Generic ordered endpoint')
    rejected = []
    for i, (kind, _) in enumerate(PROGRAM):
        if kind in ('X', 'Y'):
            need(replay(PROGRAM[:i] + PROGRAM[i+1:]) != expected, 'Omitted code control')
            rejected.append(i)
    x, y = replay(PROGRAM, raw=True)
    final_x = left(4, left(4, left(-4, y)))
    final_y = {key: -value for key, value in x.items()}
    need(final_x == {(0, (4, 3, -2, 1, -4)): 1}
         and final_y == {(1, ()): 1}, 'Exact physical Q boundary')
    for symbol in (-4, -3, 2, -1, 4):
        final_x = left(symbol, final_x)
    need(final_x == {(0, ()): 1}, 'Direct physical inverse order')
    inverse = [(kind, target, source, 1/c if kind == 'scale' else -c)
               for kind, target, source, c in reversed(GATES)]
    identity = [{i: F(1)} for i in range(3)]
    c = [{j: F(-1) for j in range(3) if j != i} for i in range(3)]
    ci = [{j: F(int(i == j)) - F(1, 2) for j in range(3)} for i in range(3)]
    need(apply(GATES) == c and apply(inverse) == ci, 'All scalar code columns')
    need(apply(inverse, c) == apply(GATES, ci) == identity, 'Both scalar inverse orders')
    receipt = {
        'status': 'PASS_ONE_PAIR_GENERAL_UNITS',
        'predecessor_proof_sha256': PIN,
        'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'proof_sha256': sha256((HERE / 'GENERAL-UNITS.md').read_bytes()).hexdigest(),
        'program': PROGRAM,
        'content_endpoint': ['-y', 'E2 G1^-1 E0 x'],
        'physical_raw_output': ['Q E2 G1^-1 E0 Q^-1', 'I'],
        'omitted_code_controls': rejected,
        'three_field_code': {'input_columns_checked': 3, 'inverse_orders_checked': 2,
                             'unit_adds': 6, 'signed_factor_two_scales': 1,
                             'real_scalar_primitives_each_direction': 52,
                             'owned_or_borrowed_fields': 0},
        'native_or_host_claimed': False,
    }
    (HERE / 'CHECKS.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()

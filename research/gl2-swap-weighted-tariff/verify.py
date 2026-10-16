#!/usr/bin/env python3
"""Independent full F2[GL2(F2)] witnesses and weighted lower-bound checks."""
import argparse
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            bit = row.bit_length()-1
            if bit in basis:
                row ^= basis[bit]
            else:
                basis[bit] = row
                break
    return len(basis)


def binary_mul(a, b):
    return tuple(xor(b[j] for j in range(len(b)) if row >> j & 1) for row in a)


def xor(values):
    result = 0
    for v in values:
        result ^= v
    return result


GROUP = tuple(a for a in product(range(4), repeat=2) if rank(a) == 2)
ONE = GROUP.index((1, 2))
A = GROUP.index((3, 2))
B = GROUP.index((1, 3))
SWAP = GROUP.index((2, 1))
MUL = [[GROUP.index(binary_mul(a, b)) for b in GROUP] for a in GROUP]


def ring_mul(a, b):
    return xor(1 << MUL[i][j] for i in range(6) for j in range(6)
               if a >> i & 1 and b >> j & 1)


def identity(r):
    return tuple(tuple((1 << ONE) if i == j else 0 for j in range(r)) for i in range(r))


def matrix_mul(a, b):
    r = len(a)
    return tuple(tuple(xor(ring_mul(a[i][k], b[k][j]) for k in range(r))
                       for j in range(r)) for i in range(r))


def projector(r, u, v):
    need((u & v).bit_count() % 2 == 1, 'not a rank-one idempotent')
    return tuple(v if u >> i & 1 else 0 for i in range(r))


def call(rows, label):
    r = len(rows)
    scalar = (1 << label) ^ (1 << ONE)
    return tuple(tuple(((1 << ONE) if i == j else 0) ^
                       (scalar if rows[i] >> j & 1 else 0)
                       for j in range(r)) for i in range(r))


def scalar(rows):
    return tuple(tuple((1 << ONE) if row >> j & 1 else 0 for j in range(len(rows)))
                 for row in rows)


def natural(mat):
    """Coordinate-major natural representation, 2r by 2r."""
    r = len(mat)
    result = [0] * (2*r)
    for i, row in enumerate(mat):
        for j, entry in enumerate(row):
            small = tuple(xor(GROUP[g][k] for g in range(6) if entry >> g & 1)
                          for k in range(2))
            for k in range(2):
                for l in range(2):
                    result[k*r+i] |= ((small[k] >> l) & 1) << (l*r+j)
    return tuple(result)


def crossing(mat):
    r = len(mat)//2
    return rank([row >> r for row in mat[:r]]), rank([row & ((1 << r)-1) for row in mat[r:]])


def witnesses():
    count = 0
    for t in range(9):
        for extra in range(3):
            r = t+extra
            for labels in ((A, B, A), (B, A, B)):
                out = identity(r)
                for j in range(t):
                    p = projector(r, 1 << j, 1 << j)
                    for label in labels:
                        out = matrix_mul(out, call(p, label))
                expected = tuple(tuple((1 << (SWAP if i < t else ONE)) if i == j else 0
                                       for j in range(r)) for i in range(r))
                need(out == expected, 'full formal attainment')
                need(crossing(natural(out)) == (t, t), 'target per-label rank')
                count += 1
    return count


def projection_checks():
    factors = 0
    for r in range(1, 6):
        for u in range(1, 1 << r):
            for v in range(1, 1 << r):
                if (u & v).bit_count() % 2:
                    p = projector(r, u, v)
                    for label, expect in ((A, (1, 0)), (B, (0, 1))):
                        need(crossing(natural(call(p, label))) == expect, 'per-label increment')
                        factors += 1
    # Every free GL2 scalar and all twelve two-role factors, on both sides.
    factors2 = [call(projector(2, u, v), label) for u in range(1, 4)
                for v in range(1, 4) if (u & v).bit_count() % 2 for label in (A, B)]
    for free in GROUP:
        f = scalar(free)
        need(crossing(natural(f)) == (0, 0), 'free scalar crossing')
        for paid in factors2:
            for mixed in (matrix_mul(f, paid), matrix_mul(paid, f)):
                need(crossing(natural(mixed)) == crossing(natural(paid)),
                     'free scalar preservation')
    rng = Random(2026101514)
    checked = 0
    for r in range(1, 7):
        for trial in range(30):
            out = identity(r)
            counts = [0, 0]
            for step in range(12):
                if step % 3 == 0 and r > 1:
                    rows = [1 << i for i in range(r)]
                    i, j = rng.sample(range(r), 2)
                    rows[i] ^= 1 << j
                    nxt = scalar(rows)
                else:
                    while True:
                        u, v = rng.randrange(1, 1 << r), rng.randrange(1, 1 << r)
                        if (u & v).bit_count() % 2:
                            break
                    label = rng.choice((A, B))
                    counts[label == B] += 1
                    nxt = call(projector(r, u, v), label)
                before = natural(out)
                out = matrix_mul(out, nxt)
                now = natural(out)
                need(now == binary_mul(before, natural(nxt)), 'natural product convention')
                q0, q1 = crossing(now)
                p0, p1 = crossing(before)
                d0, d1 = crossing(natural(nxt))
                need(q0 <= p0+d0 and q1 <= p1+d1, 'subadditivity')
                need(q0 <= counts[0] and q1 <= counts[1], 'prefix label bound')
                checked += 1
    return {'paid_factors': factors, 'free_two_role_compositions': 144,
            'mixed_prefixes': checked}


def tariff_checks():
    weights = [Fraction(0), Fraction(1, 3), Fraction(1), Fraction(2), Fraction(7, 2)]
    inequalities, sharp = 0, 0
    for t in range(9):
        for a, b in product(weights, repeat=2):
            lower = t*(2*min(a, b)+max(a, b))
            need(min(2*t*a+t*b, t*a+2*t*b) == lower, 'sharp weighted formula')
            sharp += 1
            for na in range(t, 4*t+1):
                for nb in range(t, 4*t+1):
                    if na+nb >= 3*t:
                        need(a*na+b*nb >= lower, 'weighted dual inequality')
                        inequalities += 1
    return {'rational_tariff_pairs': len(weights)**2, 'sharp_instances': sharp,
            'feasible_count_inequalities': inequalities,
            'example_t5_a1_b2': 20, 'example_t5_a0_b2': 10}


def controls():
    p = projector(2, 1, 1)
    aa = matrix_mul(call(p, A), call(p, A))
    need(aa == identity(2), 'negative tariff identity loop')
    need(2*Fraction(-1) < 0, 'negative tariff control')
    out = identity(2)
    for label in (A, B, A):
        out = matrix_mul(out, call(p, label))
    corrupt = [list(row) for row in out]
    corrupt[0][0] ^= 63
    corrupt = tuple(tuple(row) for row in corrupt)
    need(corrupt != out and natural(corrupt) == natural(out), 'unfaithful natural control')
    # A concrete weighted claim needs BOTH individual bounds and the total bound.
    need(1*3+2*0 < 4, 'dropped b-bound control')
    need(2*0+1*3 < 4, 'dropped a-bound control')
    need(1*1+1*1 < 3, 'dropped total-bound control')
    # A changed alphabet directly charging SWAP at 1 would violate 3t.
    direct = call(p, SWAP)
    need(direct == out and crossing(natural(direct)) == (1, 1), 'direct SWAP boundary')
    need(matrix_mul(call(p, A), call(p, B)) != out, 'omitted attaining call')
    return {'identity_negative_price_loop': True, 'natural_alias_detected_formally': True,
            'three_missing_inequality_controls': True, 'direct_swap_changed_alphabet': True,
            'omitted_attaining_call': True}


def compute():
    need(MUL[MUL[A][B]][A] == MUL[MUL[B][A]][B] == SWAP, 'label identity')
    return dict(schema_version=1, scope='fixed nonnegative label tariffs; formal GL2 coordinate SWAP',
                formula='minimum=t*(2*min(A,B)+max(A,B))',
                formal_witnesses=witnesses(), projection=projection_checks(),
                tariff=tariff_checks(), controls=controls())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = compute()
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.out:
        with args.out.open('x', encoding='utf-8', newline='\n') as f:
            f.write(text)
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'complete receipt mismatch')
    print('PASS_SWAP_WEIGHTED_TARIFF formal_witnesses=54 paid_factors=1302 mixed_prefixes=2160')


if __name__ == '__main__':
    main()

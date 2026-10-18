#!/usr/bin/env python3
"""Exact d=4 commutant witness, written without importing candidate code.

DLamdata with OpenAI Codex assistance, including a separate verifier agent.
Apache-2.0.

This finite rational witness corroborates an algebraic step; it does not
establish the theorem for all complex representations.
"""
from fractions import Fraction as Q
import argparse
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum((x * y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def rref(rows, columns):
    a = [[Q(x) for x in row] for row in rows]
    pivots = []
    for col in range(columns):
        k = len(pivots)
        pivot = next((i for i in range(k, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[k], a[pivot] = a[pivot], a[k]
        divisor = a[k][col]
        a[k] = [x / divisor for x in a[k]]
        for i in range(len(a)):
            if i != k and a[i][col]:
                factor = a[i][col]
                a[i] = [x - factor * y for x, y in zip(a[i], a[k])]
        pivots.append(col)
    return a, pivots


def inverse(a):
    n = len(a)
    rr, pivots = rref([r + s for r, s in zip(a, identity(n))], n)
    need(len(pivots) == n, 'singular basis')
    return [r[n:] for r in rr]


def flatten(a):
    return [x for row in a for x in row]


def span_rank(matrices):
    return len(rref([flatten(m) for m in matrices], len(matrices[0]) ** 2)[1])


def centralizer(generators):
    """Solve all entries of M G - G M=0 over Q, with no ansatz on M."""
    n = len(generators[0])
    equations = []
    for g in generators:
        for i in range(n):
            for j in range(n):
                row = [Q(0)] * (n * n)
                for k in range(n):
                    row[i * n + k] += g[k][j]
                    row[k * n + j] -= g[i][k]
                equations.append(row)
    rr, pivots = rref(equations, n * n)
    basis = []
    for free in sorted(set(range(n * n)) - set(pivots)):
        vector = [Q(0)] * (n * n)
        vector[free] = Q(1)
        for k, pivot in enumerate(pivots):
            vector[pivot] = -rr[k][free]
        basis.append([vector[i * n:(i + 1) * n] for i in range(n)])
    return basis


def tensor(a, b):
    return [[x * y for x in ra for y in rb] for ra in a for rb in b]


def same_span(a, b):
    return span_rank(a) == span_rank(b) == span_rank(a + b)


def run():
    z = [[Q(1), Q(0)], [Q(0), Q(-1)]]
    x = [[Q(0), Q(1)], [Q(1), Q(0)]]
    s = [[Q(v) for v in row] for row in
         [[1, 1, 1, 1], [0, 1, 2, 3], [0, 0, 1, 4], [0, 0, 0, 1]]]
    sinv = inverse(s)
    conjugate = lambda m: multiply(multiply(s, m), sinv)
    a, b = [conjugate(tensor(m, identity(2))) for m in (z, x)]
    c, d = [conjugate(tensor(identity(2), m)) for m in (z, x)]
    unit = identity(4)
    for first, second in ((a, b), (c, d)):
        need(multiply(first, first) == multiply(second, second) == unit,
             'involution relation')
        neg = [[-v for v in row] for row in multiply(second, first)]
        need(multiply(first, second) == neg, 'Weyl relation')
    need(multiply([list(row) for row in zip(*a)], a) != unit,
         'fixture accidentally unitary')
    alg0 = [unit, a, b, multiply(a, b)]
    alg1 = [unit, c, d, multiply(c, d)]
    cent0 = centralizer([a, b])
    cent1 = centralizer([c, d])
    double0 = centralizer(cent0)
    common = centralizer([a, b, c, d])
    need(same_span(cent0, alg1) and same_span(cent1, alg0),
         'complementary commutants')
    need(same_span(double0, alg0), 'double commutant')
    need(same_span(common, [unit]), 'intersection must be scalar')
    need(span_rank([multiply(p, q) for p in alg0 for q in alg1]) == 16,
         'joint algebra is not all M4')
    drop_one = len(centralizer([a]))
    drop_neighbor = len(centralizer([a, b]))
    need(drop_one == 8, 'dropping B must enlarge centralizer')
    need(drop_neighbor == 4, 'dropping one neighbor must leave M2')
    # Multiplicity three exposes the dimension-four premise: its commutant
    # has dimension nine, so a neighboring four-dimensional algebra need
    # not exhaust it. No claim about a valid d=6 crossing edge is made.
    multiplicity_three = len(centralizer([tensor(z, identity(3)),
                                        tensor(x, identity(3))]))
    need(multiplicity_three == 9, 'multiplicity-three commutant')
    result = {
        'status': 'PASS_EXACT_NONUNITARY_D4_COMMUTANT',
        'arithmetic': 'Fraction exact rational RREF on unrestricted matrix entries',
        'candidate_imports': [],
        'dimension': 4,
        'algebra_dimensions': [span_rank(alg0), span_rank(alg1)],
        'commutant_dimensions': [len(cent0), len(cent1)],
        'double_commutant_dimension': len(double0),
        'common_commutant_dimension': len(common),
        'joint_algebra_dimension': 16,
        'nonunitary_generator': True,
        'failure_controls': {
            'drop_B_centralizer_dimension': drop_one,
            'drop_second_neighbor_centralizer_dimension': drop_neighbor,
            'd6_single_pair_centralizer_dimension': multiplicity_three,
        },
        'limitation': 'Finite witness only; all-GL result rests on the written proof',
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = run()
    if not args.emit:
        expected = json.loads(Path(__file__).with_name('COMMUTANT.json').read_text())
        need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
             'commutant receipt mismatch')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

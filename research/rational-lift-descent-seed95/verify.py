"""Exact finite evidence for PROOF.md, Python >=3.10, standard library only.

The uniform theorem is a written proof. This checker verifies its displayed
quadratic-extension examples, finite avoidance bound, and F4 boundary.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZERO = (Q(0), Q(0))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def scale(c, x):
    return (c * x[0], c * x[1])


def mul(x, y, d):
    return (x[0] * y[0] + d * x[1] * y[1],
            x[0] * y[1] + x[1] * y[0])


def inverse(x, d):
    norm = x[0] ** 2 - d * x[1] ** 2
    require(norm != 0, 'zero inverse')
    return (x[0] / norm, -x[1] / norm)


def image(x, a):
    return [tuple(sum(row[j] * a[j][h] for j in range(len(a)))
                  for h in range(2)) for row in x]


def signature(x, a, z, d):
    xa = image(x, a)
    residual = [[add((c, Q(0)), scale(-1, mul(a[j], z[i], d)))
                 for j, c in enumerate(row)] for i, row in enumerate(x)]
    return {'a': [v != ZERO for v in a], 'z': [v != ZERO for v in z],
            'Xa': [v != ZERO for v in xa],
            'residual': [[v != ZERO for v in row] for row in residual]}


def projection(x, a, z, d, omit=None, direct=False):
    groups = {'a': list(a), 'Xa': image(x, a), 'inverse': [], 'residual': []}
    for i, v in enumerate(z):
        if v != ZERO:
            iz = inverse(v, d)
            groups['inverse'].append(iz)
            groups['residual'].extend(add(a[j], scale(-c, iz))
                                      for j, c in enumerate(x[i]))
    values = {v for k, group in groups.items() if k != omit
              for v in group if v != ZERO}
    t = next(t for t in range(len(values) + 1)
             if all(v[0] + t * v[1] != 0 for v in values))
    f = lambda v: v[0] + t * v[1]
    b = [f(v) for v in a]
    w = [Q(0) if v == ZERO else f(v) if direct else 1 / f(inverse(v, d))
         for v in z]
    return b, w, t, len(values)


def check_witness(x, a, z, d, b, w):
    require(d in (-1, 2), 'unsupported example field')
    require(len(a) > 0 and len(z) == len(x) and
            all(len(row) == len(a) for row in x), 'dimensions')
    require(len(b) == len(a) and len(w) == len(z), 'witness dimensions')
    expected = signature(x, a, z, d)
    # Evaluate the rational side directly, without extension multiplication.
    xb = [sum(c * b[j] for j, c in enumerate(row)) for row in x]
    actual = {'a': [v != 0 for v in b], 'z': [v != 0 for v in w],
              'Xa': [v != 0 for v in xb],
              'residual': [[c - b[j] * w[i] != 0
                            for j, c in enumerate(row)] for i, row in enumerate(x)]}
    require(actual == expected, 'support mismatch')
    # Check every entry of both complete rank-one identities.
    xa = image(x, a)
    for i, row in enumerate(x):
        for k, target in enumerate(x):
            gram = sum(c * target[j] for j, c in enumerate(row))
            rational = sum(c * (target[j] - b[j] * w[k])
                           for j, c in enumerate(row)) + xb[i] * w[k]
            extension = mul(xa[i], z[k], d)
            for j, c in enumerate(row):
                extension = add(extension, scale(c, add((target[j], Q(0)),
                                        scale(-1, mul(a[j], z[k], d)))))
            require(rational == gram and extension == (gram, Q(0)), 'identity')
    return expected


def fixture(name, d, x, a, z):
    return (name, d, [[Q(v) for v in row] for row in x],
            [tuple(Q(c) for c in v) for v in a],
            [tuple(Q(c) for c in v) for v in z])


FIXTURES = [
    fixture('zero', 2, [[0]], [(0, 0)], [(0, 0)]),
    fixture('sqrt2-cancellation', 2, [[1]], [(0, 1)], [(0, '1/2')]),
    fixture('sqrt2-zero-total', 2, [[1, 1], [1, -1]],
            [(0, 1), (0, -1)], [(0, '1/2'), (0, 0)]),
    fixture('sqrt2-rectangular', 2, [[1, 2], [-1, 1], [0, 1]],
            [(1, 1), (-2, 1)], [(0, 1), ('1/2', 1), (0, 0)]),
    fixture('complex-cancellation', -1, [[1]], [(0, 1)], [(0, -1)]),
    fixture('residual-guard', -1, [[1]], [(1, 1)], [(1, 0)]),
    fixture('total-guard', -1, [[1, 1]], [(1, 1), (-1, 1)], [(0, 0)]),
    fixture('coefficient-guard', -1, [[0]], [(0, 1)], [(0, 0)]),
    fixture('inverse-guard', -1, [[0]], [(1, 0)], [(0, 1)]),
]


def rejected(fn):
    try:
        fn()
    except (ValueError, ZeroDivisionError):
        return True
    return False


def finite_field_boundary():
    def multiply(x, y):
        raw = (x if y & 1 else 0) ^ (x << 1 if y & 2 else 0)
        return raw ^ (7 if raw & 4 else 0)
    require(all(multiply(v, 1) == v for v in range(4)), 'F4 units')
    require(all(any(multiply(v, u) == 1 for u in range(1, 4))
                for v in range(1, 4)), 'F4 inverses')
    require(multiply(2, 2) == 3 and (1 ^ multiply(2, 2)) == 2, 'F4 example')
    require((2 ^ multiply(2, 2)) == 1, 'F4 complete identity')
    candidates = [(b, w) for b, w in product(range(2), repeat=2)
                  if b != 0 and w != 0 and (1 ^ (b * w)) != 0]
    require(candidates == [], 'unexpected F2 witness')
    return {'F4_a': 2, 'F4_z': 2, 'F4_residual': 2,
            'F2_pairs_exhausted': 4, 'F2_witnesses': 0}


def evidence():
    records = []
    for name, d, x, a, z in FIXTURES:
        b, w, t, n = projection(x, a, z, d)
        supports = check_witness(x, a, z, d, b, w)
        records.append({'name': name, 'D': d, 't': t, 'N': n,
                        'b': list(map(str, b)), 'w': list(map(str, w)),
                        'supports': supports})
    grid = [tuple(map(Q, pair)) for pair in product((-1, 0, 1), repeat=2)]
    counts = {}
    for d in (-1, 2):
        patterns = set()
        for a, z in product(grid, repeat=2):
            b, w, _, _ = projection([[Q(1)]], [a], [z], d)
            s = check_witness([[Q(1)]], [a], [z], d, b, w)
            patterns.add(json.dumps(s, sort_keys=True))
        counts[str(d)] = {'lifts_checked': 81, 'support_patterns': len(patterns)}
    controls = []
    for index, group, direct in [(4, None, True), (5, 'residual', False),
                                  (6, 'Xa', False), (7, 'a', False),
                                  (8, 'inverse', False)]:
        name, d, x, a, z = FIXTURES[index]
        def run():
            b, w, _, _ = projection(x, a, z, d, omit=group, direct=direct)
            check_witness(x, a, z, d, b, w)
        require(rejected(run), 'negative control admitted: ' + name)
        controls.append(name)
    # Three degree-two exclusion polynomials cover 0,...,5; t=6 is allowed.
    rows = [(0, -1, 1), (6, -5, 1), (20, -9, 1)]
    allowed = [t for t in range(7) if all(sum(c * t ** j for j, c in enumerate(r))
                                        != 0 for r in rows)]
    require(allowed == [6], 'polynomial avoidance bound')
    return {'status': 'PASS_RATIONAL_LIFT_DESCENT', 'witnesses': records,
            'scalar_grid': counts, 'rejected_controls': controls,
            'avoidance': {'N': 3, 'D': 3, 'bound': 6, 'first_allowed': 6},
            'finite_field_boundary': finite_field_boundary(), 'new_kappa': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print recomputed certificate')
    args = parser.parse_args()
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    root = HERE.parents[1]
    for path, expected in sources['files'].items():
        require(sha256((root / path).read_bytes()).hexdigest() == expected,
                'source pin: ' + path)
    actual = evidence()
    if args.emit:
        print(json.dumps(actual, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE / 'CERTIFICATE.json').read_text(encoding='utf-8'))
        require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
                'certificate mismatch')
        print('PASS_RATIONAL_LIFT_DESCENT witnesses=9 scalar_lifts=162 '
              'controls=5 finite_field_pairs=4 new_kappa=false')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Exact finite corroboration of the changed-coupling cycle theorem.

Produced by Nick Petalas. Apache-2.0. Only the standard library is used.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path

MAX_BANKS = 13
MAX_INTERNAL = 2
SOURCE_NAMES = ('README.md', 'SOURCES.json', 'TASK.json', 'VERIFY.json', 'verify.py')
type Matrix = tuple[tuple[F, ...], ...]
type Poly = tuple[F, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def eye(n: int) -> Matrix:
    require(1 <= n <= MAX_BANKS * MAX_INTERNAL, 'matrix dimension')
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def transpose(a: Matrix) -> Matrix:
    return tuple(zip(*a))


def multiply(a: Matrix, b: Matrix) -> Matrix:
    bt = transpose(b)
    return tuple(tuple(sum((x * y for x, y in zip(row, col)), F(0))
                       for col in bt) for row in a)


def scaled(a: Matrix, c: F) -> Matrix:
    return tuple(tuple(c * x for x in row) for row in a)


def add(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(x + y for x, y in zip(ar, br)) for ar, br in zip(a, b))


def trace(a: Matrix) -> F:
    return sum((a[i][i] for i in range(len(a))), F(0))


def trim(p: Poly) -> Poly:
    q = list(p)
    for _ in range(len(q) - 1):
        if q[-1]:
            break
        q.pop()
    return tuple(q)


def padd(p: Poly, q: Poly) -> Poly:
    n = max(len(p), len(q))
    return trim(tuple((p[i] if i < len(p) else F(0)) +
                      (q[i] if i < len(q) else F(0)) for i in range(n)))


def pscale(p: Poly, c: F) -> Poly:
    return trim(tuple(x * c for x in p))


def pmul(p: Poly, q: Poly) -> Poly:
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            out[i + j] += x * y
    return trim(tuple(out))


def peval(p: Poly, x: F) -> F:
    out = F(0)
    for c in reversed(p):
        out = out * x + c
    return out


def pdiv(p: Poly, q: Poly) -> tuple[Poly, Poly]:
    require(q != (F(0),), 'zero polynomial divisor')
    rem = list(p)
    out = [F(0)] * max(1, len(p) - len(q) + 1)
    for _ in range(max(0, len(p) - len(q) + 1)):
        rem = list(trim(tuple(rem)))
        if len(rem) < len(q) or rem == [F(0)]:
            break
        k, c = len(rem) - len(q), rem[-1] / q[-1]
        out[k] = c
        for j, a in enumerate(q):
            rem[j + k] -= c * a
    return trim(tuple(out)), trim(tuple(rem))


def derivative(p: Poly) -> Poly:
    return trim(tuple(F(i) * p[i] for i in range(1, len(p))) or (F(0),))


def squarefree(p: Poly) -> Poly:
    a, b = p, derivative(p)
    for _ in range(len(p)):
        if b == (F(0),):
            break
        _, rem = pdiv(a, b)
        a, b = b, rem
    require(b == (F(0),), 'polynomial gcd budget')
    q, rem = pdiv(p, a)
    require(rem == (F(0),), 'squarefree exact division')
    return pscale(q, 1 / q[-1])


def sturm(p: Poly) -> tuple[Poly, ...]:
    p = squarefree(p)
    chain = [p, derivative(p)]
    for _ in range(len(p)):
        if chain[-1] == (F(0),):
            chain.pop()
            break
        _, rem = pdiv(chain[-2], chain[-1])
        chain.append(pscale(rem, F(-1)))
    require(chain[-1] != (F(0),), 'Sturm budget')
    return tuple(chain)


def variations(chain: tuple[Poly, ...], x: F) -> int:
    signs = [1 if y > 0 else -1 for p in chain if (y := peval(p, x))]
    return sum(signs[i] != signs[i - 1] for i in range(1, len(signs)))


@lru_cache(maxsize=128)
def extreme_roots(p: Poly, r: F) -> tuple[F, F, F, F]:
    chain = sturm(p)
    left, right = F(0), (1 + r) ** 2 + 1
    v0 = variations(chain, left)
    count = v0 - variations(chain, right)
    require(count >= 1, 'positive Gram roots')
    bounds = []
    for target in (1, count):
        lo, hi = left, right
        for _ in range(48):
            mid = (lo + hi) / 2
            if v0 - variations(chain, mid) >= target:
                hi = mid
            else:
                lo = mid
        bounds.extend((lo, hi))
    require(bounds[0] > 0, 'positive minimum root bracket')
    return tuple(bounds)


def characteristic(a: Matrix) -> Poly:
    """Faddeev-LeVerrier on the literal matrix, without cycle information."""
    n = len(a)
    ident = eye(n)
    b = ident
    descending = [F(1)]
    for k in range(1, n + 1):
        ab = multiply(a, b)
        c = -trace(ab) / k
        descending.append(c)
        b = add(ab, scaled(ident, c))
    require(b == scaled(ident, F(0)), 'Cayley-Hamilton residual')
    return tuple(reversed(descending))


def validate(edges: tuple[Matrix, ...], r: F) -> int:
    require(2 <= len(edges) <= MAX_BANKS, 'bank count')
    require(0 < r < 1, 'coupling magnitude')
    d = len(edges[0])
    require(1 <= d <= MAX_INTERNAL, 'internal dimension')
    for u in edges:
        require(len(u) == d and all(len(row) == d for row in u), 'edge shape')
        require(multiply(transpose(u), u) == eye(d), 'unitary edge')
    return d


def literal(edges: tuple[Matrix, ...], r: F) -> tuple[Matrix, Matrix, Matrix]:
    d = validate(edges, r)
    w, n = len(edges), len(edges) * d
    s = [[F(0)] * n for _ in range(n)]
    h = eye(d)
    for j, u in enumerate(edges):
        h = multiply(h, u)
        for a in range(d):
            for b in range(d):
                s[j * d + a][((j + 1) % w) * d + b] = u[a][b]
    s = tuple(tuple(row) for row in s)
    require(multiply(transpose(s), s) == eye(n), 'whole-cycle unitarity')
    a = add(eye(n), scaled(s, r))
    gram = multiply(transpose(a), a)
    return s, gram, h


def predicted(w: int, r: F, h: Matrix) -> Poly:
    """det(2*r^W*T_W((t-a)/(2r))*I-r^W*(H+H^T))."""
    x = (-(1 + r * r) / (2 * r), 1 / (2 * r))
    t0, t1 = (F(1),), x
    for _ in range(2, w + 1):
        t0, t1 = t1, padd(pscale(pmul(x, t1), F(2)), pscale(t0, F(-1)))
    base = pscale(t1, 2 * r ** w)
    c = scaled(add(h, transpose(h)), r ** w)
    if len(h) == 1:
        return padd(base, (-c[0][0],))
    determinant = c[0][0] * c[1][1] - c[0][1] * c[1][0]
    return padd(padd(pmul(base, base), pscale(base, -trace(c))), (determinant,))


def inspect(edges: tuple[Matrix, ...], r: F) -> tuple[Poly, Matrix, Matrix]:
    _, gram, h = literal(edges, r)
    direct = characteristic(gram)
    require(direct == predicted(len(edges), r, h), 'cycle spectrum polynomial')
    return direct, gram, h


def orthogonal_group() -> tuple[Matrix, ...]:
    out = []
    for perm in itertools.permutations(range(2)):
        for signs in itertools.product((-1, 1), repeat=2):
            out.append(tuple(tuple(F(signs[i] if j == perm[i] else 0)
                                   for j in range(2)) for i in range(2)))
    require(len(set(out)) == 8, 'complete signed-permutation alphabet')
    return tuple(out)


def exact_small_optimum(poly: Poly, gram: Matrix, h: Matrix, w: int, r: F) -> bool:
    sigma = F(-1 if w % 2 == 0 else 1)
    attaining = h == scaled(eye(len(h)), sigma)
    a = 1 + r * r
    if attaining:
        if w == 2:
            require(gram == scaled(eye(len(gram)), a), 'even perfect conditioning')
        else:
            high, low = a + 2 * r, a - r
            ident = eye(len(gram))
            residual = multiply(add(gram, scaled(ident, -high)),
                                add(gram, scaled(ident, -low)))
            require(residual == scaled(ident, F(0)), 'odd attaining Gram polynomial')
            require(gram != scaled(ident, high) and gram != scaled(ident, low),
                    'both extremal eigenspaces occur')
        return True
    low_lo, low_hi, high_lo, _ = extreme_roots(poly, r)
    optimum_squared = F(1) if w == 2 else (1 + r) ** 2 / (a - r)
    require(low_lo > 0 and high_lo / low_hi > optimum_squared,
            'strict nonattaining condition-number gap')
    return False


def scalar_census() -> dict[str, int]:
    fixtures = winners = 0
    for w in range(2, 8):
        for r in (F(1, 3), F(1, 2), F(3, 4)):
            for signs in itertools.product((-1, 1), repeat=w):
                edges = tuple(((F(s),),) for s in signs)
                p, gram, h = inspect(edges, r)
                fixtures += 1
                winners += h == ((F((-1) ** (w + 1)),),)
                if w <= 3:
                    exact_small_optimum(p, gram, h, w, r)
    return {'scalar_fixtures': fixtures, 'scalar_attaining_products': winners}


def matrix_census() -> dict[str, int]:
    fixtures = winners = 0
    for w in (2, 3):
        for edges in itertools.product(orthogonal_group(), repeat=w):
            p, gram, h = inspect(edges, F(1, 2))
            winners += exact_small_optimum(p, gram, h, w, F(1, 2))
            fixtures += 1
    return {'matrix_fixtures': fixtures, 'matrix_attainers': winners}


def gauge_fixtures() -> int:
    rot = ((F(3, 5), F(-4, 5)), (F(4, 5), F(3, 5)))
    flip = ((F(1), F(0)), (F(0), F(-1)))
    fixtures = 0
    for w in (*range(2, 8), 13):
        q = tuple(rot if j % 3 == 0 else flip if j % 3 == 1 else eye(2)
                  for j in range(w))
        for h in (scaled(eye(2), F((-1) ** (w + 1))), rot, flip):
            edges = tuple(multiply(q[j], transpose(q[j + 1])) for j in range(w - 1))
            edges += (multiply(multiply(q[-1], h), transpose(q[0])),)
            for r in (F(1, 3), F(1, 2)):
                p, _, product = inspect(edges, r)
                require(product == multiply(multiply(q[0], h), transpose(q[0])),
                        'ordered-product gauge conjugation')
                if w <= 3:
                    _, gram, _ = literal(edges, r)
                    exact_small_optimum(p, gram, product, w, r)
                fixtures += 1
    require(multiply(rot, flip) != multiply(flip, rot), 'noncommuting fixture')
    return fixtures


def rejected(call, message: str) -> None:
    try:
        call()
    except ValueError:
        return
    raise ValueError('control was accepted: ' + message)


def controls() -> int:
    unit = (((F(1),),),) * 3
    for r in (F(0), F(1), F(-1, 2)):
        rejected(lambda: literal(unit, r), 'invalid gain')
    rejected(lambda: literal(unit[:1], F(1, 2)), 'one bank')
    rejected(lambda: literal(((), ()) , F(1, 2)), 'zero dimension')
    rejected(lambda: literal((eye(1), eye(2)), F(1, 2)), 'unequal dimensions')
    rejected(lambda: literal((((F(1), F(0)),),) * 2, F(1, 2)), 'nonsquare')
    rejected(lambda: literal((((F(2),),),) * 2, F(1, 2)), 'nonunitary')
    p, gram, _ = inspect(unit, F(1, 2))
    require(p == (F(-81, 64), F(63, 16), F(-15, 4), F(1)), 'three-bank fixture')
    corrupt = add(gram, scaled(eye(3), F(1, 8)))
    require(characteristic(corrupt) != p, 'Gram mutation detected')
    require(F(81, 49) < 3, 'loop-only number cannot certify changed fixture')
    bad = tuple(((-F(1),),) for _ in range(3))
    bp, bg, bh = inspect(bad, F(1, 2))
    require(not exact_small_optimum(bp, bg, bh, 3, F(1, 2)), 'odd product sign')
    return 11


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    stats = scalar_census() | matrix_census()
    stats['gauge_fixtures'] = gauge_fixtures()
    stats['controls'] = controls()
    require(stats['scalar_fixtures'] == 756, 'scalar enumeration completeness')
    require(stats['matrix_fixtures'] == 576, 'matrix enumeration completeness')
    package = Path(__file__).resolve().parent
    receipt = {'schema': 'unitary-cycle-optimal-conditioning/v1',
               'claim_type': 'scoped algebraic proof with exact finite corroboration',
               'no_new_kappa': True, 'statistics': stats,
               'sha256': {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                          for name in SOURCE_NAMES}}
    data = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.receipt is not None:
        require(not args.receipt.resolve().is_relative_to(package),
                'receipt must be outside the package')
        written = args.receipt.write_text(data)
        require(written == len(data), 'complete receipt write')
    print(data, end='')
    print('PASS_UNITARY_CYCLE_OPTIMAL_CONDITIONING',
          ' '.join(f'{k}={v}' for k, v in stats.items()), 'no_new_kappa')


if __name__ == '__main__':
    main()

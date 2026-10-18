"""Exact canonical P112 geometry and Gaussian-rational fixture arithmetic.

Gareth Davidson / OpenAI Codex. Apache-2.0. Geometry follows credited PR717/845.
"""
from fractions import Fraction as F
from functools import reduce
from itertools import combinations, product
from math import gcd, lcm


def need(value, message):
    if not value:
        raise ValueError(message)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def geometry():
    roots = []
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            r = [0] * 8
            r[i], r[j] = a, b
            roots.append(tuple(r))
    roots += [r for r in product((-1, 1), repeat=8) if sum(x < 0 for x in r) % 2 == 0]
    lines = {max(r, tuple(-x for x in r)) for r in roots}
    frame = []
    for j in range(4):
        for sign in (1, -1):
            f = [0] * 8
            f[2 * j], f[2 * j + 1] = 2, 2 * sign
            frame.append(tuple(f))
    roots = sorted(lines - set(frame))
    x = [[dot(r, f) // 4 for f in frame] for r in roots]
    b = [sum(((1 + dot(a, c) // 4) % 2) << j for j, c in enumerate(roots)) for a in roots]
    need(len(roots) == 112 and len(lines) == 120, "root-line inventory")
    need(all(dot(r, r) == 8 for r in roots), "root norm")
    need(all(set(row) <= {-1, 0, 1} and dot(row, row) == 4 for row in x), "coordinate alphabet")
    need(all(dot(x[i], x[j]) == dot(roots[i], roots[j]) // 2
             for i in range(112) for j in range(112)), "XX^T=2G")
    return roots, frame, x, b


def binary_basis(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return [pivots[p] for p in sorted(pivots)]


def characters(b):
    basis = binary_basis(b)
    need(len(basis) == 9, "binary pairing dimension")
    result = [0]
    for row in basis:
        result += [v ^ row for v in result]
    need(len(set(result)) == 512, "complete character space")
    return sorted(result)


def rational_basis(rows, width=8):
    """Fraction-free rational elimination, recording original pivot-row indices."""
    basis, selected = {}, []
    for index, row in enumerate(rows):
        r = list(row)
        for p, previous in sorted(basis.items()):
            if r[p]:
                a, c = previous[p], r[p]
                r = [a * u - c * v for u, v in zip(r, previous)]
                divisor = reduce(gcd, map(abs, r), 0)
                if divisor:
                    r = [u // divisor for u in r]
        if any(r):
            p = next(i for i, v in enumerate(r) if v)
            if r[p] < 0:
                r = [-u for u in r]
            basis[p] = r
            selected.append(index)
            if len(basis) == width:
                break
    return selected


def support(values):
    return [i for i, v in enumerate(values) if v]


def pairing_rank(b, left, right):
    mask = sum(1 << j for j in right)
    return len(binary_basis(b[i] & mask for i in left))


def g(value=0, imag=0):
    return (F(value), F(imag))


ZERO, ONE = g(), g(1)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def neg(a):
    return (-a[0], -a[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def inv(a):
    d = a[0] ** 2 + a[1] ** 2
    need(d != 0, "division by zero")
    return (a[0] / d, -a[1] / d)


def transpose(a):
    return [list(r) for r in zip(*a)]


def eye(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def matrix_product(a, b):
    return [[reduce(add, (mul(x, y) for x, y in zip(row, col)), ZERO)
             for col in zip(*b)] for row in a]


def inverse(a):
    n = len(a)
    rows = [list(r) + e for r, e in zip(a, eye(n))]
    for p in range(n):
        pivot = next((i for i in range(p, n) if rows[i][p] != ZERO), None)
        need(pivot is not None, "singular factor change")
        rows[p], rows[pivot] = rows[pivot], rows[p]
        factor = inv(rows[p][p])
        rows[p] = [mul(v, factor) for v in rows[p]]
        for i in range(n):
            if i != p and rows[i][p] != ZERO:
                c = rows[i][p]
                rows[i] = [add(v, neg(mul(c, w))) for v, w in zip(rows[i], rows[p])]
    return [row[n:] for row in rows]


def cleared(a):
    denominator = lcm(*(v.denominator for row in a for pair in row for v in pair))
    return [[(int(re * denominator), int(im * denominator)) for re, im in row]
            for row in a], denominator


def expand(c, coefficients):
    """Integer C times denominator-cleared Gaussian coefficient matrix."""
    return [[(sum(a * pair[0] for a, pair in zip(row, col)),
              sum(a * pair[1] for a, pair in zip(row, col)))
             for col in zip(*coefficients)] for row in c]


def ig_product_entry(left, right):
    return (sum(a * c - b * d for (a, b), (c, d) in zip(left, right)),
            sum(a * d + b * c for (a, b), (c, d) in zip(left, right)))


def factor_model(x, v, lam, left):
    """K=C H C^T; derive right factor by ordinary inverse transpose."""
    s = x[v]
    h = eye(9)
    for i in range(8):
        h[i][8] = mul(lam, g(s[i]))
    h[8][8] = mul(g(-4), lam)
    right = matrix_product(transpose(h), transpose(inverse(left)))
    need(matrix_product(left, transpose(right)) == h, "coefficient product")
    c = [row + [int(i == v)] for i, row in enumerate(x)]
    lm, ld = cleared(left)
    rm, rd = cleared(right)
    return expand(c, lm), expand(c, rm), ld * rd, right, h


def fixture_left(x, v, lam, kind):
    s = x[v]
    if kind == "left_zero":
        kappa = mul(lam, inv(add(ONE, lam)))
        result = eye(9)
        for j in range(8):
            result[8][j] = neg(mul(kappa, g(s[j])))
        return result
    if kind == "pure_compensation":
        p = next(i for i, a in enumerate(s) if a)
        right_basis = eye(8)
        for i in range(8):
            right_basis[i][p] = g(s[i])
        a = transpose(inverse(right_basis))
        return [row + [ZERO] for row in a] + [[ZERO] * 8 + [ONE]]
    result = eye(9)
    for j in range(8):
        result[j][8] = g(s[j])
    result[8][8] = g(-4)
    if kind == "right_zero":
        return result
    if kind == "nine_mixed_71":
        p = next(i for i, a in enumerate(s) if a)
        for row in result:
            row[p] = add(row[p], row[8])
        return result
    need(kind == "dense_complex", "unknown fixture type")
    for turn in range(36):
        source = turn % 9
        target = (4 * turn + 1) % 9
        if target == source:
            target = (target + 1) % 9
        coefficient = (g(1), g(0, 1), g(-1), g(1, -1))[turn % 4]
        for row in result:
            row[target] = add(row[target], mul(coefficient, row[source]))
    return result

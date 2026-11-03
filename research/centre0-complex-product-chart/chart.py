"""Exact common split-product coordinates for the pinned centre0 pair.

New construction produced by Nick Petalas. Apache-2.0.
Quadratic numbers are pairs (a,b) representing a+b*sqrt(6097).
"""

from fractions import Fraction as F

D = 6097
N = 112
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
LAM = (F(937), F(12))
RECIP = (F(937), F(-12))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def q(value):
    return (F(value), F(0))


def add(x, y):
    return (x[0] + y[0], x[1] + y[1])


def neg(x):
    return (-x[0], -x[1])


def mul(x, y):
    return (x[0]*y[0] + D*x[1]*y[1], x[0]*y[1] + x[1]*y[0])


def scale(x, a):
    return (x[0]*a, x[1]*a)


def inverse(x):
    norm = x[0]*x[0] - D*x[1]*x[1]
    require(norm != 0, "zero quadratic denominator")
    return (x[0]/norm, -x[1]/norm)


def total(values):
    result = ZERO
    for value in values:
        result = add(result, value)
    return result


def rref(rows, width):
    require(0 <= len(rows) <= 14 and width == N, "unsupported row domain")
    require(all(len(row) == width for row in rows), "ragged constraints")
    a = [[F(x) for x in row] for row in rows]
    pivots = []
    for column in range(width):
        candidates = [i for i in range(len(pivots), len(a)) if a[i][column]]
        if not candidates:
            continue
        k = len(pivots)
        a[k], a[candidates[0]] = a[candidates[0]], a[k]
        divisor = a[k][column]
        a[k] = [x/divisor for x in a[k]]
        for i in range(len(a)):
            if i != k and a[i][column]:
                coefficient = a[i][column]
                a[i] = [x-coefficient*y for x, y in zip(a[i], a[k])]
        pivots.append(column)
        if len(pivots) == len(a):
            break
    return a[:len(pivots)], pivots


def source_vectors(r, selected):
    require(len(r) == 8 and all(len(row) == N for row in r), "bad R size")
    require(len(selected) == 8 and len(set(selected)) == 8, "bad selected set")
    require(all(type(i) is int and 0 <= i < N for i in selected), "bad port")
    require(all(x.denominator == 1 and abs(x) <= 2 for row in r for x in row),
            "R outside source alphabet")
    u = [[x * (F(-11, 4) if i in selected else F(1, 4))
          for i, x in enumerate(row)] for row in r]
    return r[1:], u[1:]


def complement(r, u):
    reduced, pivots = rref(r + u, N)
    require(len(pivots) == 14, "active space is not fourteen dimensional")
    free = [j for j in range(N) if j not in pivots]
    columns = []
    for j in free:
        z = [F(i == j) for i in range(N)]
        for k, pivot in enumerate(pivots):
            z[pivot] = -reduced[k][j]
        columns.append(z)
    return free, columns


def common_coordinates(r, selected):
    """Return W and Q=W^-1, both as row matrices over Q(sqrt(6097))."""
    r, u = source_vectors(r, selected)
    free, z = complement(r, u)
    t = scale(neg(add(ONE, RECIP)), F(1, 56))
    inv_t = inverse(t)
    inv_gap = inverse(add(ONE, neg(RECIP)))
    columns, rows = [], []
    alpha, beta = [], []
    for rr, uu in zip(r, u):
        aa = [(56*x-2*y)/1872 for x, y in zip(uu, rr)]
        bb = [(-2*x+F(67, 2)*y)/1872 for x, y in zip(uu, rr)]
        alpha.append(aa)
        beta.append(bb)
        columns.append([add(q(x), scale(t, y)) for x, y in zip(uu, rr)])
        columns.append([add(scale(RECIP, x), scale(t, y))
                        for x, y in zip(uu, rr)])
        rows.append([mul(inv_gap, add(q(x), neg(scale(mul(RECIP, inv_t), y))))
                     for x, y in zip(aa, bb)])
        rows.append([mul(inv_gap, add(q(-x), scale(inv_t, y)))
                     for x, y in zip(aa, bb)])
    columns.extend([[q(x) for x in column] for column in z])
    for j in free:
        row = [F(i == j) for i in range(N)]
        for k in range(7):
            row = [x-u[k][j]*a-r[k][j]*b
                   for x, a, b in zip(row, alpha[k], beta[k])]
        rows.append([q(x) for x in row])
    w = [list(row) for row in zip(*columns)]
    require(len(w) == N and len(rows) == N, "wrong chart dimension")
    return w, rows


def split_maps(width):
    require(type(width) is int and N <= width <= 512, "unsupported fixture width")
    permutation = list(range(width))
    weights = [ONE] * width
    for k in range(7):
        i = 2*k
        permutation[i], permutation[i+1] = i+1, i
        weights[i], weights[i+1] = RECIP, LAM
    return permutation, weights


def apply(matrix, vector):
    require(len(matrix) <= 512 and len(vector) <= 512, "oversized matrix")
    require(all(len(row) == len(vector) for row in matrix), "matrix shape")
    return [total(mul(x, y) for x, y in zip(row, vector) if x != ZERO and y != ZERO)
            for row in matrix]

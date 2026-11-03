"""Bounded exact prime-field linear algebra, with no field-element search."""

from math import isqrt


def prime(p):
    if type(p) is not int or not 2 <= p <= 65537:
        raise ValueError("prime must be in 2..65537")
    if any(p % i == 0 for i in range(2, isqrt(p) + 1)):
        raise ValueError("composite characteristic")


def vector(v, n, p):
    if len(v) != n or any(type(x) is not int or not 0 <= x < p for x in v):
        raise ValueError("noncanonical vector")


def rref(rows, p, width):
    a = [list(row) for row in rows]
    pivots = []
    for j in range(width):
        pivot = next((i for i in range(len(pivots), len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        k = len(pivots)
        a[k], a[pivot] = a[pivot], a[k]
        scale = pow(a[k][j], -1, p)
        a[k] = [(x * scale) % p for x in a[k]]
        for i in range(len(a)):
            if i != k and a[i][j]:
                scale = a[i][j]
                a[i] = [(x - scale * y) % p for x, y in zip(a[i], a[k])]
        pivots.append(j)
    return a, pivots


def span(rows, p, width):
    a, pivots = rref(rows, p, width)
    return a[:len(pivots)]


def nullspace(rows, p, width):
    a, pivots = rref(rows, p, width)
    result = []
    for j in range(width):
        if j in pivots:
            continue
        v = [int(i == j) for i in range(width)]
        for k, pivot in enumerate(pivots):
            v[pivot] = -a[k][j] % p
        result.append(v)
    return result


def solve(rows, rhs, p, width):
    a, pivots = rref([list(row) + [b] for row, b in zip(rows, rhs)], p, width)
    if any(not any(row[:width]) and row[width] for row in a):
        return None
    v = [0] * width
    for i, j in enumerate(pivots):
        v[j] = a[i][width]
    return v


def transpose(a):
    return [list(row) for row in zip(*a)]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mv(a, v, p):
    return [sum(x * y for x, y in zip(row, v)) % p for row in a]


def mm(a, b, p):
    return transpose([mv(a, col, p) for col in transpose(b)])


def combine(coefficients, vectors, dimension, p):
    return [sum(c * v[j] for c, v in zip(coefficients, vectors)) % p
            for j in range(dimension)]


def flatten(a):
    return [x for row in a for x in row]


def matrix_combination(c, matrices, p):
    n = len(matrices[0])
    flat = combine(c, [flatten(m) for m in matrices], n * n, p)
    return [flat[i * n:(i + 1) * n] for i in range(n)]

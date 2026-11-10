"""Exact rational matrices and coefficients in Q(i).

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def matrix(rows):
    return [[Q(x) for x in row] for row in rows]


def eye(n):
    return matrix([[int(i == j) for j in range(n)] for i in range(n)])


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, column)) for column in zip(*b)] for row in a]


def add(a, b, scale=1):
    return [[x+scale*y for x, y in zip(row, other)] for row, other in zip(a, b)]


def inverse(a):
    n = len(a)
    rows = [row[:] + identity for row, identity in zip(a, eye(n))]
    for j in range(n):
        k = next((k for k in range(j, n) if rows[k][j]), None)
        need(k is not None, 'Nonsingular rational matrix')
        rows[j], rows[k] = rows[k], rows[j]
        v = rows[j][j]
        rows[j] = [x/v for x in rows[j]]
        for k in range(n):
            if k != j:
                v = rows[k][j]
                rows[k] = [x-v*y for x, y in zip(rows[k], rows[j])]
    return [row[n:] for row in rows]


def coefficient(x):
    return (Q(x), Q(0))


def zadd(a, b):
    return a[0]+b[0], a[1]+b[1]


def zmul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def accumulate(dst, src, c=(Q(1), Q(0))):
    for key, value in src.items():
        value = zadd(dst.get(key, (Q(0), Q(0))), zmul(c, value))
        if value != (0, 0):
            dst[key] = value
        else:
            dst.pop(key, None)


def shifted(row, term):
    result = []
    for cell in row:
        target = {}
        for key, value in cell.items():
            new = ((key[0]+term[0]) % 4,) + tuple(a+b for a, b in zip(key[1:], term[1:]))
            accumulate(target, {new: value})
        result.append(target)
    return result

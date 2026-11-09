"""Host arithmetic for fixture construction and expected values only."""
from math import gcd

from words import need


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, modulus):
    out = [[0]*len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] = (out[i][j]+x*y) % modulus
    return out


def inverse(a, modulus):
    n = len(a)
    rows = [list(row)+unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        k = next((i for i in range(j, n) if gcd(rows[i][j], modulus) == 1), None)
        need(k is not None, "oracle unit pivot")
        rows[j], rows[k] = rows[k], rows[j]
        inv = pow(rows[j][j], -1, modulus)
        rows[j] = [x*inv % modulus for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                c = rows[i][j]
                rows[i] = [(x-c*y) % modulus for x, y in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def reduce_rational(a, modulus):
    return [[x.numerator*pow(x.denominator, -1, modulus) % modulus for x in row] for row in a]


def fixture(template, width, high=1, bad=False, unit_low=False, row=None):
    q, modulus = template.q, template.q**width
    row = template.rank if row is None else row
    h = eye(64)
    if bad:
        h[0][0], h[0][row], h[row][0], h[row][row] = q, q-1, 1, 1+q*high
    elif unit_low:
        h[0][0], h[0][row], h[row][0], h[row][row] = 1+q*high, 1, 1, 2
    else:
        h[0][row], h[row][0], h[row][row] = 1, q*high, 1+q*high
    raw = multiply(h, inverse(reduce_rational(template.preparation, modulus), modulus), modulus)
    low = tuple(tuple(x % q for x in row) for row in raw)
    digits = tuple(tuple(x//q for x in row) for row in raw)
    return low, digits


def projector(template, low, high, width):
    q, modulus = template.q, template.q**width
    raw = [[a+q*b for a, b in zip(lo, hi)] for lo, hi in zip(low, high)]
    common = multiply(raw, reduce_rational(template.chart, modulus), modulus)
    return multiply(multiply(common, reduce_rational(template.base, modulus), modulus),
                    inverse(common, modulus), modulus)


def good_pivots(p, rank, modulus):
    rows, pivots = [list(row) for row in p], []
    for k in range(rank):
        inv = pow(rows[k][k], -1, modulus)
        pivots.append(rows[k][k])
        for i in range(k+1, len(rows)):
            coefficient = rows[i][k]*inv % modulus
            rows[i] = [(x-coefficient*y) % modulus for x, y in zip(rows[i], rows[k])]
    return pivots


def fallback(p, modulus):
    n = len(p)
    rows = [[0]*(2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            rows[i][j] = rows[2*n-1-i][2*n-1-j] = (int(i == j)-p[i][j]) % modulus
            rows[i][2*n-1-j] = rows[2*n-1-i][j] = p[i][j]
    permutation = list(range(2*n))
    for j in range(2*n):
        pivot = next(i for i in range(j, 2*n) if gcd(rows[i][j], modulus) == 1)
        rows[j], rows[pivot] = rows[pivot], rows[j]
        permutation[j], permutation[pivot] = permutation[pivot], permutation[j]
        inv = pow(rows[j][j], -1, modulus)
        for i in range(2*n):
            if i != j and rows[i][j]:
                coefficient = rows[i][j]*inv % modulus
                rows[i] = [(x-coefficient*y) % modulus for x, y in zip(rows[i], rows[j])]
    return [rows[i][i] for i in range(2*n)], tuple(permutation)

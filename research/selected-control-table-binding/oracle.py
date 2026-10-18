"""Independent dense local-ring oracle for the table's mathematical meaning.

This module imports no predecessor algebra. It uses normalized row reduction,
where the producer uses unnormalized elimination; good pivots are extracted
from the unreversed weighted projector instead of its northeast cross block.
"""
from math import gcd


def need(test, message):
    if not test:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def product(a, b, modulus):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) % modulus
             for col in columns] for row in a]


def inverse(a, modulus):
    n = len(a)
    rows = [list(row) + e for row, e in zip(a, identity(n))]
    for j in range(n):
        k = next((i for i in range(j, n) if gcd(rows[i][j], modulus) == 1), None)
        need(k is not None, "oracle invertible matrix")
        rows[j], rows[k] = rows[k], rows[j]
        rows[j] = [(x * pow(rows[j][j], -1, modulus)) % modulus for x in rows[j]]
        for i in range(n):
            if i != j:
                coefficient = rows[i][j]
                rows[i] = [(x - coefficient * y) % modulus for x, y in zip(rows[i], rows[j])]
    need([r[:n] for r in rows] == identity(n), "oracle inverse endpoint")
    return [r[n:] for r in rows]


def actual_projector(header):
    """Raw GL matrix and actual label, bypassing the producer's split basis."""
    modulus, q = header.q ** header.width, header.q
    g = [[x + q * y for x, y in zip(a, b)] for a, b in zip(header.low, header.high)]
    sigma = [[x.numerator * pow(x.denominator, -1, modulus) % modulus for x in row]
             for row in header.catalogue.chart_matrix(header.request.chart)]
    base = header.request.base
    p = [[0] * 64 for _ in range(64)]
    if base.kind == "idle":
        for axis in base.data:
            p[axis][axis] = 1
    else:
        need(base.kind == "local", "oracle selected label kind")
        for i, row in enumerate(base.data):
            for j, x in enumerate(row):
                p[i][j] = x.numerator * pow(x.denominator, -1, modulus) % modulus
    common = product(g, sigma, modulus)
    return product(product(common, p, modulus), inverse(common, modulus), modulus)


def weighted_good_pivots(projector, weights, rank, modulus):
    """Leading LU pivots of diag(weights) P; no column-reversal code."""
    rows = [[weight * x % modulus for x in row] for weight, row in zip(weights, projector)]
    pivots = []
    for k in range(rank):
        pivot = rows[k][k]
        need(gcd(pivot, modulus) == 1, "oracle generic leading minor")
        pivots.append(pivot)
        rows[k] = [x * pow(pivot, -1, modulus) % modulus for x in rows[k]]
        for i in range(k + 1, len(rows)):
            c = rows[i][k]
            rows[i] = [(x - c * y) % modulus for x, y in zip(rows[i], rows[k])]
    need(all(not any(row) for row in rows[rank:]), "oracle rank endpoint")
    return tuple(pivots)


def weighted_residual(projector, weights, modulus):
    n = len(projector)
    bank = list(weights) + [1] * n
    rows = []
    for i in range(2 * n):
        row = []
        for j in range(2 * n):
            if i < n and j < n:
                x = int(i == j) - projector[i][j]
            elif i < n:
                x = projector[i][2 * n - 1 - j]
            elif j < n:
                x = projector[2 * n - 1 - i][j]
            else:
                x = int(i == j) - projector[2 * n - 1 - i][2 * n - 1 - j]
            row.append(bank[i] * x * pow(bank[j], -1, modulus) % modulus)
        rows.append(row)
    return rows


def normalized_elimination(matrix, modulus):
    """Return pre-normalization pivots and original-row permutation."""
    rows = [list(row) for row in matrix]
    n = len(rows)
    permutation, pivots = list(range(n)), []
    for column in range(n):
        row = next((i for i in range(column, n) if gcd(rows[i][column], modulus) == 1), None)
        need(row is not None, "oracle residual unit pivot")
        rows[column], rows[row] = rows[row], rows[column]
        permutation[column], permutation[row] = permutation[row], permutation[column]
        pivot = rows[column][column]
        pivots.append(pivot)
        inv = pow(pivot, -1, modulus)
        rows[column] = [x * inv % modulus for x in rows[column]]
        for i in range(n):
            if i == column:
                continue
            c = rows[i][column]
            if c:
                rows[i] = [(x - c * y) % modulus for x, y in zip(rows[i], rows[column])]
    need(rows == identity(n), "oracle normalized elimination endpoint")
    return tuple(pivots), tuple(permutation)

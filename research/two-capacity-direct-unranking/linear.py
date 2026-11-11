"""Small exact field and subspace operations. Produced by Nick Petalas."""
from math import isqrt


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """Prime fields through 31, plus F4 = F2[t]/(t^2+t+1)."""

    def __init__(self, q):
        need(type(q) is int and 2 <= q <= 31, "field order limit")
        need(q == 4 or all(q % d for d in range(2, isqrt(q) + 1)), "field order")
        self.q = q

    def add(self, x, y):
        return x ^ y if self.q == 4 else (x + y) % self.q

    def neg(self, x):
        return x if self.q == 4 else -x % self.q

    def mul(self, x, y):
        if self.q != 4:
            return x * y % self.q
        z = (x & 1) * (y & 1)
        z ^= ((x >> 1) * (y & 1) ^ (x & 1) * (y >> 1)) << 1
        z ^= ((x >> 1) * (y >> 1)) * 3
        return z

    def inv(self, x):
        need(0 < x < self.q, "nonzero inverse")
        return self.mul(x, x) if self.q == 4 else pow(x, -1, self.q)


def unit(n, j):
    return tuple(int(i == j) for i in range(n))


def standard(n):
    return tuple(unit(n, j) for j in range(n))


def combine(coefficients, rows, n, field):
    need(len(coefficients) == len(rows), "combination dimensions")
    out = [0] * n
    for a, row in zip(coefficients, rows):
        for j in range(n):
            out[j] = field.add(out[j], field.mul(a, row[j]))
    return tuple(out)


def add_vectors(x, y, field):
    need(len(x) == len(y), "vector dimensions")
    return tuple(field.add(a, b) for a, b in zip(x, y))


def reduce_rows(rows, n, field):
    work = [list(row) for row in rows]
    pivots = []
    for col in range(n):
        at = next((i for i in range(len(pivots), len(work)) if work[i][col]), None)
        if at is None:
            continue
        pos = len(pivots)
        work[pos], work[at] = work[at], work[pos]
        scale = field.inv(work[pos][col])
        work[pos] = [field.mul(x, scale) for x in work[pos]]
        for i in range(len(work)):
            if i != pos and work[i][col]:
                scale = field.neg(work[i][col])
                work[i] = [field.add(x, field.mul(scale, y))
                           for x, y in zip(work[i], work[pos])]
        pivots.append(col)
    return tuple(tuple(row) for row in work[:len(pivots)]), tuple(pivots)


def basis(rows, n, field):
    return reduce_rows(rows, n, field)[0]


def annihilator(rows, n, field):
    reduced, pivots = reduce_rows(rows, n, field)
    out = []
    for j in range(n):
        if j not in pivots:
            v = list(unit(n, j))
            for row, col in zip(reduced, pivots):
                v[col] = field.neg(row[j])
            out.append(tuple(v))
    return tuple(out)


def meet(left, right, n, field):
    return annihilator(annihilator(left, n, field) +
                       annihilator(right, n, field), n, field)


def complement(initial, container, n, field):
    current = list(initial)
    need(len(basis(current, n, field)) == len(current), "independent initial basis")
    added = []
    for v in container:
        if len(basis(tuple(current) + (v,), n, field)) > len(current):
            current.append(v)
            added.append(v)
    return tuple(added)


def coordinates(rows, vector, n, field):
    """Unique coordinates in an independent ordered row basis."""
    k = len(rows)
    equations = [tuple(row[j] for row in rows) + (vector[j],) for j in range(n)]
    reduced, pivots = reduce_rows(equations, k + 1, field)
    need(pivots == tuple(range(k)), "vector outside independent span")
    return tuple(row[-1] for row in reduced)

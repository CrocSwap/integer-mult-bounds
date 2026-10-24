"""Literal column-update construction over F_p[t]/t^d. Apache-2.0.

Prepared for Cinna Davis with substantial OpenAI Codex assistance.
Ring elements are coefficient vectors encoded as base-p integers.
"""
from itertools import product


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Ring:
    def __init__(self, p, d):
        need(type(p) is int and p >= 2 and all(p % i for i in range(2, p)),
             "prime characteristic required")
        need(type(d) is int and d >= 1, "positive nilpotency required")
        self.p, self.d, self.size = p, d, p ** d
        self.coeffs = [tuple((a // p ** i) % p for i in range(d))
                       for a in range(self.size)]
        self.adds = [[self.encode((x + y) % p for x, y in zip(a, b))
                      for b in self.coeffs] for a in self.coeffs]
        self.muls = [[self.encode(sum(a[i] * b[k-i] for i in range(k+1)) % p
                                 for k in range(d))
                      for b in self.coeffs] for a in self.coeffs]
        self.negs = [self.encode(-x % p for x in a) for a in self.coeffs]

    def encode(self, coefficients):
        return sum(x * self.p ** i for i, x in enumerate(coefficients))

    def add(self, a, b):
        return self.adds[a][b]

    def sub(self, a, b):
        return self.adds[a][self.negs[b]]

    def mul(self, a, b):
        return self.muls[a][b]

    def valuation(self, a):
        return next((i for i, x in enumerate(self.coeffs[a]) if x), self.d)

    def unit_inverse(self, a):
        need(a % self.p != 0, "nonunit inverse")
        aa, result = self.coeffs[a], []
        c = pow(aa[0], -1, self.p)
        for k in range(self.d):
            result.append(c if k == 0 else
                          -c * sum(aa[i] * result[k-i] for i in range(1, k+1)) % self.p)
        return self.encode(result)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(ring, a, b):
    need(len(a[0]) == len(b), "matrix dimensions")
    result = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    result[i][j] = ring.add(result[i][j], ring.mul(x, y))
    return result


def subtract(ring, a, b):
    return [[ring.sub(x, y) for x, y in zip(aa, bb)] for aa, bb in zip(a, b)]


def inverse(ring, matrix):
    n = len(matrix)
    a, result = [row[:] for row in matrix], identity(n)
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j] % ring.p), None)
        need(pivot is not None, "matrix has nonunit determinant")
        a[j], a[pivot] = a[pivot], a[j]
        result[j], result[pivot] = result[pivot], result[j]
        c = ring.unit_inverse(a[j][j])
        a[j] = [ring.mul(c, x) for x in a[j]]
        result[j] = [ring.mul(c, x) for x in result[j]]
        for i in range(n):
            if i != j:
                c = a[i][j]
                a[i] = [ring.sub(x, ring.mul(c, y)) for x, y in zip(a[i], a[j])]
                result[i] = [ring.sub(x, ring.mul(c, y))
                             for x, y in zip(result[i], result[j])]
    return result


def complete_top_row(ring, matrix):
    """Return a,T with matrix=a*T and T right-unimodular, using Smith pivots."""
    m, width = len(matrix), len(matrix[0])
    need(width == 2*m, "top block row shape")
    work, left, right = [r[:] for r in matrix], identity(m), identity(width)
    diagonal = [0] * m
    for k in range(m):
        v, i, j = min((ring.valuation(work[i][j]), i, j)
                      for i in range(k, m) for j in range(k, width))
        if v == ring.d:
            break
        work[k], work[i] = work[i], work[k]
        left[k], left[i] = left[i], left[k]
        for rows in (work, right):
            for row in rows:
                row[k], row[j] = row[j], row[k]
        unit = work[k][k] // ring.p ** v
        c = ring.unit_inverse(unit)
        work[k] = [ring.mul(c, x) for x in work[k]]
        left[k] = [ring.mul(c, x) for x in left[k]]
        diagonal[k] = ring.p ** v
        for i in range(k+1, m):
            c = work[i][k] // ring.p ** v
            for rows in (work, left):
                rows[i] = [ring.sub(x, ring.mul(c, y))
                           for x, y in zip(rows[i], rows[k])]
        for j in range(k+1, width):
            c = work[k][j] // ring.p ** v
            for rows in (work, right):
                for row in rows:
                    row[j] = ring.sub(row[j], ring.mul(c, row[k]))
    left_inv, right_inv = inverse(ring, left), inverse(ring, right)
    a = [[ring.mul(left_inv[i][j], diagonal[j]) for j in range(m)] for i in range(m)]
    return a, right_inv[:m]


def block_matrix(a, b, c, d):
    return [x+y for x, y in zip(a, b)] + [x+y for x, y in zip(c, d)]


def three_factors(ring, target):
    """Return L,B,R with target=L*B*R and common block columns e1,e2,e1."""
    m = len(target) // 2
    need(m >= 1 and len(target) == 2*m and all(len(row) == 2*m for row in target),
         "two-role target shape")
    need(all(type(x) is int and 0 <= x < ring.size for row in target for x in row),
         "canonical ring entries")
    a, top = complete_top_row(ring, target[:m])
    x, y = [row[:m] for row in top], [row[m:] for row in top]
    c, d = [row[:m] for row in target[m:]], [row[m:] for row in target[m:]]
    # Finite-field search implements stable range one only for the bounded replay.
    # The written proof uses basis extension and applies to every field and size.
    for entries in product(range(ring.p), repeat=m*m):
        f = [list(entries[i*m:(i+1)*m]) for i in range(m)]
        e = subtract(ring, x, multiply(ring, y, f))
        try:
            ei = inverse(ring, e)
        except ValueError:
            continue
        break
    else:
        raise ValueError("unimodular-row completion failed")
    b = multiply(ring, subtract(ring, c, multiply(ring, d, f)), ei)
    dd = subtract(ring, d, multiply(ring, b, y))
    zero, one = [[0]*m for _ in range(m)], identity(m)
    return (block_matrix(a, zero, b, one), block_matrix(one, y, zero, dd),
            block_matrix(e, zero, f, one))


def scalar_two_factors(ring, target):
    """Return L,R,H with target=L*R*H; H is a scalar column permutation."""
    a, b = target[0]
    c, d = target[1]
    h = identity(2)
    if ring.valuation(b) < ring.valuation(a):
        a, b, c, d = b, a, d, c
        h = [[0, 1], [1, 0]]
    if a:
        v = ring.valuation(a)
        q = ring.mul(b // ring.p ** v, ring.unit_inverse(a // ring.p ** v))
    else:
        q = 0
    return [[a, 0], [c, 1]], [[1, q], [0, ring.sub(d, ring.mul(c, q))]], h

"""Explicit good/fallback child weights over Z/q^w.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0. Diagonal covariance and fallback algebra are inherited from
source527 and Ross Richardson's PR2159; the descriptor continuation takes
Jose Manuel's PR2171 handoff. No predecessor executable is imported.
"""

from dataclasses import dataclass
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, modulus):
    result = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        result[i][j] = (result[i][j] + x * y) % modulus
    return result


def inverse(a, modulus):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, identity(n))]
    for k in range(n):
        p = next((i for i in range(k, n) if gcd(rows[i][k], modulus) == 1), None)
        require(p is not None, "matrix has no unit pivot")
        rows[k], rows[p] = rows[p], rows[k]
        d = pow(rows[k][k], -1, modulus)
        rows[k] = [x * d % modulus for x in rows[k]]
        for i in range(n):
            if i != k and rows[i][k]:
                c = rows[i][k]
                rows[i] = [(x - c * y) % modulus for x, y in zip(rows[i], rows[k])]
    require([row[:n] for row in rows] == identity(n), "inverse endpoint")
    return [row[n:] for row in rows]


def projector(chart, axes, modulus):
    gi = inverse(chart, modulus)
    return multiply([[row[k] for k in axes] for row in chart],
                    [gi[k] for k in axes], modulus)


def residual(p, modulus):
    """Unweighted [[I-P,PC],[CP,I-CPC]], in physical coordinate order."""
    n = len(p)
    out = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            out[i][j] = (int(i == j) - p[i][j]) % modulus
            out[i][n+j] = p[i][n-1-j]
            out[n+i][j] = p[n-1-i][j]
            out[n+i][n+j] = (int(i == j) - p[n-1-i][n-1-j]) % modulus
    return out


def good_pivots(p, rank, modulus):
    """Unweighted northeast elimination of P C, with full-ring coefficients."""
    n = len(p)
    a = [row[::-1] for row in p]
    pivots = []
    for k in range(rank):
        c = n - 1 - k
        pivot = a[k][c]
        require(gcd(pivot, modulus) == 1, "nongeneric good ancestor")
        pivots.append(pivot)
        inv = pow(pivot, -1, modulus)
        for i in range(k+1, n):
            scale = a[i][c] * inv % modulus
            if scale:
                a[i] = [(x - scale*y) % modulus for x, y in zip(a[i], a[k])]
        for j in range(c):
            scale = a[k][j] * inv % modulus
            if scale:
                for i in range(n):
                    a[i][j] = (a[i][j] - scale*a[i][c]) % modulus
    expected = [[0] * n for _ in range(n)]
    for k, d in enumerate(pivots):
        expected[k][n-1-k] = d
    require(a == expected, "complete good cross-block endpoint")
    return tuple(pivots)


@dataclass(frozen=True)
class Plan:
    modulus: int
    diagonal: tuple
    permutation: tuple
    pivots: tuple
    operations: tuple


def elimination(matrix, modulus):
    """All-row unnormalized elimination; pi[i] is the ORIGINAL row at i."""
    n = len(matrix)
    require(n > 0 and all(len(row) == n for row in matrix), "square matrix")
    a = [[x % modulus for x in row] for row in matrix]
    pi, pivots, operations = list(range(n)), [], []
    for k in range(n):
        p = next((i for i in range(k, n) if gcd(a[i][k], modulus) == 1), None)
        require(p is not None, "fallback unit pivot")
        pivots.append(p)
        if p != k:
            a[k], a[p] = a[p], a[k]
            pi[k], pi[p] = pi[p], pi[k]
            operations.append(("swap", k, p, 0))
        inv = pow(a[k][k], -1, modulus)
        for i in range(n):
            if i == k:
                continue
            c = -a[i][k] * inv % modulus
            operations.append(("add", i, k, c))  # Keep zero slots.
            if c:
                a[i] = [(x + c*y) % modulus for x, y in zip(a[i], a[k])]
    require(all(a[i][j] == 0 for i in range(n) for j in range(n) if i != j),
            "fallback diagonal endpoint")
    return Plan(modulus, tuple(a[i][i] for i in range(n)), tuple(pi),
                tuple(pivots), tuple(operations))


@dataclass(frozen=True)
class Root:
    size: int
    modulus: int
    unit: int = 1

    def value(self, index):
        require(0 <= index < self.size, "root index extent")
        require(gcd(self.unit, self.modulus) == 1, "root weight unit")
        return self.unit % self.modulus


@dataclass(frozen=True)
class Good:
    parent: object
    dimension: int
    columns: int
    pivots: tuple

    def __post_init__(self):
        require(self.dimension > len(self.pivots) > 0, "good rank")
        require(self.columns == self.parent.size // self.dimension and self.columns > 0,
                "good coarse child width")
        require(all(gcd(x, self.modulus) == 1 for x in self.pivots), "good pivot units")

    @property
    def modulus(self):
        return self.parent.modulus

    @property
    def size(self):
        return len(self.pivots) * self.columns

    def value(self, index):
        require(0 <= index < self.size, "good child index extent")
        k, _ = divmod(index, self.columns)
        return self.parent.value(index) * self.pivots[k] % self.modulus


@dataclass(frozen=True)
class FallbackPair:
    """Weights for F_a within a weighted diagonal-pair J_a J_1.

    The first physical field is `field`; its atom orientation can be reversed.
    The head-bank conjugator has parent weights, the tail-bank conjugator 1.
    `plan` is prepared once from the FULL UNWEIGHTED parent residual.
    """
    parent: object
    dimension: int
    columns: int
    plan: Plan
    field: int
    reverse: bool

    def __post_init__(self):
        n = 2 * self.dimension
        require(self.columns == self.parent.size // self.dimension and self.columns > 0,
                "fallback coarse child width")
        require(self.plan.modulus == self.modulus, "fallback plan modulus")
        require(len(self.plan.diagonal) == n and len(self.plan.permutation) == n,
                "fallback plan dimension")
        require(sorted(self.plan.permutation) == list(range(n)), "fallback row permutation")
        require(0 <= self.field < n-1, "paired diagonal field")
        require(all(gcd(d, self.modulus) == 1 for d in self.plan.diagonal), "fallback diagonal units")

    @property
    def modulus(self):
        return self.parent.modulus

    @property
    def size(self):
        return self.columns

    def bank_weight(self, row, column):
        if row < self.dimension:
            return self.parent.value(row * self.columns + column)
        return 1

    def value(self, index):
        require(0 <= index < self.size, "fallback child index extent")
        j = self.columns - 1 - index if self.reverse else index
        numerator = self.bank_weight(self.plan.permutation[self.field], j)
        denominator = self.bank_weight(self.field, j)
        return (self.plan.diagonal[self.field] * numerator *
                pow(denominator, -1, self.modulus)) % self.modulus


def weighted_residual(matrix, weights, modulus):
    n = len(matrix) // 2
    require(len(matrix) == 2*n and len(weights) == n, "weighted residual dimensions")
    b = list(weights) + [1] * n
    require(all(gcd(x, modulus) == 1 for x in b), "diagonal conjugator units")
    return [[b[i] * x * pow(b[j], -1, modulus) % modulus
             for j, x in enumerate(row)] for i, row in enumerate(matrix)]


def reversed_child(head, tail, weights, modulus):
    require(len(head) == len(tail) == len(weights), "child extent")
    require(all(gcd(a, modulus) == 1 for a in weights), "child weight units")
    f = len(weights)
    return ([weights[t] * tail[f-1-t] % modulus for t in range(f)],
            [pow(weights[f-1-t], -1, modulus) * head[f-1-t] % modulus for t in range(f)])

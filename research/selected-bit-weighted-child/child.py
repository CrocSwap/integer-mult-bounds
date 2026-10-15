"""One generic weighted-child lowering over an odd prime-power ring.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
The normal-form formula is credited to the retained source527 proof.
Apache-2.0. No predecessor executable is imported.
"""
from dataclasses import dataclass
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def multiply(a, b, modulus):
    require(a and b and len(a[0]) == len(b), "matrix dimensions")
    out = []
    for row in a:
        total = [0] * len(b[0])
        for x, brow in zip(row, b):
            if x:
                for j, y in enumerate(brow):
                    total[j] += x * y
        out.append([x % modulus for x in total])
    return out


def matvec(a, x, modulus):
    return [sum(c * v for c, v in zip(row, x)) % modulus for row in a]


def add(a, b, modulus, scale=1):
    return [[(x + scale * y) % modulus for x, y in zip(arow, brow)]
            for arow, brow in zip(a, b)]


def inverse(a, q, modulus):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if gcd(rows[i][j], q) == 1), None)
        require(pivot is not None, "no unit pivot in inverse")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        unit = pow(rows[j][j], -1, modulus)
        rows[j] = [(x * unit) % modulus for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                coefficient = rows[i][j]
                rows[i] = [(x - coefficient * y) % modulus
                           for x, y in zip(rows[i], rows[j])]
    require([row[:n] for row in rows] == eye(n), "inverse endpoint")
    return [row[n:] for row in rows]


def residual(projector, weights, modulus):
    """Independent displayed D_P formula, with the full tail reversal."""
    n = len(projector)
    invweights = [pow(a, -1, modulus) for a in weights]
    result = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            p = projector[i][j]
            result[i][j] = weights[i] * (int(i == j) - p) * invweights[j] % modulus
            result[i][n + n - 1 - j] = weights[i] * p % modulus
            result[n + n - 1 - i][j] = p * invweights[j] % modulus
            result[n + n - 1 - i][n + n - 1 - j] = (int(i == j) - p) % modulus
    return result


def block_diagonal(a, b):
    n, m = len(a), len(b)
    return [row + [0] * m for row in a] + [[0] * n + row for row in b]


def shear(k, modulus, sign=1):
    n = len(k)
    return [row + [0] * n for row in eye(n)] + [
        [sign * x % modulus for x in row] + unit for row, unit in zip(k, eye(n))]


def weighted_swap(n, pivots, weights, modulus):
    out = eye(2 * n)
    for k, pivot in enumerate(pivots):
        a = weights[k] * pivot % modulus
        out[k][k] = out[2 * n - 1 - k][2 * n - 1 - k] = 0
        out[k][2 * n - 1 - k] = a
        out[2 * n - 1 - k][k] = pow(a, -1, modulus)
    return out


@dataclass(frozen=True)
class NormalForm:
    q: int
    modulus: int
    rank: int
    left: list
    right: list
    left_inverse: list
    right_inverse: list
    cross_shear: list
    pivots: tuple
    row_additions: tuple
    column_additions: tuple


def compile_projector(projector, rank, q, width):
    """Generic northeast elimination; never invert a nonunit or normalize a pivot.

    Both recorded normalizers are unit lower triangular. All denominators used
    here are ring units. A nongeneric residue is rejected, not treated as zero.
    """
    n = len(projector)
    require(1 <= rank <= n <= 64 and q >= 3 and q % 2 and 1 <= width <= 8,
            "bounded compiler domain")
    require(all(len(row) == n for row in projector), "square projector")
    modulus = q ** width
    projector = [[x % modulus for x in row] for row in projector]
    require(multiply(projector, projector, modulus) == projector, "split projector")
    a = [list(reversed(row)) for row in projector]
    left, right = eye(n), eye(n)
    row_ops, col_ops, pivots = [], [], []
    for k in range(rank):
        column = n - 1 - k
        pivot = a[k][column]
        require(gcd(pivot, q) == 1, "nongeneric northeast pivot")
        pivots.append(pivot)
        invpivot = pow(pivot, -1, modulus)
        for i in range(k + 1, n):
            c = -a[i][column] * invpivot % modulus
            if c:
                a[i] = [(x + c * y) % modulus for x, y in zip(a[i], a[k])]
                left[i] = [(x + c * y) % modulus for x, y in zip(left[i], left[k])]
                row_ops.append((i, k, c))
        for j in range(column):
            c = -a[k][j] * invpivot % modulus
            if c:
                for i in range(n):
                    a[i][j] = (a[i][j] + c * a[i][column]) % modulus
                    right[i][j] = (right[i][j] + c * right[i][column]) % modulus
                col_ops.append((column, j, c))
    expected = [[0] * n for _ in range(n)]
    for k, p in enumerate(pivots):
        expected[k][n - 1 - k] = p
    require(a == expected, "complete rank-r cross block")
    for normalizer in (left, right):
        require(all(normalizer[i][i] == 1 and all(normalizer[i][j] == 0
                    for j in range(i + 1, n)) for i in range(n)), "unit lower normalizer")
    li, ri = inverse(left, q, modulus), inverse(right, q, modulus)
    change = block_diagonal(left, ri)
    change_inverse = block_diagonal(li, right)
    g = multiply(multiply(change, residual(projector, [1] * n, modulus), modulus),
                 change_inverse, modulus)
    delta = add(g, eye(2 * n), modulus, -1)
    a0 = [row[:n] for row in delta[:rank]]
    b = [[delta[n + i][2 * n - 1 - k] * pow(pivots[k], -1, modulus) % modulus
          for k in range(rank)] for i in range(n)]
    u = [[int(i == k) for k in range(rank)] for i in range(n)] + b
    v = [row[:] for row in delta[:rank]]
    require(multiply(u, v, modulus) == delta, "full split factorization")
    require(multiply(v, u, modulus) == [[-2 * x % modulus for x in row]
                                     for row in eye(rank)], "VU equals minus two")
    # K=-(B+F D^-1)E^t + F D^-1 A0 (I-EE^t).
    k_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(rank):
            k_matrix[i][k] = (-b[i][k] - int(i == n - 1 - k)
                              * pow(pivots[k], -1, modulus)) % modulus
    for k in range(rank):
        for j in range(rank, n):
            k_matrix[n - 1 - k][j] = pow(pivots[k], -1, modulus) * a0[k][j] % modulus
    actual = multiply(multiply(shear(k_matrix, modulus), g, modulus),
                      shear(k_matrix, modulus, -1), modulus)
    require(actual == weighted_swap(n, pivots, [1] * n, modulus), "source normal form")
    return NormalForm(q, modulus, rank, left, right, li, ri, k_matrix,
                      tuple(pivots), tuple(row_ops), tuple(col_ops))


def weighted_adapters(form, weights):
    modulus, n = form.modulus, len(form.left)
    require(len(weights) == n and all(gcd(a, form.q) == 1 for a in weights), "unit parent weights")
    ai = [pow(a, -1, modulus) for a in weights]
    def twist(matrix):
        return [[weights[i] * x * ai[j] % modulus for j, x in enumerate(row)]
                for i, row in enumerate(matrix)]
    return (twist(form.left), twist(form.left_inverse),
            [[x * ai[j] % modulus for j, x in enumerate(row)] for row in form.cross_shear])


@dataclass(frozen=True)
class ChildDescriptor:
    """An explicit finite descriptor for A_child[k*f+j]=A[k*f+j]*pivot[k].

    Parent weights and pivots have already been evaluated on the complete
    parent row, which is an ancestor at the child. No fresh child field is an
    argument to evaluation. Parent weight evaluation/time remains inherited.
    """
    modulus: int
    atom_columns: int
    parent_weights: tuple
    pivots: tuple

    def values(self):
        f = self.atom_columns
        require(1 <= f <= 3 and len(self.parent_weights) >= len(self.pivots) * f,
                "bounded descriptor shape")
        return tuple(self.parent_weights[k * f + j] * pivot % self.modulus
                     for k, pivot in enumerate(self.pivots) for j in range(f))


def execute(form, parent_weights, f, head, tail, *, wrong_child_order=False,
            omit_tail_atom_reversal=False, omit_restore=False):
    """Adapters, one contiguous F_A_child, inverse adapters; no spectator access."""
    n, modulus = len(form.left), form.modulus
    require(1 <= f <= 3 and len(head) == len(tail) == len(parent_weights) == n * f,
            "bounded execution shape")
    h, d = list(head), list(tail)
    adapters = []
    for j in range(f):
        weights = parent_weights[j::f]
        require(all(gcd(a, form.q) == 1 for a in weights), "unit parent weights")
        ai = [pow(a, -1, modulus) for a in weights]
        row_ops = [(i, k, weights[i] * c * ai[k] % modulus)
                   for i, k, c in form.row_additions]
        cross_ops = tuple((i, k, x * ai[k] % modulus)
                          for i, row in enumerate(form.cross_shear)
                          for k, x in enumerate(row) if x)
        hj, dj = h[j::f], d[f - 1 - j::f]
        for i, k, c in row_ops:
            hj[i] = (hj[i] + c * hj[k]) % modulus
        # R=E1 E2 ...; R^-1 on a column executes E1^-1 first.
        for i, k, c in form.column_additions:
            dj[i] = (dj[i] - c * dj[k]) % modulus
        # Every cross-bank ADD reads the unchanged head bank. These ADDs
        # commute, but retain a concrete order and invert it below.
        for i, k, c in cross_ops:
            dj[i] = (dj[i] + c * hj[k]) % modulus
        h[j::f], d[f - 1 - j::f] = hj, dj
        adapters.append((row_ops, cross_ops))
    values = ChildDescriptor(modulus, f, tuple(parent_weights), form.pivots).values()
    if wrong_child_order:
        values = tuple(parent_weights[k * f + j] * form.pivots[k] % modulus
                       for j in range(f) for k in range(form.rank))
    # One reversed call on head prefix [0,rf) and tail suffix [(n-r)f,nf).
    for a, weight in enumerate(values):
        k, j = divmod(a, f)
        b = n * f - 1 - a
        if omit_tail_atom_reversal:
            b = (n - 1 - k) * f + j
        h[a], d[b] = weight * d[b] % modulus, pow(weight, -1, modulus) * h[a] % modulus
    if not omit_restore:
        for j, (row_ops, cross_ops) in enumerate(adapters):
            hj, dj = h[j::f], d[f - 1 - j::f]
            for i, k, c in reversed(cross_ops):
                dj[i] = (dj[i] - c * hj[k]) % modulus
            for i, k, c in reversed(row_ops):
                hj[i] = (hj[i] - c * hj[k]) % modulus
            for i, k, c in reversed(form.column_additions):
                dj[i] = (dj[i] + c * dj[k]) % modulus
            h[j::f], d[f - 1 - j::f] = hj, dj
    return h, d


def direct_action(projector, weights, f, head, tail, modulus):
    """D_P oracle: act on the whole atom vector using the two displayed formulas.

    This uses neither normalizers, pivots, K, the descriptor, nor execute().
    """
    n = len(projector)
    aih = [x * pow(a, -1, modulus) % modulus for x, a in zip(head, weights)]
    reverse_d = list(reversed(tail))
    ph, pd = [0] * (n * f), [0] * (n * f)
    for i in range(n):
        for j in range(f):
            ph[i * f + j] = sum(projector[i][k] * aih[k * f + j] for k in range(n)) % modulus
            pd[i * f + j] = sum(projector[i][k] * reverse_d[k * f + j] for k in range(n)) % modulus
    h = [(x + a * (b - c)) % modulus for x, a, b, c in zip(head, weights, pd, ph)]
    revout = [(x + b - c) % modulus for x, b, c in zip(reverse_d, ph, pd)]
    return h, list(reversed(revout))

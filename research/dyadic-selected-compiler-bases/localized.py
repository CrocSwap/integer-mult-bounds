"""Exact carried bases over a localization of the integers.

Column-basis construction uses unimodular integer Euclidean operations. It
does not assume that arbitrary rational elimination pivots remain units.
"""

from fractions import Fraction as Q
from math import gcd, lcm


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def mul(a, b):
    need(len(a[0]) == len(b), 'Matrix product shape')
    out = [[Q(0) for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, v in enumerate(row):
            if v:
                for j, w in enumerate(b[k]):
                    if w:
                        out[i][j] += v*w
    return out


def add(a, b, scale=1):
    return [[x+scale*y for x, y in zip(u, v)] for u, v in zip(a, b)]


def invdet(a):
    n = len(a)
    need(all(len(row) == n for row in a), 'Inverse needs a square matrix')
    work = [[Q(v) for v in row]+[Q(i == j) for j in range(n)] for i, row in enumerate(a)]
    det = Q(1)
    for k in range(n):
        pivot = next((j for j in range(k, n) if work[j][k]), None)
        need(pivot is not None, 'Singular complete basis')
        if pivot != k:
            work[k], work[pivot] = work[pivot], work[k]
            det = -det
        value = work[k][k]
        det *= value
        work[k] = [x/value for x in work[k]]
        for i in range(n):
            if i != k and work[i][k]:
                factor = work[i][k]
                work[i] = [x-factor*y for x, y in zip(work[i], work[k])]
    return [row[n:] for row in work], det


def columns(a, ids):
    return [[row[j] for j in ids] for row in a]


def concatenate(a, b):
    return [x+y for x, y in zip(a, b)]


def bezout(a, b):
    old_r, r, old_s, s, old_t, t = abs(a), abs(b), 1, 0, 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r-q*r
        old_s, s = s, old_s-q*s
        old_t, t = t, old_t-q*t
    return old_r, old_s*(1 if a >= 0 else -1), old_t*(1 if b >= 0 else -1)


def integer_column_basis(matrix):
    """Return a lattice basis and an exact unimodular-column certificate.

    The output is column echelon, not necessarily canonical reduced HNF.
    It spans exactly the original integer column lattice.
    """
    n, m = len(matrix), len(matrix[0])
    a = [list(map(int, row)) for row in matrix]
    need(a == matrix, 'Column-basis input must be integral')
    u = [[int(i == j) for j in range(m)] for i in range(m)]
    rank = 0
    for row in range(n):
        pivot = next((j for j in range(rank, m) if a[row][j]), None)
        if pivot is None:
            continue
        for table in (a, u):
            for line in table:
                line[rank], line[pivot] = line[pivot], line[rank]
        for j in range(rank+1, m):
            if not a[row][j]:
                continue
            x, y = a[row][rank], a[row][j]
            g, s, t = bezout(x, y)
            need(s*x+t*y == g and g > 0, 'Bezout certificate')
            for table in (a, u):
                for line in table:
                    left, right = line[rank], line[j]
                    line[rank] = s*left+t*right
                    line[j] = -(y//g)*left+(x//g)*right
        if a[row][rank] < 0:
            for table in (a, u):
                for line in table:
                    line[rank] = -line[rank]
        rank += 1
        if rank == m:
            break
    need(all(not value for row in a for value in row[rank:]), 'Unremoved dependent column')
    need(mul(matrix, u) == a, 'Column transformation certificate')
    _, determinant = invdet(u)
    need(abs(determinant) == 1, 'Column transformation must be unimodular')
    return columns(a, range(rank)), u


def diagonal_projector(n, active):
    active = set(active)
    need(all(type(i) is int and 0 <= i < n for i in active), 'Invalid active coordinate')
    return [[Q(i == j and i in active) for j in range(n)] for i in range(n)]


def integral_split_basis(projector):
    """Complete image/kernel bases using only integral lattice operations."""
    n = len(projector)
    need(all(len(row) == n for row in projector), 'Square projector required')
    need(mul(projector, projector) == projector, 'Not an idempotent')
    scale = lcm(*(Q(v).denominator for row in projector for v in row))
    complement = add(eye(n), projector, -1)
    left, _ = integer_column_basis([[int(scale*v) for v in row] for row in projector])
    right, _ = integer_column_basis([[int(scale*v) for v in row] for row in complement])
    r = len(left[0])
    basis = concatenate(left, right)
    inverse, det = invdet(basis)
    need(mul(projector, left) == left and all(not v for row in mul(projector, right) for v in row),
         'Wrong image/kernel summands')
    need(mul(mul(inverse, projector), basis) == diagonal_projector(n, range(r)),
         'Complete normalized projector identity')
    need(det.denominator == 1 and scale**n % abs(det.numerator) == 0,
         'Lattice index introduced a new prime')
    return basis, inverse, r, scale, det


def direct_sum(a, b):
    return [row+[Q(0)]*len(b[0]) for row in a]+[[Q(0)]*len(a[0])+row for row in b]


def kron(a, b):
    return [[v*w for v in row_a for w in row_b] for row_a in a for row_b in b]


def permutation(order):
    n = len(order)
    need(sorted(order) == list(range(n)), 'Placement is not a permutation')
    # Columns are the old-coordinate vectors in their new basis order.
    return [[Q(i == order[j]) for j in range(n)] for i in range(n)]


def split_in_carried_basis(basis, rank, selected):
    n = len(basis)
    selected = tuple(selected)
    need(len(set(selected)) == len(selected) and all(0 <= x < rank for x in selected),
         'Split must select distinct image coordinates')
    order = selected+tuple(j for j in range(n) if j not in selected)
    return mul(basis, permutation(order))


def matcher(left, left_rank, right, right_rank):
    need(left_rank == right_rank and len(left) == len(right), 'Whole-job rank/ambient mismatch')
    inverse, _ = invdet(right)
    return mul(left, inverse)


def dyadic(x):
    q = Q(x).denominator
    return q > 0 and q & (q-1) == 0


def dyadic_unit(x):
    x = abs(Q(x))
    return x != 0 and dyadic(x) and x.numerator & (x.numerator-1) == 0

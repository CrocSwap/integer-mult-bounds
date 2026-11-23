"""Choose split frames in Z_(3) and obtain the factors of a covered leaf."""

from fractions import Fraction


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def transpose(matrix):
    return [list(column) for column in zip(*matrix, strict=True)]


def multiply(left, right):
    columns = transpose(right)
    return [[sum(a * b for a, b in zip(row, column, strict=True)) for column in columns] for row in left]


def residue(value, modulus):
    x = Fraction(value)
    return x.numerator * pow(x.denominator, -1, modulus) % modulus


def inverse(matrix):
    """Invert an integral-at-three matrix, choosing only unit pivots."""
    n = len(matrix)
    rows = [list(map(Fraction, row + unit)) for row, unit in zip(matrix, identity(n), strict=True)]
    for j in range(n):
        p = next(i for i in range(j, n) if residue(rows[i][j], 3))
        rows[j], rows[p] = rows[p], rows[j]
        pivot = rows[j][j]
        rows[j] = [x / pivot for x in rows[j]]
        for i, row in enumerate(rows):
            if i != j and row[j]:
                scale = row[j]
                rows[i] = [x - scale * y for x, y in zip(row, rows[j], strict=True)]
    return [row[n:] for row in rows]


def projector(frame, rank):
    """Form an idempotent using the first rank columns of the split frame."""
    projected = [[a if j < rank else 0 for j, a in enumerate(row)] for row in frame]
    return multiply(projected, inverse(frame))


def frame_at_three(p):
    """Return an exact rational image/kernel frame and its image rank."""
    n = len(p)
    columns = transpose(p)
    pivots = {}
    chosen = []

    def insert(column):
        work = [residue(x, 3) for x in column]
        for k, v in sorted(pivots.items()):
            if work[k]:
                a = work[k]
                work = [(x - a * y) % 3 for x, y in zip(work, v, strict=True)]
        leading = next((k for k, x in enumerate(work) if x), None)
        if leading is not None:
            s = pow(work[leading], -1, 3)
            pivots[leading] = [x * s % 3 for x in work]
            chosen.append(column)

    for column in columns:
        insert(column)
    rank = len(chosen)
    for j, column in enumerate(columns):
        insert([int(i == j) - x for i, x in enumerate(column)])
    if len(chosen) != n:
        raise ValueError("The image and kernel did not span the residue space")
    return transpose(chosen), rank


def matcher(source, target):
    """Obtain S with source*S=S*target for equal-rank idempotents."""
    left, r = frame_at_three(source)
    right, s = frame_at_three(target)
    if r != s:
        raise ValueError("Projector ranks differ")
    return multiply(left, inverse(right))


def split(p, first):
    """Split an idempotent at a positive image rank in its computed frame."""
    frame, rank = frame_at_three(p)
    if not 0 < first < rank:
        raise ValueError("The split must have two positive parts")
    left = projector(frame, first)
    right = [[a - b for a, b in zip(row, sub, strict=True)] for row, sub in zip(p, left, strict=True)]
    return left, right


def native_factors(p):
    """Read two exact factors from any split rank-one projector."""
    i = next(k for k, row in enumerate(p) if residue(row[k], 3))
    return [Fraction(row[i]) / p[i][i] for row in p], list(p[i])


def covered_factors(native, cover_row, digits):
    """Compute g*u and v*g^-1 on the full ring without forming g*P*g^-1."""
    modulus = 3**digits
    u, v = ([residue(x, modulus) for x in factor] for factor in native)
    placed_u = [sum(x * y for x, y in zip(row, u, strict=True)) % modulus for row in cover_row]
    n = len(cover_row)
    rows = [list(row) + [v[i]] for i, row in enumerate(transpose(cover_row))]
    for j in range(n):
        k = next(i for i in range(j, n) if rows[i][j] % 3)
        rows[j], rows[k] = rows[k], rows[j]
        scale = pow(rows[j][j], -1, modulus)
        rows[j][j:] = [x * scale % modulus for x in rows[j][j:]]
        for i in range(j + 1, n):
            scale = rows[i][j]
            if scale:
                rows[i][j:] = [(a - scale * b) % modulus for a, b in zip(rows[i][j:], rows[j][j:], strict=True)]
    placed_v = [0] * n
    for j in reversed(range(n)):
        placed_v[j] = (rows[j][-1] - sum(rows[j][i] * placed_v[i] for i in range(j + 1, n))) % modulus
    return placed_u, placed_v

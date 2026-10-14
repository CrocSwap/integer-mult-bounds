"""Exact binary subspace checks for the complex phase-network interface.

Vectors are integer bit masks. A nondegenerate residual must also be
nonalternating to use the upstream one-kernel-per-dimension interface.
"""


def dot(a, b):
    return (a & b).bit_count() & 1


def basis(rows):
    pivots = {}
    for row in rows:
        assert isinstance(row,int) and row>=0, 'Binary vectors must be nonnegative masks'
        while row:
            p = row.bit_length()-1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def contains(space, vector):
    return len(basis((*space, vector))) == len(basis(space))


def nullspace(rows, dimension):
    rows = list(basis(rows))
    assert dimension>=0 and all(row < (1<<dimension) for row in rows)
    pivots = []
    row = 0
    for col in range(dimension):
        pivot = next((j for j in range(row, len(rows)) if rows[j] >> col & 1), None)
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        for j in range(len(rows)):
            if j != row and rows[j] >> col & 1:
                rows[j] ^= rows[row]
        pivots.append(col)
        row += 1
    result = []
    for col in range(dimension):
        if col in pivots:
            continue
        value = 1 << col
        for j, p in enumerate(pivots):
            if rows[j] >> col & 1:
                value |= 1 << p
        result.append(value)
    return tuple(result)


def classify(rows):
    rows = basis(rows)
    gram = [sum(dot(a, b) << i for i, b in enumerate(rows)) for a in rows]
    return dict(dimension=len(rows), nondegenerate=len(basis(gram)) == len(rows),
                nonalternating=any(dot(v, v) for v in rows))


def residual(lower, upper):
    lower, upper = basis(lower), basis(upper)
    assert classify(lower)['nondegenerate'] and classify(upper)['nondegenerate']
    assert all(contains(upper, x) for x in lower)
    constraints = [sum(dot(u, v) << j for j, v in enumerate(upper)) for u in lower]
    out = []
    for coefficients in nullspace(constraints, len(upper)):
        value = 0
        for j, vector in enumerate(upper):
            if coefficients >> j & 1:
                value ^= vector
        out.append(value)
    assert len(out) == len(upper)-len(lower)
    return tuple(out)


def orthonormal_basis(rows):
    """Construct a basis, rejecting nonzero alternating or degenerate spaces."""
    work = list(basis(rows))
    dimension = len(work)
    assert classify(work)['nondegenerate'], 'Degenerate frame residual'
    units = []
    while any(dot(x, x) for x in work):
        i = next(i for i, x in enumerate(work) if dot(x, x))
        v = work.pop(i)
        units.append(v)
        work = list(basis(x ^ (v if dot(x, v) else 0) for x in work))
    if work:
        assert units, 'Nonzero alternating residual needs a different kernel interface'
    while work:
        a = work[0]
        b = next(x for x in work if dot(a, x))
        rest = basis(x ^ (a if dot(x, b) else 0) ^ (b if dot(x, a) else 0)
                     for x in work)
        w = units.pop()
        units.extend((w ^ a, w ^ b, w ^ a ^ b))
        work = list(rest)
    assert len(units) == dimension
    assert all(dot(a, b) == (i == j) for i, a in enumerate(units)
               for j, b in enumerate(units))
    return tuple(units)


def certify_chain(chain):
    """Return exact residual dimensions and explicit orthonormal bases."""
    result = []
    for lower, upper in zip(chain, chain[1:]):
        vectors = orthonormal_basis(residual(lower, upper))
        result.append(dict(dimension=len(vectors), orthonormal_basis=list(vectors)))
    return result

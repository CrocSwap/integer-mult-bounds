"""Exact matrices and generic support tests. Nick Petalas. Apache-2.0."""

from fractions import Fraction
from itertools import permutations, product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    require(1 <= n <= 6, "matrix dimension must be between one and six")
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def multiply(a, b):
    n = len(a)
    require(1 <= n <= 6 and len(b) == n, "incompatible dimensions")
    require(all(len(row) == n for row in a + b), "matrices must be square")
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def inverse(a):
    n = len(a)
    require(1 <= n <= 6 and all(len(row) == n for row in a), "bad matrix")
    aug = [[Fraction(value) for value in a[i]] + list(identity(n)[i])
           for i in range(n)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if aug[i][col]), None)
        require(pivot is not None, "singular matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [value / scale for value in aug[col]]
        for i in range(n):
            if i != col:
                scale = aug[i][col]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[col], strict=True)]
    require(tuple(tuple(row[:n]) for row in aug) == identity(n), "bad elimination")
    return tuple(tuple(row[n:]) for row in aug)


def negate(a):
    return tuple(tuple(-x for x in row) for row in a)


def expand_blocks(a):
    return tuple(tuple(a[i // 2][j // 2][i % 2][j % 2]
                       for j in range(6)) for i in range(6))


def witness():
    unit, zero = identity(2), ((0, 0), (0, 0))
    t = ((0, -1), (1, -1))
    t2 = multiply(t, t)
    b = ((zero, unit, unit), (unit, zero, unit), (unit, t, zero))
    p = ((t2, negate(t2), negate(t)), (negate(t), t, negate(t)),
         (negate(t2), negate(t), t))
    return expand_blocks(p), expand_blocks(b)


def masks(a, b, sizes):
    n = sum(sizes)
    require(len(a) == len(b) == n and n <= 6, "bad signature dimensions")
    require(all(size > 0 for size in sizes), "empty block")
    require(all(len(row) == n for row in a + b), "bad signature matrix")
    blocks, start = [], 0
    for size in sizes:
        blocks.append(tuple(range(start, start + size)))
        start += size
    source = tuple(sum(1 << k for k, rows in enumerate(blocks)
                       if any(a[i][j] for i in rows)) for j in range(n))
    reader = tuple(sum(1 << k for k, rows in enumerate(blocks)
                       if any(b[j][i] for i in rows)) for j in range(n))
    return source, reader


def matching_terms(n):
    require(1 <= n <= 6, "unsupported generic dimension")
    terms = tuple((sum(1 << (i * n + p[i]) for i in range(n)), p)
                  for p in permutations(range(n)))
    cofactors = []
    for removed_row in range(n):
        rows = tuple(i for i in range(n) if i != removed_row)
        row_terms = []
        for removed_col in range(n):
            cols = tuple(j for j in range(n) if j != removed_col)
            row_terms.append(tuple(sum(1 << (i * n + col)
                                       for i, col in zip(rows, perm, strict=True))
                                   for perm in permutations(cols)))
        cofactors.append(tuple(row_terms))
    return terms, tuple(cofactors)


def generic_inverse(support, n, terms, cofactors):
    require(0 <= support < 1 << (n * n), "support outside matrix")
    match = next((p for bits, p in terms if support & bits == bits), None)
    if match is None:
        return None, None
    result = tuple(tuple(int(any(support & bits == bits for bits in cofactors[i][j]))
                         for i in range(n)) for j in range(n))
    return result, match


def reach_inverse(support, n, match):
    """Alternating paths, computed without the cofactor matching test."""
    row_for_col = [0] * n
    for row, col in enumerate(match):
        row_for_col[col] = row
    reach = [1 << i for i in range(n)]
    for i in range(n):
        for j in range(n):
            if support & (1 << (i * n + j)):
                reach[i] |= 1 << row_for_col[j]
    for middle in range(n):
        for i in range(n):
            if reach[i] & (1 << middle):
                reach[i] |= reach[middle]
    return tuple(tuple((reach[row_for_col[j]] >> i) & 1 for i in range(n))
                 for j in range(n))


def full_source_supports(sizes):
    n = sum(sizes)
    require(1 <= n <= 6 and all(1 <= s <= 2 for s in sizes), "bad support domain")
    offsets, start = [], 0
    for size in sizes:
        offsets.append(start)
        start += size
    columns = tuple(sum(bits << offset for bits, offset in zip(parts, offsets, strict=True))
                    for parts in product(*(range(1, 1 << size) for size in sizes)))
    for choice in product(columns, repeat=n):
        yield sum(1 << (i * n + j) for j in range(n) for i in range(n)
                  if choice[j] & (1 << i))


def support_matrix(support, n):
    require(1 <= n <= 6 and 0 <= support < 1 << (n * n), "bad support")
    return tuple(tuple((support >> (i * n + j)) & 1 for j in range(n))
                 for i in range(n))

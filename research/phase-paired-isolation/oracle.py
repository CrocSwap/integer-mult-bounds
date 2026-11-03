"""Small exhaustive oracles, separate from the constructive elimination.

Produced by Nick Petalas. Apache-2.0.
"""

from itertools import product


def binary_inverse(rows):
    n = len(rows)
    work = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for column in range(n):
        pivot = next((i for i in range(column, n) if work[i] >> column & 1), None)
        if pivot is None:
            return None
        work[column], work[pivot] = work[pivot], work[column]
        for i in range(n):
            if i != column and work[i] >> column & 1:
                work[i] ^= work[column]
    return tuple(row >> n for row in work)


def binary_product(left, right):
    columns = tuple(sum(((row >> j) & 1) << i for i, row in enumerate(right))
                    for j in range(len(right)))
    return tuple(sum(((row & column).bit_count() & 1) << j
                     for j, column in enumerate(columns)) for row in left)


def binary_group(n):
    if n not in (1, 2, 3):
        raise ValueError("Binary oracle dimension outside capacity")
    result = []
    for rows in product(range(1 << n), repeat=n):
        back = binary_inverse(rows)
        if back is not None:
            result.append((rows, back))
    return result


def binary_block(rows):
    n = len(rows)
    best = 0
    for size in range(1, n + 1):
        valid = all(((rows[i] >> j) & 1) == int(i == j)
                    for i in range(n) for j in range(n) if i < size or j < size)
        if valid:
            best = size
    return best


def binary_matrix(rows):
    return tuple(tuple((row >> j) & 1 for j in range(len(rows))) for row in rows)


def similarity_capacity(rows, group):
    best = 0
    for basis, back in group:
        changed = binary_product(binary_product(back, rows), basis)
        best = max(best, binary_block(changed))
    return best


def ternary_group():
    result = []
    for a, b, c, d in product(range(3), repeat=4):
        determinant = (a * d - b * c) % 3
        if determinant:
            scale = pow(determinant, -1, 3)
            back = ((d * scale % 3, -b * scale % 3),
                    (-c * scale % 3, a * scale % 3))
            result.append((((a, b), (c, d)), back))
    return result


def ternary_product(left, right):
    return (((left[0][0] * right[0][0] + left[0][1] * right[1][0]) % 3,
             (left[0][0] * right[0][1] + left[0][1] * right[1][1]) % 3),
            ((left[1][0] * right[0][0] + left[1][1] * right[1][0]) % 3,
             (left[1][0] * right[0][1] + left[1][1] * right[1][1]) % 3))


def ternary_block(rows):
    if rows == ((1, 0), (0, 1)):
        return 2
    return int(rows[0][0] == 1 and rows[0][1] == rows[1][0] == 0)

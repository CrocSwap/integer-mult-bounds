"""Exact finite matrices for the six bit-permutation orbit blocks.

The exterior-power model is credited to Jacob Sussman's PR6706.
This implementation computes the new coarsened cut tables directly.
"""

from itertools import combinations, permutations
from math import gcd


def planes_and_orbits():
    planes = sorted(
        {tuple(sorted((0, a, b, a ^ b))) for a, b in combinations(range(1, 16), 2)}
    )
    assert len(planes) == 35
    actions = tuple(permutations(range(4)))
    orbits = []
    seen = set()
    for index, plane in enumerate(planes):
        if index in seen:
            continue
        images = set()
        for action in actions:
            image = tuple(sorted(sum(((x >> j) & 1) << action[j] for j in range(4))
                                 for x in plane))
            images.add(planes.index(image))
        orbit = sorted(images)
        seen.update(orbit)
        orbits.append(orbit)
    assert sorted(map(len, orbits)) == [3, 4, 4, 6, 6, 12]
    return planes, orbits


def call_matrix(direction, planes):
    if direction not in (1, 2, 4, 8):
        raise ValueError("this package uses the four single-bit directions")
    representatives = {plane[:3]: index for index, plane in enumerate(planes)}
    # (1+i)^(3-k) (1-i)^k for k=0,1,2,3.
    coefficients = ((-2, 2), (2, 2), (2, -2), (-2, -2))
    real = [[0] * 35 for _ in range(35)]
    imag = [[0] * 35 for _ in range(35)]
    for column, plane in enumerate(planes):
        for shift in range(16):
            for choice in range(8):
                xs = tuple(plane[j] ^ shift ^ (direction if choice >> j & 1 else 0)
                           for j in range(3))
                ordered = tuple(sorted(xs))
                if ordered not in representatives:
                    continue
                row = representatives[ordered]
                sign = (-1) ** sum(xs[i] > xs[j] for i in range(3)
                                   for j in range(i + 1, 3))
                a, b = coefficients[choice.bit_count()]
                real[row][column] += sign * a
                imag[row][column] += sign * b
    assert all(value == 0 for row in imag for value in row)
    return real


def multiply(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(35))
             for j in range(35)] for i in range(35)]


def integer_rank(matrix, rows, columns):
    work = [[matrix[i][j] for j in columns] for i in rows]
    pivot = 0
    for column in range(len(columns)):
        found = next((i for i in range(pivot, len(work)) if work[i][column]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        scale = work[pivot][column]
        for i in range(pivot + 1, len(work)):
            factor = work[i][column]
            if not factor:
                continue
            row = [scale * x - factor * y for x, y in zip(work[i], work[pivot])]
            divisor = gcd(*row)
            work[i] = [x // divisor for x in row] if divisor else row
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def cut_tables():
    planes, orbits = planes_and_orbits()
    calls = [call_matrix(w, planes) for w in (1, 2, 4, 8)]
    target = multiply(multiply(multiply(calls[0], calls[1]), calls[2]), calls[3])
    blocks = [tuple(i for j, orbit in enumerate(orbits) if mask >> j & 1 for i in orbit)
              for mask in range(64)]
    subsets = [[b for b in range(64) if b & a == b] for a in range(64)]
    tables = []
    for matrix in (calls[0], target):
        table = [[None] * 64 for _ in range(64)]
        for a in range(64):
            for b in subsets[a]:
                table[a][b] = integer_rank(matrix, blocks[b], blocks[63 ^ a])
        tables.append(table)
    assert sum(map(len, subsets)) == 729
    return planes, orbits, subsets, tables[0], tables[1]

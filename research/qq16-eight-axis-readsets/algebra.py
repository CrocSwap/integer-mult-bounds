"""Exact small rational matrices. Gareth Davidson / OpenAI Codex, Apache-2.0."""
from fractions import Fraction as Q


def rref(rows):
    a = [[Q(x) for x in row] for row in rows]
    width = len(a[0]) if a else 0
    pivots = []
    for j in range(width):
        k = next((k for k in range(len(pivots), len(a)) if a[k][j]), None)
        if k is None:
            continue
        i = len(pivots)
        a[i], a[k] = a[k], a[i]
        scale = a[i][j]
        a[i] = [x / scale for x in a[i]]
        for k in range(len(a)):
            if k != i and a[k][j]:
                scale = a[k][j]
                a[k] = [x - scale * y for x, y in zip(a[k], a[i])]
        pivots.append(j)
        if len(pivots) == len(a):
            break
    return a, pivots


def rank(rows):
    return len(rref(rows)[1])


def null_vector(rows):
    a, pivots = rref(rows)
    width = len(a[0])
    free = next((j for j in range(width) if j not in pivots), None)
    if free is None:
        raise ValueError('columns are independent')
    v = [Q(0)] * width
    v[free] = 1
    for i, j in enumerate(pivots):
        v[j] = -a[i][free]
    return v


def inverse(rows):
    n = len(rows)
    a, pivots = rref([list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(rows)])
    if pivots != list(range(n)):
        raise ValueError('singular inverse')
    return [row[n:] for row in a]


def mv(matrix, vector):
    return [sum(x * y for x, y in zip(row, vector)) for row in matrix]

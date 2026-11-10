"""Ordinary matrix minors and a brute-force labeled-order oracle."""
from itertools import combinations, permutations


def reduce_matrix(f, square, inverse=False):
    n = len(square)
    a = [list(row) + ([int(i == j) for j in range(n)] if inverse else [])
         for i, row in enumerate(square)]
    det = 1
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        if pivot is None:
            return 0, ()
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            det = f.neg[det]
        factor = a[j][j]
        det = f.mul[det][factor]
        a[j] = [f.mul[f.inv[factor]][x] for x in a[j]]
        for i in range(n):
            if i != j and a[i][j]:
                scalar = f.neg[a[i][j]]
                a[i] = [f.add[x][f.mul[scalar][y]] for x,y in zip(a[i], a[j])]
    inv = tuple(tuple(row[n:]) for row in a) if inverse else ()
    return det, inv


def complement(f, u, row):
    return tuple(tuple(f.add[int(i == j)][f.neg[f.mul[x][y]]] for j,y in enumerate(row))
                 for i,x in enumerate(u))


def pass_subset(f, matrices, indices):
    for matrix in matrices:
        minor = [[matrix[i][j] for j in indices] for i in indices]
        if reduce_matrix(f, minor)[0] == 0:
            return False
    return True


def identity_pass(f, u, rows):
    matrices = [complement(f, u, row) for row in rows]
    return all(pass_subset(f, matrices, range(length)) for length in range(1, len(u)))


def literal_orders(f, u, rows):
    """Build actual principal submatrices; list every full labeled order."""
    m = len(u)
    matrices = [complement(f, u, row) for row in rows]
    admissible = set()
    for length in range(1, m):
        for sub in combinations(range(m), length):
            if pass_subset(f, matrices, sub):
                admissible.add(frozenset(sub))
    return sum(all(frozenset(order[:j]) in admissible for j in range(1, m))
               for order in permutations(range(m)))


def product(f, a, b):
    columns = list(zip(*b))
    return tuple(tuple(f.dot(row, col) for col in columns) for row in a)

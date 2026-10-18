"""Attributed local-ring preparations, adapted from PR2234 and PR2364.

These host arithmetic macros have the schoolbook lowering in PROOF.md.
They do not supply measured binary-arithmetic transition counts.
"""
from math import gcd
from tapes import need


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b, modulus):
    out = [[0] * len(b[0]) for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] = (out[i][j] + x*y) % modulus
    return out


def inverse(a, modulus):
    n = len(a)
    rows = [list(row) + unit for row, unit in zip(a, eye(n))]
    for j in range(n):
        pivot = next((i for i in range(j, n) if gcd(rows[i][j], modulus) == 1), None)
        need(pivot is not None, "unit matrix pivot")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        u = pow(rows[j][j], -1, modulus)
        rows[j] = [x*u % modulus for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                c = rows[i][j]
                rows[i] = [(x-c*y) % modulus for x, y in zip(rows[i], rows[j])]
    need([row[:n] for row in rows] == eye(n), "inverse endpoint")
    return [row[n:] for row in rows]


def independent_columns(a, q):
    rows, rank, columns = [[x % q for x in row] for row in a], 0, []
    for j in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        u = pow(rows[rank][j], -1, q)
        rows[rank] = [x*u % q for x in rows[rank]]
        for i in range(len(a)):
            if i != rank and rows[i][j]:
                c = rows[i][j]
                rows[i] = [(x-c*y) % q for x, y in zip(rows[i], rows[rank])]
        columns.append(j)
        rank += 1
        if rank == len(a):
            break
    return columns


def split_basis(p, rank, q, modulus):
    n = len(p)
    other = [[(int(i == j)-p[i][j]) % modulus for j in range(n)] for i in range(n)]
    image, kernel = independent_columns(p, q), independent_columns(other, q)
    need((len(image), len(kernel)) == (rank, n-rank), "source projector rank")
    basis = [[p[i][j] for j in image] + [other[i][j] for j in kernel] for i in range(n)]
    need(projector(basis, rank, modulus) == p, "actual image/kernel basis")
    return basis


def projector(h, rank, modulus):
    inv = inverse(h, modulus)
    return multiply([row[:rank] for row in h], inv[:rank], modulus)


def good_pivots(p, rank, modulus):
    a, pivots = [list(row) for row in p], []
    for k in range(rank):
        pivot = a[k][k]
        need(gcd(pivot, modulus) == 1, "nongeneric low class")
        pivots.append(pivot)
        inv = pow(pivot, -1, modulus)
        for i in range(k+1, len(a)):
            c = a[i][k] * inv % modulus
            a[i] = [(x-c*y) % modulus for x, y in zip(a[i], a[k])]
    return tuple(pivots)


def fallback_table(p, modulus):
    n = len(p)
    a = [[0] * (2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            a[i][j] = a[2*n-1-i][2*n-1-j] = (int(i == j)-p[i][j]) % modulus
            a[i][2*n-1-j] = a[2*n-1-i][j] = p[i][j]
    pi = list(range(2*n))
    for j in range(2*n):
        pivot = next((i for i in range(j, 2*n) if gcd(a[i][j], modulus) == 1), None)
        need(pivot is not None, "fallback unit pivot")
        a[j], a[pivot], pi[j], pi[pivot] = a[pivot], a[j], pi[pivot], pi[j]
        inv = pow(a[j][j], -1, modulus)
        for i in range(2*n):
            if i != j and a[i][j]:
                c = a[i][j] * inv % modulus
                a[i] = [(x-c*y) % modulus for x, y in zip(a[i], a[j])]
    need(all(not a[i][j] for i in range(2*n) for j in range(2*n) if i != j),
         "fallback terminal diagonal")
    return tuple(a[i][i] for i in range(2*n)), tuple(pi)

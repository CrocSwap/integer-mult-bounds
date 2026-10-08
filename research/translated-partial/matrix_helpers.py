"""Small exact finite-field matrices for bounded algebra controls.

Copyright 2026 Zhihao Chen (jacklightChen). Apache-2.0.
These elementary helpers perform no floating-point operations.
"""
P = 65521


def ident(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col)) % P for col in zip(*b)] for row in a]


def subtract(a, b):
    return [[(x-y) % P for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def inv(a):
    n = len(a)
    a = [list(row)+e for row, e in zip(a, ident(n))]
    for j in range(n):
        k = next((k for k in range(j, n) if a[k][j]), None)
        if k is None:
            raise ValueError('singular')
        a[j], a[k] = a[k], a[j]
        d = pow(a[j][j], -1, P)
        a[j] = [x*d % P for x in a[j]]
        for k in range(n):
            if k != j:
                f = a[k][j]
                a[k] = [(x-f*y) % P for x, y in zip(a[k], a[j])]
    return [row[n:] for row in a]


def randinv(n, rng):
    while True:
        a = [[rng.randrange(P) for _ in range(n)] for _ in range(n)]
        try:
            return a, inv(a)
        except ValueError:
            pass


def pivots(a):
    a = [r[:] for r in a]
    active = set(range(len(a[0])))
    out = []
    for i in range(len(a)):
        js = [j for j in active if a[i][j]]
        if not js:
            continue
        j = max(js)
        out.append((i, j))
        active.remove(j)
        c = pow(a[i][j], -1, P)
        for k in range(i+1, len(a)):
            f = a[k][j]*c % P
            if f:
                a[k] = [(x-f*y) % P for x, y in zip(a[k], a[i])]
    return out

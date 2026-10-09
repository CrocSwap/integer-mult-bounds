#!/usr/bin/env python3
"""Exact sufficient rejection checks for a common triangular frame flag.

The written theorem applies over any characteristic-zero splitting field.
The explicit-basis check uses rational arithmetic; commuting rational frames
are covered even when their common triangularizing basis is not rational.
"""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations


def matrix(a):
    n = len(a)
    if not n or any(len(row) != n for row in a):
        raise ValueError("Square nonempty matrices required")
    if any(isinstance(v, float) for row in a for v in row):
        raise ValueError("Use exact entries")
    return tuple(tuple(Q(v) for v in row) for row in a)


def multiply(a, b):
    if len(a) != len(b):
        raise ValueError("Dimensions differ")
    n = len(a)
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(n)), Q(0))
                       for j in range(n)) for i in range(n))


def inverse(a):
    n = len(a)
    rows = [list(a[i]) + [Q(i == j) for j in range(n)] for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            raise ValueError("Singular common basis")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [v / scale for v in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def rejection(frames, basis=None):
    frames = tuple(dict.fromkeys(matrix(a) for a in frames))
    if not frames or any(len(a) != len(frames[0]) for a in frames):
        raise ValueError("Nonempty common-dimensional frame family required")
    n = len(frames[0])
    if basis is not None:
        basis = matrix(basis)
        if len(basis) != n:
            raise ValueError("Wrong common basis dimension")
        inv = inverse(basis)
        changed = [multiply(multiply(inv, a), basis) for a in frames]
        if any(a[i][j] for a in changed for i in range(n) for j in range(i)):
            raise ValueError("The supplied common basis does not triangularize every frame")
        return {"rejected": True, "reason": "Exact common triangularizing basis",
                "unique_frames": len(frames), "rank_lower_bound": "W*m"}
    commuting = all(multiply(a, b) == multiply(b, a) for a, b in combinations(frames, 2))
    return {"rejected": commuting,
            "reason": "Pairwise commuting frames" if commuting else "This sufficient screen is inconclusive",
            "unique_frames": len(frames), "rank_lower_bound": "W*m" if commuting else None}

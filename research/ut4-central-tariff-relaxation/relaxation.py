#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact fixtures attaining the isolated middle-factor linear relaxation.

Rows are binary integers, with column zero in the least significant bit.
This constructs four matrices, not a legal UT4 operation word.
Prepared for @ToikY with substantial OpenAI Codex assistance.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return bin(value).count("1") % 2


def row_reduce(rows, width):
    reduced = list(rows)
    pivots = []
    rank = 0
    for column in range(width):
        found = next((i for i in range(rank, len(reduced)) if (reduced[i] >> column) & 1), None)
        if found is None:
            continue
        reduced[rank], reduced[found] = reduced[found], reduced[rank]
        for i in range(len(reduced)):
            if i != rank and (reduced[i] >> column) & 1:
                reduced[i] ^= reduced[rank]
        pivots.append(column)
        rank += 1
    return reduced[:rank], pivots


def kernel_basis(rows, width):
    reduced, pivots = row_reduce(rows, width)
    result = []
    for column in range(width):
        if column not in pivots:
            vector = 1 << column
            for row, pivot in zip(reduced, pivots):
                if (row >> column) & 1:
                    vector |= 1 << pivot
            result.append(vector)
    return result


def dual_solution(constraints, rhs, width):
    """Solve independent binary dot-product constraints, setting free coordinates zero."""
    rows, values = list(constraints), list(rhs)
    rank, pivots = 0, []
    for column in range(width):
        found = next((i for i in range(rank, len(rows)) if (rows[i] >> column) & 1), None)
        if found is None:
            continue
        rows[rank], rows[found] = rows[found], rows[rank]
        values[rank], values[found] = values[found], values[rank]
        for i in range(len(rows)):
            if i != rank and (rows[i] >> column) & 1:
                rows[i] ^= rows[rank]
                values[i] ^= values[rank]
        pivots.append(column)
        rank += 1
    require(rank == len(constraints), "dual constraints are not independent")
    answer = sum(value << pivot for value, pivot in zip(values[:rank], pivots))
    require(all(parity(answer & row) == value for row, value in zip(constraints, rhs)),
            "constructed dual fails a constraint")
    return answer


def transpose(rows, width):
    return [sum(((row >> column) & 1) << i for i, row in enumerate(rows))
            for column in range(width)]


def build(w, r):
    """Return {X,Y,U,V,n}, with X/U r×n and Y/V n×r.

    XY=UY=XV=0 and UV=diag(I_w,0). X and Y have rank w; every
    original middle-factor X column and Y row is nonzero. The fixtures
    attain only these projected equations, with no word-realization claim.
    """
    require(type(w) is int and type(r) is int and 1 <= w <= r,
            "positive target width and r>=w required")
    if w == 1:
        columns = [1, 1, 1, 1]
    else:
        two_blocks = w // 2 if w % 2 == 0 else (w - 3) // 2
        three_blocks = 0 if w % 2 == 0 else 1
        columns, role = [], 0
        for _ in range(two_blocks):
            columns.extend(value << role for value in (1, 1, 2, 2, 3, 3))
            role += 2
        for _ in range(three_blocks):
            columns.extend(value << role for value in (1, 2, 3, 4, 5, 6, 7, 1, 1))
            role += 3
        require(role == w, "block inventory does not cover the requested width")
    n = len(columns)
    require(n == (4 if w == 1 else 3 * w), "middle-factor count differs from the relaxation target")
    X = transpose(columns, r)
    Y = list(columns)
    require(all(columns) and len(row_reduce(X, n)[0]) == w, "X/Y rank or nonzero-coupling property fails")
    require(all(parity(left & right) == 0 for left in X for right in X),
            "X row space is not self-orthogonal")
    representatives, augmented = [], list(X[:w])
    for vector in kernel_basis(X, n):
        if len(row_reduce(augmented + [vector], n)[0]) > len(augmented):
            representatives.append(vector)
            augmented.append(vector)
            if len(representatives) == w:
                break
    require(len(representatives) == w, "kernel quotient lacks the requested representatives")
    require(all(parity(row & vector) == 0 for row in X for vector in representatives),
            "V representative is outside ker(X)")
    constraints = X[:w] + representatives
    U = [dual_solution(constraints, [0] * w + [int(i == j) for j in range(w)], n)
         for i in range(w)] + [0] * (r - w)
    V = transpose(representatives + [0] * (r - w), n)
    require(all(parity(u & x) == 0 for u in U for x in X), "UY is nonzero")
    require(all(parity(x & v) == 0 for x in X for v in representatives), "XV is nonzero")
    require(all(parity(U[i] & representatives[j]) == int(i == j)
                for i in range(w) for j in range(w)), "UV target is not I_w")
    return {"X": X, "Y": Y, "U": U, "V": V, "n": n}


if __name__ == "__main__":
    for width in range(1, 21):
        build(width, width)
        build(width, width + 2)
    print("PASS_UT4_MIDDLE_RELAXATION widths=1..20 padded_roles=2 no_word_claim")

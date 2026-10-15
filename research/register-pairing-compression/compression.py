#!/usr/bin/env python3
"""Exact binary pairing compression; Gareth Davidson, Codex assistance, Apache-2.0.

Vectors and functionals are little-endian bit masks. Maps are mathematical
witnesses for constructing a new word; they are not executed register operations.
"""
from dataclasses import dataclass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return (x & y).bit_count() & 1


def basis(vectors):
    pivots = {}
    chosen = []
    for original in vectors:
        v = original
        for p in sorted(pivots, reverse=True):
            if v >> p & 1:
                v ^= pivots[p]
        if v:
            pivots[v.bit_length() - 1] = v
            chosen.append(original)
    return chosen


def coordinates(independent, vector):
    pivots = {}
    for i, original in enumerate(independent):
        v, tag = original, 1 << i
        for p in sorted(pivots, reverse=True):
            if v >> p & 1:
                v ^= pivots[p][0]
                tag ^= pivots[p][1]
        require(v != 0, "coordinate basis is dependent")
        pivots[v.bit_length() - 1] = (v, tag)
    out = 0
    for p in sorted(pivots, reverse=True):
        if vector >> p & 1:
            vector ^= pivots[p][0]
            out ^= pivots[p][1]
    require(vector == 0, "vector is outside the coordinate span")
    return out


def solve(equations, width):
    """Solve a consistent binary linear system, assigning free coordinates zero."""
    pivots = {}
    for mask, rhs in equations:
        require(0 <= mask < 1 << width and rhs in (0, 1), "invalid equation")
        for p in sorted(pivots, reverse=True):
            if mask >> p & 1:
                mask ^= pivots[p][0]
                rhs ^= pivots[p][1]
        if mask:
            pivots[mask.bit_length() - 1] = (mask, rhs)
        else:
            require(rhs == 0, "inconsistent equations")
    answer = 0
    for p in sorted(pivots):
        mask, rhs = pivots[p]
        answer |= (rhs ^ dot(mask, answer)) << p
    return answer


@dataclass(frozen=True)
class Factor:
    label: str
    x: int
    y: int


def evaluate_rows(rows, vector):
    return sum(dot(row, vector) << i for i, row in enumerate(rows))


def pairing_maps(word, active, roles):
    require(0 <= active <= roles, "invalid active/total dimension")
    for f in word:
        require(0 < f.x < 1 << roles and 0 < f.y < 1 << roles,
                "original factor must be nonzero and within the role space")
    width = roles - active
    ub = basis(f.x >> active for f in word)
    vb = basis(f.y >> active for f in word)
    images, columns = [], []
    for u in ub:
        image = evaluate_rows(vb, u)
        if len(basis([*images, image])) > len(images):
            images.append(image)
            columns.append(u)
    t = len(images)
    u_coordinates = [coordinates(images, evaluate_rows(vb, u)) for u in ub]
    rows = [solve([(u, c >> j & 1) for u, c in zip(ub, u_coordinates)], width)
            for j in range(t)]
    return {"active": active, "roles": roles, "rank": t,
            "column_span_rank": len(ub), "row_span_rank": len(vb),
            "F_rows": rows, "G_columns": columns}


def compress(word, active, roles):
    maps = pairing_maps(word, active, roles)
    rows, columns = maps["F_rows"], maps["G_columns"]
    mask = (1 << active) - 1
    reduced, indices = [], []
    for i, f in enumerate(word):
        x = (f.x & mask) | (evaluate_rows(rows, f.x >> active) << active)
        y = (f.y & mask) | (evaluate_rows(columns, f.y >> active) << active)
        if x and y:
            reduced.append(Factor(f.label, x, y))
            indices.append(i)
    maps["retained_indices"] = indices
    check_compression(word, reduced, maps)
    return reduced, maps


def check_compression(word, reduced, maps):
    h, r, t = maps["active"], maps["roles"], maps["rank"]
    require(0 <= h <= r and 0 <= t <= r - h, "invalid map dimensions")
    rows, columns = maps["F_rows"], maps["G_columns"]
    require(len(rows) == len(columns) == t, "map shape mismatch")
    require(all(0 <= v < 1 << (r - h) for v in [*rows, *columns]), "map outside workspace")
    require(all(dot(row, col) == (i == j)
                for i, row in enumerate(rows) for j, col in enumerate(columns)), "FG is not identity")
    ub = basis(f.x >> h for f in word)
    vb = basis(f.y >> h for f in word)
    require(len(basis(evaluate_rows(vb, u) for u in ub)) == t, "incorrect pairing rank")
    require(maps["column_span_rank"] == len(ub) and maps["row_span_rank"] == len(vb),
            "incorrect span dimensions")
    mask = (1 << h) - 1
    all_reduced = [Factor(f.label, (f.x & mask) | (evaluate_rows(rows, f.x >> h) << h),
                          (f.y & mask) | (evaluate_rows(columns, f.y >> h) << h)) for f in word]
    require(all(dot(a.y, b.x) == dot(ap.y, bp.x)
                for a, ap in zip(word, all_reduced) for b, bp in zip(word, all_reduced)),
            "ordered contraction changed")
    indices = [i for i, f in enumerate(all_reduced) if f.x and f.y]
    require(indices == maps["retained_indices"], "incorrect deleted-factor indices")
    require(reduced == [all_reduced[i] for i in indices], "compressed word mismatch")
    for i, f in enumerate(word):
        if dot(f.x, f.y):
            require(i in indices, "idempotent factor was deleted")


def group_multiply(g, h):
    # Upper triangular coordinates 12,13,14,23,24,34, identity encoded by 0.
    return (g ^ h ^ (((g & 1) * ((h >> 3) & 1)) << 1)
            ^ ((((g & 1) * ((h >> 4) & 1)) ^ (((g >> 1) & 1) * ((h >> 5) & 1))) << 2)
            ^ ((((g >> 3) & 1) * ((h >> 5) & 1)) << 4))


GROUP = [[group_multiply(g, h) for h in range(64)] for g in range(64)]
COEFFICIENTS = {"a": 1 ^ (1 << 1), "b": 1 ^ (1 << 8), "c": 1 ^ (1 << 32)}


def bits(value):
    while value:
        bit = value & -value
        yield bit.bit_length() - 1
        value ^= bit


def ring_multiply(a, b):
    result = 0
    for g in bits(a):
        for h in bits(b):
            result ^= 1 << GROUP[g][h]
    return result


def identity(roles):
    return [[int(i == j) for j in range(roles)] for i in range(roles)]


def word_matrix(word, roles, coefficients=COEFFICIENTS):
    result = identity(roles)
    for factor in word:
        values = []
        for row in result:
            v = 0
            for j in bits(factor.x):
                v ^= row[j]
            values.append(ring_multiply(v, coefficients[factor.label]))
        for i in range(roles):
            for j in bits(factor.y):
                result[i][j] ^= values[i]
    return result


def sandwich(matrix, maps):
    h, r, t = maps["active"], maps["roles"], maps["rank"]
    rows = [1 << i for i in range(h)] + [v << h for v in maps["F_rows"]]
    columns = [1 << i for i in range(h)] + [v << h for v in maps["G_columns"]]
    require(len(matrix) == r and all(len(row) == r for row in matrix), "matrix shape")
    result = [[0] * (h + t) for _ in range(h + t)]
    for i, row in enumerate(rows):
        for j, col in enumerate(columns):
            for a in bits(row):
                for b in bits(col):
                    result[i][j] ^= matrix[a][b]
    return result


def target(roles):
    require(roles >= 2, "two target roles are required")
    matrix = identity(roles)
    matrix[0][0], matrix[1][1] = 1 << 4, 1 << 6
    return matrix


def direct_word():
    return [Factor(g, 1, 1) for g in "abcbabcb"] + [Factor(g, 2, 2) for g in "acbabc"]

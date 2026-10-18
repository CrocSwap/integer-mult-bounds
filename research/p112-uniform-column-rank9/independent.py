#!/usr/bin/env python3
"""Independent frame-coordinate enumeration and modular-minor certificates.

Imports neither the primary checker/model nor predecessor executables.
Gareth Davidson / OpenAI Codex, Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def packed(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def geometry():
    """Enumerate weight-four frame coordinates, then enforce E8 membership."""
    found = {}
    for places in combinations(range(8), 4):
        for signs in product((-1, 1), repeat=4):
            x = [0] * 8
            for p, s in zip(places, signs):
                x[p] = s
            root = tuple(t for j in range(4) for t in
                         (x[2 * j] + x[2 * j + 1], x[2 * j] - x[2 * j + 1]))
            integral = sum(abs(v) == 2 for v in root) == 2 and all(v in (-2, 0, 2) for v in root)
            half = all(v in (-1, 1) for v in root) and sum(v < 0 for v in root) % 2 == 0
            if not (integral or half) or next(v for v in root if v) < 0:
                continue
            found[root] = x
    roots = sorted(found)
    x = [found[r] for r in roots]
    require(len(roots) == 112, "independent P112 inventory")
    matrix = [[(1 + sum(a * b for a, b in zip(s, t)) // 2) % 2 for t in x] for s in x]
    rows = [sum(v << j for j, v in enumerate(row)) for row in matrix]
    frame = []
    for j in range(4):
        for sign in (1, -1):
            f = [0] * 8
            f[2 * j], f[2 * j + 1] = 2, 2 * sign
            frame.append(f)
    return roots, frame, x, rows


def binary_rank(rows):
    """Eliminate by least pivot, independently of the primary highest-pivot code."""
    basis = {}
    for value in rows:
        while value:
            pivot = value & -value
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def rank_mod(rows, width, prime=257):
    basis = {}
    for source in rows:
        row = [v % prime for v in source]
        for p, previous in sorted(basis.items()):
            multiplier = row[p]
            if multiplier:
                row = [(v - multiplier * b) % prime for v, b in zip(row, previous)]
        pivot = next((i for i, v in enumerate(row) if v), None)
        if pivot is not None:
            scale = pow(row[pivot], -1, prime)
            basis[pivot] = [(v * scale) % prime for v in row]
            if len(basis) == width:
                return width
    return len(basis)


def finite():
    roots, frame, x, b = geometry()
    space = {0}
    for row in b:
        if row not in space:
            space |= {v ^ row for v in tuple(space)}
    chars = sorted(space)
    require(len(chars) == 512 and binary_rank(b) == 9, "independent character inventory")
    frame_chars = [sum(int(row[k] == 0) << i for i, row in enumerate(x)) for k in range(8)]
    require(len(set(frame_chars)) == 8 and set(frame_chars) <= space, "frame characters")
    rows_by_char = [[i for i in range(112) if (c >> i) & 1] for c in chars[1:]]
    counts = Counter()
    rank_digest = sha256()
    kernels = []
    tables = []
    for v in range(112):
        expected = {c: [int(j == k) for j in range(8)] for k, c in enumerate(frame_chars)}
        expected[b[v]] = x[v]
        require(len(expected) == 9, "distinct exceptional kernels")
        exceptions = []
        for index, (char, support) in enumerate(zip(chars[1:], rows_by_char), 1):
            rows = [x[i] for i in support if i != v]
            rank = rank_mod(rows, 8)
            if char in expected:
                normal = expected[char]
                require(rank == 7 and any(normal) and
                        all(sum(a * c for a, c in zip(row, normal)) == 0 for row in rows),
                        "independent rational-null/modular-minor certificate")
                exceptions.append(index)
            else:
                require(rank == 8, "independent full-rank minor")
            counts[rank] += 1
            rank_digest.update(f"{v},{index},{rank}\n".encode())
        kernels.append(exceptions)
        supports = [[i for i in range(112) if i != v and x[i][k]] for k in range(8)]
        supports += [[i for i in range(112) if not ((b[v] >> i) & 1)], [v], list(range(112))]
        require([binary_rank(b[i] for i in group) for group in supports] == [8] * 9 + [1, 9],
                "independent actual support spans")
        table = []
        for left in supports:
            line = []
            for right in supports:
                projected = [sum(((b[i] >> j) & 1) << k for k, j in enumerate(right)) for i in left]
                line.append(binary_rank(projected))
            table.append(line)
        tables.append(table)
    unpunctured = Counter()
    for char, support in zip(chars[1:], rows_by_char):
        rank = rank_mod([x[i] for i in support], 8)
        require(rank == (7 if char in frame_chars else 8), "unpunctured minor classification")
        if char in frame_chars:
            k = frame_chars.index(char)
            require(all(x[i][k] == 0 for i in support), "unpunctured exact null vector")
        unpunctured[rank] += 1
    return {"geometry_sha256": sha256(packed([roots, frame, x, b]).encode()).hexdigest(),
            "characters_sha256": sha256(packed(chars).encode()).hexdigest(),
            "puncture_character_cases": 112 * 511,
            "complex_rank_counts": {str(k): v for k, v in sorted(counts.items())},
            "rank_table_sha256": rank_digest.hexdigest(), "exceptional_character_indices": kernels,
            "pairing_table_entries": 112 * 121,
            "pairing_tables_sha256": sha256(packed(tables).encode()).hexdigest(),
            "unpunctured_rank_counts": {str(k): v for k, v in sorted(unpunctured.items())}}


def integer_boundaries():
    _, _, x, b = geometry()
    results = []
    for v in (0, 42, 111):
        s = x[v]
        p = next(j for j, value in enumerate(s) if value)
        w = [sum(a * c for a, c in zip(row, s)) - 4 * int(i == v) for i, row in enumerate(x)]
        # Integer dual basis with its p-th right normal equal to s.
        rb = [[int(i == j) for j in range(8)] for i in range(8)]
        for i in range(8):
            rb[i][p] = s[i]
        la = [[int(i == j) for j in range(8)] for i in range(8)]
        la[p] = [-s[j] * s[p] if j != p else s[p] for j in range(8)]
        left = [[sum(row[k] * la[k][j] for k in range(8)) for j in range(8)] + [int(i == v)]
                for i, row in enumerate(x)]
        right = [[sum(row[k] * rb[k][j] for k in range(8)) -
                  int(i == v) * sum(rb[k][j] * s[k] for k in range(8)) for j in range(8)] + [4 * int(i == v)]
                 for i, row in enumerate(x)]
        for i in range(112):
            for j in range(112):
                actual = sum(a * c for a, c in zip(left[i], right[j]))
                expected = sum(a * c for a, c in zip(x[i], x[j])) - w[i] * int(j == v)
                require(actual == expected, "independent compensated completion")
        ranks = []
        for k in range(9):
            cols = [j for j in range(112) if right[j][k]]
            rows = [sum(((b[i] >> j) & 1) << q for q, j in enumerate(cols))
                    for i in range(112) if left[i][k]]
            ranks.append(binary_rank(rows))
        require(sorted(ranks) == [1, 7] + [8] * 7, "independent 63+1 compensation bill")
        require(left[v][-1] * right[v][-1] == 4 and (b[v] >> v) & 1,
                "omitted compensation must break a constrained diagonal")
        results.append({"v": v, "ranks": ranks, "entries": 112 * 112, "omitted_diagonal_error": 4})
    return results


if __name__ == "__main__":
    result = finite()
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    require(packed(result) == packed(expected["finite"]), "independent finite receipt mismatch")
    boundaries = integer_boundaries()
    require(packed(boundaries) == packed(expected["independent_integer_boundaries"]), "independent boundary receipt")
    print("PASS_UNIFORM_COLUMN_INDEPENDENT", "hyperplanes=57232", "integer_entries=37632")

"""Check the literal witness using lattice membership and modular rank minors.

This file does not import the primary verifier or predecessor geometry code.
Nonzero modular minors prove rational lower bounds. Five explicit inclusion
relations give the matching rational upper bound, not modular zero tests.
"""

import json
from fractions import Fraction
from itertools import product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
PRIME = 101
# The exact simple system used for labels in the pinned predecessor source.
SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def lattice_points():
    roots = []
    for row in product(range(-2, 3), repeat=8):
        if sum(x * x for x in row) != 8:
            continue
        if len({x % 2 for x in row}) != 1 or sum(row) % 4:
            continue
        if next(x for x in row if x) > 0:
            roots.append(row)
    frame = set()
    for j in range(4):
        for sign in (-1, 1):
            row = [0] * 8
            row[2 * j], row[2 * j + 1] = 2, 2 * sign
            frame.add(tuple(row))
    ensure(len(roots) == 120 and len(frame) == 8, "lattice inventory")
    points = tuple(row for row in roots if row not in frame)
    ensure(len(points) == 112 and points == tuple(sorted(points)), "P112 order")
    return points


def modular_rank(rows):
    ensure(1 <= len(rows) <= 19, "modular row bound")
    width = len(rows[0])
    ensure(
        1 <= width <= 112 and all(len(row) == width for row in rows), "modular shape"
    )
    matrix = [[x % PRIME for x in row] for row in rows]
    rank = 0
    for col in range(width):
        selected = next((i for i in range(rank, len(rows)) if matrix[i][col]), None)
        if selected is None:
            continue
        matrix[rank], matrix[selected] = matrix[selected], matrix[rank]
        inverse = pow(matrix[rank][col], -1, PRIME)
        matrix[rank] = [(x * inverse) % PRIME for x in matrix[rank]]
        for i in range(rank + 1, len(rows)):
            scale = matrix[i][col]
            matrix[i] = [
                (x - scale * y) % PRIME
                for x, y in zip(matrix[i], matrix[rank], strict=True)
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def decode(witness):
    cuts = witness["cuts"]
    ensure(len(cuts) == len(set(cuts)) == 31, "31 distinct cuts")
    ensure(all(type(x) is int and 0 <= x < 112 for x in cuts), "cut range")
    directions = witness["directions_doubled"]
    ensure(len(directions) == 5 and all(len(h) == 8 for h in directions), "directions")
    ensure(
        all(type(x) is int and abs(x) <= 2 for h in directions for x in h),
        "direction range",
    )
    sparse = witness["endpoints_sparse"]
    ensure(len(sparse) == 6, "six endpoints")
    endpoints = []
    for entries in sparse:
        ensure(
            len(entries) == 20 and all(len(row) == 2 for row in entries),
            "twenty entries",
        )
        ensure(
            all(
                type(i) is int and 0 <= i < 112 and type(x) is int and 0 < abs(x) <= 2
                for i, x in entries
            ),
            "sparse bounds",
        )
        mapping = dict(entries)
        ensure(len(mapping) == 20, "distinct endpoint coordinates")
        endpoints.append(tuple(mapping.get(i, 0) for i in range(112)))
    return set(cuts), directions, endpoints


def binary_labels(points):
    matrix = [
        [Fraction(SIMPLE[j][i]) for j in range(8)]
        + [Fraction(int(i == j)) for j in range(8)]
        for i in range(8)
    ]
    for col in range(8):
        pivot = next((i for i in range(col, 8) if matrix[i][col]), None)
        ensure(pivot is not None, "simple-system invertibility")
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        scale = matrix[col][col]
        matrix[col] = [x / scale for x in matrix[col]]
        for i in range(8):
            if i != col:
                scale = matrix[i][col]
                matrix[i] = [
                    x - scale * y for x, y in zip(matrix[i], matrix[col], strict=True)
                ]
    labels = []
    for point in points:
        coordinates = [sum(row[8 + j] * point[j] for j in range(8)) for row in matrix]
        ensure(all(x.denominator == 1 for x in coordinates), "simple-root integrality")
        labels.append(
            1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(coordinates))
        )
    ensure(len(set(labels)) == 112, "binary label count")
    return labels


def binary_support_rank(row, labels):
    basis = [0] * 9
    for i, x in enumerate(row):
        value = labels[i] if x else 0
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return sum(x != 0 for x in basis)


def check(witness):
    points = lattice_points()
    cuts, directions, endpoints = decode(witness)
    pairings = [
        [sum(r[j] * h[j] for j in range(8)) for r in points] for h in directions
    ]
    ensure(all(x % 4 == 0 for row in pairings for x in row), "integer codewords")
    codewords = [[x // 4 for x in row] for row in pairings]
    small = [
        tuple(x if i in cuts else 0 for i, x in enumerate(row)) for row in codewords
    ]
    ensure(
        set().union(*({i for i, x in enumerate(a) if x} for a in small)) == cuts,
        "actual small union",
    )
    ensure(all(sum(x != 0 for x in q) == 20 for q in endpoints), "support twenty")
    ensure(all(q[t] == 0 for q in endpoints for t in cuts), "endpoints avoid cuts")
    ensure(
        all(
            codewords[i][t] == endpoints[i + 1][t] - endpoints[0][t] + small[i][t]
            for i in range(5)
            for t in range(112)
        ),
        "five exact inclusion relations",
    )
    code = [tuple(r[j] for r in points) for j in range(8)]
    pieces = small + endpoints
    ranks = {
        "pieces": modular_rank(pieces),
        "code": modular_rank(code),
        "combined": modular_rank(pieces + code),
        "directions": modular_rank(directions),
    }
    ensure(
        ranks == {"pieces": 11, "code": 8, "combined": 14, "directions": 5},
        "nonzero modular minors",
    )
    # The five independent codewords lie in both spans. Thus dim(T+C)<=11+8-5.
    ensure(
        ranks["combined"] == ranks["pieces"] + ranks["code"] - ranks["directions"],
        "matching rational lower/upper bounds",
    )
    labels = binary_labels(points)
    return {
        "prime": PRIME,
        "modular_rank_lower_bounds": ranks,
        "rational_combined_upper_bound": 14,
        "intersection_dimension": 5,
        "errors": 0,
        "small_support_label_ranks": [
            binary_support_rank(row, labels) for row in small
        ],
        "endpoint_support_label_ranks": [
            binary_support_rank(row, labels) for row in endpoints
        ],
    }


def main():
    path = PACKAGE / "WITNESS.json"
    ensure(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 100_000,
        "witness file",
    )
    result = check(json.loads(path.read_bytes()))
    receipt = PACKAGE / "INDEPENDENT.json"
    ensure(
        receipt.is_file()
        and not receipt.is_symlink()
        and receipt.stat().st_size <= 100_000,
        "independent receipt file",
    )
    ensure(result == json.loads(receipt.read_bytes()), "independent receipt differs")
    print(json.dumps(result, sort_keys=True))
    print(
        "PASS_INDEPENDENT_SUPPORT31 lattice=120 punctures=8 "
        "nonzero_modular_minors=101 exact_relations=5"
    )


if __name__ == "__main__":
    main()

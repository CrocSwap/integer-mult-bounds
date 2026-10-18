"""Check a rational counterexample to P112 shortening at common support31.

Root coordinates follow Nick Petalas/PR3188 and its retained E8/P112 lineage.
New witness and checks are Apache-2.0. See SOURCES.json and PROOF.md.
"""

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "missing or linked JSON")
    require(path.stat().st_size <= 100_000, "oversized JSON")
    return json.loads(path.read_bytes())


def bind_sources():
    sources = read_json(PACKAGE / "SOURCES.json")
    inputs = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(inputs) == 1, "source inventory")
    row = inputs[0]
    require(
        row["path"] == "research/p112-six-vertex-budget/vendor/geometry.py",
        "source path",
    )
    path = REPO / row["path"]
    require(path.is_file() and not path.is_symlink(), "missing or linked source")
    require(path.stat().st_size <= 100_000, "oversized source")
    require(
        hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "source hash"
    )


def dot(a, b):
    return sum(x * y for x, y in zip(a, b, strict=True))


def canonical(row):
    return max(tuple(row), tuple(-x for x in row))


def geometry():
    roots, frame = set(), set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = tuple(2 if k == i else sign if k == j else 0 for k in range(8))
            roots.add(row)
            if j == i + 1 and i % 2 == 0:
                frame.add(row)
    roots.update(
        canonical(row) for row in product((-1, 1), repeat=8) if row.count(-1) % 2 == 0
    )
    require(len(roots) == 120 and len(frame) == 8, "E8/frame inventory")
    points = tuple(sorted(roots - frame))
    require(len(points) == 112, "P112 count")
    require(
        all(
            sum(r[i] * r[j] for r in points) == 112 * int(i == j)
            for i in range(8)
            for j in range(8)
        ),
        "P112 evaluation injectivity",
    )
    return points


def rank_pivots(rows):
    require(1 <= len(rows) <= 19, "rank row bound")
    width = len(rows[0])
    require(1 <= width <= 112 and all(len(row) == width for row in rows), "rank shape")
    matrix = [[Fraction(x) for x in row] for row in rows]
    pivots = []
    for col in range(width):
        rank = len(pivots)
        pivot = next((i for i in range(rank, len(rows)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][col]
        matrix[rank] = [x / scale for x in matrix[rank]]
        for i in range(rank + 1, len(rows)):
            scale = matrix[i][col]
            matrix[i] = [
                x - scale * y for x, y in zip(matrix[i], matrix[rank], strict=True)
            ]
        pivots.append(col)
        if len(pivots) == len(rows):
            break
    return tuple(pivots)


def parse_witness(witness):
    require(
        set(witness) == {"directions_doubled", "cuts", "endpoints_sparse"},
        "witness fields",
    )
    directions, cuts, sparse = (
        witness["directions_doubled"],
        witness["cuts"],
        witness["endpoints_sparse"],
    )
    require(
        len(directions) == 5 and all(len(row) == 8 for row in directions),
        "directions shape",
    )
    require(
        all(type(x) is int and -2 <= x <= 2 for row in directions for x in row),
        "direction entries",
    )
    require(len(cuts) == 31 and cuts == sorted(set(cuts)), "cut inventory")
    require(all(type(i) is int and 0 <= i < 112 for i in cuts), "cut indices")
    require(len(sparse) == 6, "endpoint inventory")
    endpoints = []
    for entries in sparse:
        require(
            len(entries) == 20 and all(len(pair) == 2 for pair in entries),
            "endpoint shape",
        )
        require(
            all(
                type(i) is int and 0 <= i < 112 and type(x) is int and 0 < abs(x) <= 2
                for i, x in entries
            ),
            "endpoint entries",
        )
        require(len({i for i, _ in entries}) == 20, "duplicate endpoint coordinate")
        row = [0] * 112
        for i, x in entries:
            row[i] = x
        endpoints.append(tuple(row))
    return tuple(map(tuple, directions)), frozenset(cuts), tuple(endpoints)


def construct(points, directions, cuts):
    require(
        tuple(tuple(dot(a, b) for b in directions) for a in directions)
        == tuple(tuple(4 + 4 * int(i == j) for j in range(5)) for i in range(5)),
        "A5 Gram matrix",
    )
    raw = tuple(tuple(dot(r, h) for r in points) for h in directions)
    require(all(x % 4 == 0 for row in raw for x in row), "nonintegral evaluation")
    codewords = tuple(tuple(x // 4 for x in row) for row in raw)
    small = tuple(
        tuple(x if t in cuts else 0 for t, x in enumerate(row)) for row in codewords
    )
    values = tuple((0, *(row[t] for row in codewords)) for t in range(112))
    shifts = tuple(
        min(Counter(row), key=lambda x: (-row.count(x), x)) for row in values
    )
    endpoints = tuple(
        tuple(0 if t in cuts else values[t][i] - shifts[t] for t in range(112))
        for i in range(6)
    )
    return codewords, small, endpoints, values


def support(row):
    return frozenset(i for i, x in enumerate(row) if x)


def check_witness(witness):
    points = geometry()
    directions, cuts, endpoints = parse_witness(witness)
    codewords, small, generated, values = construct(points, directions, cuts)
    require(endpoints == generated, "literal endpoint reconstruction")
    require([len(support(q)) for q in endpoints] == [20] * 6, "endpoint support")
    require(
        frozenset().union(*(support(a) for a in small)) == cuts, "small-support union"
    )
    require(all(not support(q) & cuts for q in endpoints), "endpoint/cut disjointness")
    require(
        all(
            codewords[i][t] == endpoints[i + 1][t] - endpoints[0][t] + small[i][t]
            for i in range(5)
            for t in range(112)
        ),
        "codeword inclusion identity",
    )
    code = tuple(tuple(row[i] for row in points) for i in range(8))
    pieces = small + endpoints
    matrices = {
        "small": small,
        "endpoints": endpoints,
        "pieces": pieces,
        "code": code,
        "combined": pieces + code,
        "directions": directions,
    }
    pivots = {name: rank_pivots(rows) for name, rows in matrices.items()}
    ranks = {name: len(columns) for name, columns in pivots.items()}
    require(
        ranks
        == {
            "small": 5,
            "endpoints": 6,
            "pieces": 11,
            "code": 8,
            "combined": 14,
            "directions": 5,
        },
        "rank certificate",
    )
    costs = tuple(6 - max(Counter(row).values()) for row in values)
    return {
        "errors": 0,
        "field": "every characteristic-zero field",
        "small_union": len(cuts),
        "small_supports": [len(support(a)) for a in small],
        "endpoint_supports": [len(support(q)) for q in endpoints],
        "ranks": ranks,
        "pivot_columns": pivots,
        "intersection_dimension": ranks["pieces"] + ranks["code"] - ranks["combined"],
        "cut_cost_histogram": dict(sorted(Counter(costs[t] for t in cuts).items())),
        "retained_cost_histogram": dict(
            sorted(Counter(costs[t] for t in range(112) if t not in cuts).items())
        ),
        "total_endpoint_support": sum(len(support(q)) for q in endpoints),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external result JSON")
    args = parser.parse_args()
    bind_sources()
    result = json.loads(json.dumps(check_witness(read_json(PACKAGE / "WITNESS.json"))))
    if args.output:
        require(not args.output.resolve().is_relative_to(REPO), "external output only")
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == read_json(PACKAGE / "RESULT.json"), "receipt differs")
    print(
        "PASS_P112_SUPPORT31_SHARPNESS pieces=11 small_union=31 "
        "endpoints=20x6 intersection=5 errors=0"
    )


if __name__ == "__main__":
    main()

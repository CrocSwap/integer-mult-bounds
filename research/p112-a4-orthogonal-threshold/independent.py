"""Separate lattice, full-frame and modular-minor checks of the A4 result.

No predecessor module, primary verifier or primary rank routine is executed.
Only the literal witness and the independent committed receipt are read.
"""

import json
from collections import Counter
from itertools import product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def lattice_roots():
    found = set()
    for row in product(range(-2, 3), repeat=8):
        if sum(x * x for x in row) != 8 or sum(row) % 4:
            continue
        if all(x % 2 == row[0] % 2 for x in row):
            found.add(max(row, tuple(-x for x in row)))
    demand(len(found) == 120, "lattice root inventory")
    return tuple(sorted(found))


def rank_mod(rows, prime=101):
    demand(1 <= len(rows) <= 17 and 1 <= len(rows[0]) <= 112, "modular shape")
    demand(prime == 101 and all(len(r) == len(rows[0]) for r in rows), "modular domain")
    demand(
        all(type(x) is int and abs(x) <= 128 for row in rows for x in row),
        "modular entry bound",
    )
    matrix = [[x % prime for x in row] for row in rows]
    count = 0
    for col in range(len(matrix[0])):
        for pivot in range(count, len(matrix)):
            if matrix[pivot][col]:
                break
        else:
            continue
        matrix[count], matrix[pivot] = matrix[pivot], matrix[count]
        inverse = pow(matrix[count][col], prime - 2, prime)
        matrix[count] = [x * inverse % prime for x in matrix[count]]
        for i in range(count + 1, len(matrix)):
            factor = matrix[i][col]
            matrix[i] = [
                (x - factor * y) % prime
                for x, y in zip(matrix[i], matrix[count], strict=True)
            ]
        count += 1
        if count == len(matrix):
            break
    return count


def frame_census(roots):
    adjacent = [
        sum(
            1 << j
            for j in range(i + 1, 120)
            if sum(a * b for a, b in zip(roots[i], roots[j], strict=True)) == 0
        )
        for i in range(120)
    ]
    values = [(0, *((r[0] + r[j]) // 2 for j in range(1, 5))) for r in roots]
    demand(
        all((r[0] + r[j]) % 2 == 0 for r in roots for j in range(1, 5)),
        "independent A4 evaluation integrality",
    )
    costs = [5 - max(v.count(x) for x in v) for v in values]
    stack, histogram, states = [((), (1 << 120) - 1)], Counter(), 0
    for _ in range(1_000_000):
        if not stack:
            break
        prefix, candidates = stack.pop()
        states += 1
        if len(prefix) == 8:
            demand(
                sum(
                    5 * sum(x * x for x in values[i]) - sum(values[i]) ** 2
                    for i in prefix
                )
                == 40,
                "independent frame Parseval",
            )
            histogram[sum(costs[i] for i in prefix)] += 1
        else:
            for j in range(120):
                if candidates >> j & 1:
                    stack.append((prefix + (j,), candidates & adjacent[j]))
        demand(len(stack) <= 1_000_000, "frame state capacity")
    demand(not stack and states == 352876, "frame enumeration incomplete")
    demand(histogram == {10: 525, 11: 600, 12: 600, 13: 300}, "frame-cost histogram")
    return {
        "frames": sum(histogram.values()),
        "states": states,
        "frame_cost_histogram": dict(sorted(histogram.items())),
        "spectrum": dict(sorted(Counter(costs).items())),
    }


def literal_witness(roots):
    path = PACKAGE / "WITNESS.json"
    demand(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 100_000,
        "independent witness file",
    )
    raw = json.loads(path.read_bytes())
    directions, cuts = raw["directions_doubled"], set(raw["cuts"])
    demand(len(directions) == 4 and len(cuts) == 29, "independent witness dimensions")
    demand(
        all(
            len(r) == 8 and all(type(x) is int and -2 <= x <= 2 for x in r)
            for r in directions
        ),
        "independent directions",
    )
    frame = {
        r
        for r in roots
        if sum(x != 0 for x in r) == 2
        and any(r[2 * j] == 2 and abs(r[2 * j + 1]) == 2 for j in range(4))
    }
    demand(len(frame) == 8, "independent fixed frame")
    points = tuple(r for r in roots if r not in frame)
    endpoints = []
    for entries in raw["endpoints_sparse"]:
        row = [0] * 112
        demand(
            1 <= len(entries) <= 20 and len({i for i, _ in entries}) == len(entries),
            "independent endpoint cardinality",
        )
        for i, x in entries:
            demand(
                type(i) is int and 0 <= i < 112 and type(x) is int and 0 < abs(x) <= 2,
                "independent sparse entry",
            )
            row[i] = x
        endpoints.append(tuple(row))
    demand(len(endpoints) == 5, "independent endpoint count")
    return witness_relations(points, directions, cuts, tuple(endpoints))


def witness_relations(points, directions, cuts, endpoints):
    raw = [
        tuple(sum(x * y for x, y in zip(r, h, strict=True)) for r in points)
        for h in directions
    ]
    demand(all(x % 4 == 0 for row in raw for x in row), "independent code integrality")
    codewords = [tuple(x // 4 for x in row) for row in raw]
    small = [
        tuple(
            codewords[i][t] - endpoints[i + 1][t] + endpoints[0][t] for t in range(112)
        )
        for i in range(4)
    ]
    demand(
        {t for row in small for t, x in enumerate(row) if x} == cuts,
        "literal inclusion relations and common union",
    )
    demand(
        all(not any(q[t] for t in cuts) for q in endpoints), "endpoint/cut separation"
    )
    code = [tuple(r[i] for r in points) for i in range(8)]
    pieces = small + list(endpoints)
    ranks = [
        rank_mod(rows)
        for rows in (small, endpoints, pieces, code, pieces + code, codewords)
    ]
    demand(ranks == [4, 5, 9, 8, 13, 4], "independent nonzero-minor lower bounds")
    sizes = [sum(x != 0 for x in row) for row in endpoints]
    demand(sizes == [20, 19, 20, 20, 20], "independent support counts")
    # Exact relations give the rational upper bound 9+8-4=13 on the sum.
    return {
        "modulus": 101,
        "rank_lower_bounds": ranks,
        "endpoint_supports": sizes,
        "exact_independent_relations": 4,
        "rational_sum_rank_upper_bound": 13,
        "intersection_dimension": 4,
        "common_support": len(cuts),
    }


def build():
    roots = lattice_roots()
    return json.loads(
        json.dumps(
            {
                "errors": 0,
                "lattice_candidates": 5**8,
                "frames": frame_census(roots),
                "witness": literal_witness(roots),
            }
        )
    )


def main():
    actual = build()
    path = PACKAGE / "INDEPENDENT.json"
    demand(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 100_000,
        "independent receipt file",
    )
    demand(actual == json.loads(path.read_bytes()), "independent receipt differs")
    print("PASS_A4_INDEPENDENT lattice=390625 frames=2025 intersection=4 errors=0")


if __name__ == "__main__":
    main()

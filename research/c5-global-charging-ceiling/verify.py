#!/usr/bin/env python3
"""Exact finite premises for the C5 charging-method ceiling. Apache-2.0."""

import argparse
import gzip
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = "research/c5-dyadic-decoder-gate/inputs/"
PINS = {
    "DATA-PHASES.json.gz": (
        "682092a4c656e0be4bdaa419783440772a80ae875cca4845aea2067927b560f6"
    ),
    "MATCHING.json": "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1",
}
BASE = "463113d675af7410ac91d53a4fed51ec6494eb9a"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_read(path, limit):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    need(len(raw) <= limit, "file capacity exceeded")
    return raw


def load_planes(root):
    manifest = json.loads(bounded_read(HERE / "SOURCES.json", 16_384))
    need(manifest["base_commit"] == BASE, "base provenance changed")
    rows = manifest["files"]
    need(len(rows) == 4, "source inventory changed")
    live = {r["path"]: r["sha256"] for r in rows if r["usage"] == "input"}
    need(live == {INPUTS + n: h for n, h in PINS.items()}, "live pins changed")
    parsed = {}
    for name, pin in PINS.items():
        raw = bounded_read(root / INPUTS / name, 32_768)
        need(hashlib.sha256(raw).hexdigest() == pin, "source authentication: " + name)
        if name.endswith(".gz"):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(1_048_577)
            need(len(raw) <= 1_048_576, "payload capacity exceeded")
        parsed[name] = json.loads(raw)
    recipes = parsed["DATA-PHASES.json.gz"]["recipes"]
    matching = parsed["MATCHING.json"]["matching"]
    need(len(recipes) == 112 and len(matching) == 56, "physical dimensions")
    labels = {r["port"]: r["q"] for r in recipes}
    need(sorted(labels) == list(range(112)), "port partition")
    need(all(type(v) is int and 0 < v < 512 for v in labels.values()), "label domain")
    need(all(len(p) == 2 for p in matching), "complete planes")
    need(sorted(p for pair in matching for p in pair) == list(range(112)), "matching")
    planes = [tuple(labels[p] for p in pair) for pair in matching]
    need(
        all([[dot(x, y) for y in p] for x in p] == [[1, 0], [0, 1]] for p in planes),
        "nondegenerate orthonormal planes",
    )
    return planes


def dot(x, y):
    return (x & y).bit_count() & 1


def binary_rank(rows, width):
    need(0 <= width <= 112 and len(rows) <= 112, "matrix capacity")
    pivots = [0] * width
    for row in rows:
        need(type(row) is int and 0 <= row < 1 << width, "binary row domain")
        for bit in range(width - 1, -1, -1):
            if row >> bit & 1:
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return sum(bool(p) for p in pivots)


def tariff(planes, left, right):
    need(len(planes) == 56 and len(left) <= 56 and len(right) <= 56, "support capacity")
    need(all(type(i) is int and 0 <= i < 56 for i in (*left, *right)), "support domain")
    xs = [x for i in left for x in planes[i]]
    ys = [y for i in right for y in planes[i]]
    rows = [sum(dot(x, y) << j for j, y in enumerate(ys)) for x in xs]
    return binary_rank(rows, len(ys))


def cycle_census(planes):
    adjacent = [set() for _ in planes]
    for i, j in combinations(range(56), 2):
        if all(dot(x, y) == 0 for x in planes[i] for y in planes[j]):
            adjacent[i].add(j)
            adjacent[j].add(i)
    paths = [(i,) for i in range(56)]
    for _ in range(4):
        paths = [
            p + (j,)
            for p in paths
            for j in sorted(adjacent[p[-1]])
            if j > p[0] and j not in p and not any(j in adjacent[k] for k in p[1:-1])
        ]
        need(len(paths) <= 200_000, "cycle path capacity")
    cycles = []
    for p in paths:
        if (
            p[0] in adjacent[p[-1]]
            and p[1] < p[-1]
            and all(sum(j in adjacent[i] for j in p) == 2 for i in p)
        ):
            cycles.append(list(p))
    cycles.sort()
    need(
        len(cycles) == 23 and len({tuple(sorted(p)) for p in cycles}) == 23, "C5 census"
    )
    return cycles


def bound(weights, local_ranks, global_rank):
    need(len(weights) == len(local_ranks) == 23, "weight dimension")
    need(
        all(isinstance(w, (int, Fraction)) and w >= 0 for w in weights),
        "nonnegative weights",
    )
    total = sum(weights)
    need(
        total > 0 and global_rank > 0 and min(local_ranks) > 0, "positive normalization"
    )
    return Fraction(
        20 * global_rank * total,
        sum(w * d for w, d in zip(weights, local_ranks, strict=True)),
    )


def cancelling_pair_control(planes, last_weight=-1):
    # Identity plus J minus J is a strict fit containing full-support terms.
    terms = [(1, (i,), (i,)) for i in range(112)]
    terms.extend(
        [
            (1, tuple(range(112)), tuple(range(112))),
            (last_weight, tuple(range(112)), tuple(range(112))),
        ]
    )
    matrix = [[0] * 112 for _ in range(112)]
    for weight, sources, targets in terms:
        for i in sources:
            for j in targets:
                matrix[i][j] += weight
    need(
        all(matrix[i][j] == int(i == j) for i in range(112) for j in range(112)),
        "signed cancellation endpoint",
    )
    singleton = [tariff(planes, [i], [i]) for i in range(56)]
    full = tariff(planes, list(range(56)), list(range(56)))
    need(singleton == [2] * 56, "identity term full-plane tariff")
    return {
        "terms": 114,
        "identity_cost": 2 * sum(singleton),
        "full_support_term_costs": [full, full],
        "total_cost": 2 * sum(singleton) + 2 * full,
    }


def compute(root):
    planes = load_planes(root)
    cycles = cycle_census(planes)
    ranks = [tariff(planes, c, c) for c in cycles]
    full = tariff(planes, list(range(56)), list(range(56)))
    need(full == 9 and Counter(ranks) == {7: 4, 8: 6, 9: 13}, "physical rank spectrum")
    weights = [int(r == 7) for r in ranks]
    best_test = bound(weights, ranks, full)
    uniform = bound([1] * 23, ranks, full)
    need(best_test == Fraction(180, 7) < 26, "universal real ceiling")
    need(uniform == Fraction(4140, 193) < 22, "uniform real ceiling")
    return {
        "schema_version": 1,
        "status": "PROOF_METHOD_OBSTRUCTION_NOT_A_DECODER_BOUND",
        "cycles": cycles,
        "full_support_local_ranks": ranks,
        "full_support_global_rank": full,
        "local_rank_sum": sum(ranks),
        "rank_histogram": {str(k): v for k, v in sorted(Counter(ranks).items())},
        "conditional_local_rhs": 20,
        "all_weights_ceiling": str(best_test),
        "uniform_weights_ceiling": str(uniform),
        "largest_integer_floor_not_excluded": 26,
        "uniform_largest_integer_floor_not_excluded": 22,
        "signed_fit_control": cancelling_pair_control(planes),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=HERE.parents[1])
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    result = compute(args.root)
    if args.emit_to:
        with args.emit_to.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = json.loads(bounded_read(HERE / "RESULT.json", 16_384))
        need(result == expected, "stored receipt differs")
    print(
        "PASS_C5_GLOBAL_CHARGING_CEILING cycles=23 ranks=7:4,8:6,9:13 "
        "ceiling=180/7 no_new_kappa"
    )


if __name__ == "__main__":
    main()

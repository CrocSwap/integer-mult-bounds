#!/usr/bin/env python3
"""Separate dense-rank and five-subset reconstruction. Apache-2.0."""

import gzip
import hashlib
import io
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "research/c5-dyadic-decoder-gate/inputs"
HASHES = (
    (
        "MATCHING.json",
        "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1",
    ),
    (
        "DATA-PHASES.json.gz",
        "682092a4c656e0be4bdaa419783440772a80ae875cca4845aea2067927b560f6",
    ),
)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read_geometry():
    data = {}
    for name, digest in HASHES:
        with (SOURCE / name).open("rb") as stream:
            raw = stream.read(32_769)
        require(len(raw) <= 32_768, "input capacity")
        require(
            hashlib.sha256(raw).hexdigest() == digest,
            "independent source authentication",
        )
        if name.endswith(".gz"):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(1_048_577)
            require(len(raw) <= 1_048_576, "decompressed capacity")
        data[name] = json.loads(raw)
    match = data["MATCHING.json"]["matching"]
    recipes = data["DATA-PHASES.json.gz"]["recipes"]
    require(len(match) == 56 and len(recipes) == 112, "geometry cardinality")
    labels = {entry["port"]: entry["q"] for entry in recipes}
    require(sorted(labels) == list(range(112)), "independent port inventory")
    require(
        sorted(i for pair in match for i in pair) == list(range(112)),
        "independent matching",
    )
    return [
        [[int(labels[i] >> k & 1) for k in range(9)] for i in pair] for pair in match
    ]


def inner(x, y):
    return sum(a * b for a, b in zip(x, y, strict=True)) % 2


def dense_rank(matrix):
    require(len(matrix) <= 112 and all(len(r) <= 112 for r in matrix), "dense capacity")
    work = [row[:] for row in matrix]
    height = len(work)
    width = len(work[0]) if height else 0
    require(all(len(r) == width for r in work), "rectangular matrix")
    lead = 0
    for column in range(width):
        pivot = next((i for i in range(lead, height) if work[i][column]), None)
        if pivot is not None:
            work[lead], work[pivot] = work[pivot], work[lead]
            for i in range(lead + 1, height):
                if work[i][column]:
                    work[i] = [
                        (a + b) % 2 for a, b in zip(work[i], work[lead], strict=True)
                    ]
            lead += 1
    return lead


def price(planes, indices):
    vectors = [v for i in indices for v in planes[i]]
    return dense_rank([[inner(x, y) for y in vectors] for x in vectors])


def find_cycles(planes):
    graph = [
        [
            i != j and all(inner(x, y) == 0 for x in p for y in q)
            for j, q in enumerate(planes)
        ]
        for i, p in enumerate(planes)
    ]
    neighbors = [sum(int(v) << j for j, v in enumerate(row)) for row in graph]
    cycles = []
    examined = 0
    for group in combinations(range(56), 5):
        examined += 1
        mask = sum(1 << i for i in group)
        if all((neighbors[i] & mask).bit_count() == 2 for i in group):
            order = [group[0]]
            for _ in range(4):
                choices = [i for i in group if i not in order and graph[order[-1]][i]]
                require(bool(choices), "C5 traversal")
                order.append(min(choices))
            require(graph[order[-1]][order[0]], "cycle closure")
            cycles.append(order)
    require(
        examined == 3_819_816 and len(cycles) == 23, "independent exhaustive census"
    )
    return sorted(cycles)


def check_signed_fit():
    left = [[int(i == j) for j in range(112)] + [1, 1] for i in range(112)]
    right = [[int(i == j) for j in range(112)] + [1, -1] for i in range(112)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            require(
                sum(x * y for x, y in zip(a, b, strict=True)) == int(i == j),
                "actual scalar factorization",
            )
    require(all(row[-2:] == [1, 1] for row in left), "full source support")
    require(all(row[-2:] == [1, -1] for row in right), "full target support")


def main():
    planes = read_geometry()
    require(
        all([[inner(x, y) for y in p] for x in p] == [[1, 0], [0, 1]] for p in planes),
        "independent orthonormality",
    )
    cycles = find_cycles(planes)
    ranks = [price(planes, c) for c in cycles]
    global_rank = price(planes, list(range(56)))
    require(Counter(ranks) == {7: 4, 8: 6, 9: 13} and global_rank == 9, "rank census")
    require(sum(ranks) == 193 and 20 * global_rank < 26 * min(ranks), "method ceiling")
    require(23 * 20 * global_rank < 22 * sum(ranks), "uniform ceiling")
    require(25 * 7 < 180 < 26 * 7 and 21 * 193 < 4140 < 22 * 193, "integer seams")
    check_signed_fit()
    require(all(price(planes, [i]) == 2 for i in range(56)), "identity tariff")
    with (HERE / "RESULT.json").open("rb") as stream:
        raw = stream.read(16_385)
    require(len(raw) <= 16_384, "receipt capacity")
    expected = json.loads(raw)
    require(expected["cycles"] == cycles, "stored physical cycles")
    require(expected["full_support_local_ranks"] == ranks, "stored local ranks")
    require(expected["full_support_global_rank"] == global_rank, "stored global rank")
    require(expected["all_weights_ceiling"] == "180/7", "stored universal ceiling")
    require(expected["uniform_weights_ceiling"] == "4140/193", "stored uniform ceiling")
    require(
        expected["signed_fit_control"]
        == {
            "terms": 114,
            "identity_cost": 224,
            "full_support_term_costs": [9, 9],
            "total_cost": 242,
        },
        "stored signed fit",
    )
    print(
        "PASS_INDEPENDENT_C5_CHARGING_CEILING subsets=3819816 "
        "scalar_entries=12544 no_new_kappa"
    )


if __name__ == "__main__":
    main()

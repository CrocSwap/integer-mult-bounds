"""All common two-cuts, using a separate matrix reduction. Apache-2.0."""

import json
from collections import Counter
from itertools import combinations

from verify import PACKAGE, dot, geometry, read_json, require, validate_witness


def matrix_rank(values):
    rows = [[(value >> bit) & 1 for bit in range(9)] for value in values]
    pivot = 0
    for column in range(9):
        found = next((i for i in range(pivot, len(rows)) if rows[i][column]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(pivot + 1, len(rows)):
            if rows[i][column]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot], strict=True)]
        pivot += 1
    return pivot


def main():
    witness = read_json(PACKAGE / "WITNESS.json")
    validate_witness(witness)
    points, labels = geometry()
    covered = set(witness["U_roots"]) | set(witness["V_roots"])
    outside = [
        [t for t in range(112) if t not in covered and dot(h, points[t])]
        for h in witness["directions"]
    ]
    own = [cut[0] for cut in witness["individual_cuts"]]
    require(
        all(matrix_rank(labels[t] for t in row) == 8 for row in outside),
        "independent uncut ranks",
    )
    histogram = Counter()
    for pair in combinations(range(112), 2):
        eligible = [
            i
            for i, row in enumerate(outside)
            if matrix_rank(labels[t] for t in row if t not in pair) <= 7
        ]
        require(
            eligible == [i for i, root in enumerate(own) if root in pair],
            "common cut differs from indispensable-root rule",
        )
        histogram[len(eligible)] += 1
    require(histogram == {0: 5356, 1: 832, 2: 28}, "all common-cut histogram")
    print(
        json.dumps(
            {
                "status": "PASS_INDEPENDENT_COMMON_CUTS",
                "pairs": 6216,
                "histogram": dict(histogram),
                "maximum_span_on_eight": 2,
            }
        )
    )


if __name__ == "__main__":
    main()

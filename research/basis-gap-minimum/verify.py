#!/usr/bin/env python3
"""Minimum of one five-cell query under two bases.

The checker prices these two bases. It does not enumerate the other fixtures.
"""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_BASIS_GAP coordinate=15 mixed=17 no_new_kappa"
FIXTURE_SHA = "1af5f743c7b41503bd013883ef5b214e722a0334dcb10aa602d62083ab4e15dc"


def fail(message):
    raise SystemExit("FAIL_BASIS_GAP " + message)


def require(condition, message):
    if not condition:
        fail(message)


def row_rank(rows):
    if not rows:
        return 0
    matrix = list(rows)
    width = max(row.bit_length() for row in matrix)
    pivot = 0
    for column in range(width):
        selected = next((index for index in range(pivot, len(matrix)) if matrix[index] & (1 << column)), None)
        if selected is None:
            continue
        matrix[pivot], matrix[selected] = matrix[selected], matrix[pivot]
        for index in range(len(matrix)):
            if index != pivot and matrix[index] & (1 << column):
                matrix[index] ^= matrix[pivot]
        pivot += 1
    return pivot


def labels_of(case):
    labels = [[] for _ in case["cells"]]
    offset = 0
    offsets = []
    for block in case["blocks"]:
        offsets.append(offset)
        offset += block["dimension"]
    for index, cell in enumerate(case["cells"]):
        for block_index, column in cell["ports"]:
            labels[index].append(case["blocks"][block_index]["bases"][cell["group"]][column] << offsets[block_index])
    return labels


def factors(case, parameter, family):
    count = len(case["cells"]) + 2
    groups = {
        "A": [int(index < count - 2 and case["cells"][index]["group"] == "A") for index in range(count)],
        "B": [int(index < count - 2 and case["cells"][index]["group"] == "B") for index in range(count)],
        "C": [int(index < count - 2 and case["cells"][index]["group"] == "C") for index in range(count)],
    }
    queries = [[] for _ in range(4)]
    readers = [[] for _ in range(4)]
    for left, middle, right, weight in zip(groups["A"], groups["B"], groups["C"], parameter):
        if family == "VVV":
            query = (left + middle, left + right, middle + right, left + middle + right)
            reader = (left + middle - right - weight, left - middle + right - weight, -left + middle + right - weight, 2 * weight)
        else:
            query = (left + middle - right, left - middle + right, -left + middle + right, left + middle + right)
            reader = (left + middle - weight, left + right - weight, middle + right - weight, weight)
        for term in range(4):
            queries[term].append(query[term])
            readers[term].append(reader[term])
    return queries, readers


def charges(case, labels, values, family):
    queries, readers = factors(case, [*values, 0, 0], family)
    costs = []
    for query, reader in zip(queries, readers):
        rows = [vector for index, cell in enumerate(labels) if query[index] for vector in cell]
        columns = [vector for index, cell in enumerate(labels) if reader[index] for vector in cell]
        matrix = [sum(((row & column).bit_count() % 2) << index for index, column in enumerate(columns)) for row in rows]
        costs.append(row_rank(matrix))
    return costs


def floors(case):
    vvv = sum(block["dimension"] * (1 if len(block["bases"]) == 1 else 3) for block in case["blocks"])
    mmm = sum(block["dimension"] * (2 if len(block["bases"]) == 1 else 3) for block in case["blocks"])
    return vvv, mmm


def minimum(case, family, alphabet, floor):
    labels = labels_of(case)
    best = None
    hits = 0
    for values in itertools.product(alphabet, repeat=len(labels)):
        total = sum(charges(case, labels, values, family))
        if family == "VVV":
            require(total >= floor, "an assignment beat the floor")
            hits += total == floor
        best = total if best is None else min(best, total)
    return best, hits


def evaluate():
    require(hashlib.sha256((PACKAGE / "fixtures.json").read_bytes()).hexdigest() == FIXTURE_SHA, "fixture drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    record = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(record["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    cases = json.loads((PACKAGE / "fixtures.json").read_text(encoding="utf-8"))
    require([case["name"] for case in cases] == ["basis-gap-coordinate", "basis-gap-mixed"], "the fixture pair moved")
    require(cases[0]["cells"] == cases[1]["cells"], "the cells are not the same query")
    changed = [index for index, (left, right) in enumerate(zip(cases[0]["blocks"], cases[1]["blocks"])) if left != right]
    require(changed == [3], "more than the four-dimensional basis changed")
    floor, mmm_floor = floors(cases[0])
    mixed_floor, mixed_mmm_floor = floors(cases[1])
    require((floor, mixed_floor, mmm_floor, mixed_mmm_floor) == (15, 15, 18, 18), "the floors moved")
    coordinate_min, coordinate_hits = minimum(cases[0], "VVV", (0, 1, -1), floor)
    mixed_min, mixed_hits = minimum(cases[1], "VVV", (0, 1, -1), mixed_floor)
    coordinate_mmm, _ = minimum(cases[0], "MMM", (0, 1), mmm_floor)
    mixed_mmm, _ = minimum(cases[1], "MMM", (0, 1), mixed_mmm_floor)
    require((coordinate_min, coordinate_hits) == (15, 1), "the coordinate minimum moved")
    require((mixed_min, mixed_hits) == (17, 0), "the mixed minimum moved")
    require(coordinate_mmm == mixed_mmm == 18, "the MMM minimum moved")
    return {
        "floor": 15,
        "coordinate_minimum": 15,
        "coordinate_hits": 1,
        "mixed_minimum": 17,
        "mixed_hits": 0,
        "mmm_floor": 18,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()

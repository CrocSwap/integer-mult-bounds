#!/usr/bin/env python3
"""Exact finite certificate for one/two-line source-complement lookup.

The unbounded-height reduction is a paper induction in README.md. This
program checks its finite normal forms, not that induction or a machine run.
Requires only Python's standard library. Prepared with AI assistance from
the independently reviewed Tintagel v9 research packet (12 October 2026).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from itertools import combinations, permutations, product


VALUES = tuple(map(Q, (
    "-4", "-3", "-5/2", "-2", "-3/2", "-1", "-1/2", "-1/3",
    "-1/4", "-1/6", "0", "1/6", "1/4", "1/3", "1/2", "2/3",
    "3/4", "1", "3/2", "2",
)))
COEFFICIENTS = tuple(map(Q, (
    "-6", "-4", "-3", "-2", "-3/2", "-1", "-1/2", "-1/3",
    "-1/4", "-1/6", "1/2", "1", "3/2", "2", "3", "4", "6",
)))
EXPECTED_DIGEST = "adf555d553a11c9f2862ddf6a7206fd03428ec657763f60f9aecfc6d4850ec7d"


def matrix(height: int, source: tuple[int, ...], target: tuple[int, ...] | None):
    """I - U V^t, with V_T(j)=(3*[j in T]-1)/6."""
    lines = (source,) if target is None else (source, target)
    return [[Q(i == j) - sum((Q(2 if j in line else -1, 6)
                              for line in lines if i in line), Q())
             for j in range(height)] for i in range(height)]


def eliminate(initial, values: set[Q], coefficients: set[Q]):
    """Top-down/rightmost exact source reference; record every intermediate."""
    height = len(initial)
    data = [row[:] for row in initial]
    values.update(value for row in data for value in row)
    remaining_rows = list(range(height))
    remaining_cols = list(range(height))
    word, pivots = [], []
    for row in range(height):
        column = next((j for j in reversed(remaining_cols) if data[row][j]), None)
        if column is None:
            continue
        pivot = data[row][column]
        values.add(pivot)
        for j in remaining_cols:
            if j < column and data[row][j]:
                coefficient = -data[row][j] / pivot
                coefficients.add(coefficient)
                word.append(("column", column, j, coefficient))
                for i in range(height):
                    data[i][j] += coefficient * data[i][column]
                    values.add(data[i][j])
        for i in remaining_rows:
            if i > row and data[i][column]:
                coefficient = -data[i][column] / pivot
                coefficients.add(coefficient)
                word.append(("row", row, i, coefficient))
                for j in range(height):
                    data[i][j] += coefficient * data[row][j]
                    values.add(data[i][j])
        coefficient = 1 / pivot
        coefficients.add(coefficient)
        word.append(("scale", row, row, coefficient))
        for j in range(height):
            data[row][j] *= coefficient
            values.add(data[row][j])
        pivots.append((row, column))
        remaining_rows.remove(row)
        remaining_cols.remove(column)
    assert all(data[i][j] == int((i, j) in pivots)
               for i in range(height) for j in range(height))
    return word, pivots


def normal_form(labels: tuple[str, ...], gaps: tuple[int, ...]):
    layout = []
    for gap, label in zip(gaps, labels):
        layout.extend("." for _ in range(gap))
        layout.append(label)
    layout.extend("." for _ in range(gaps[-1]))
    source = tuple(i for i, label in enumerate(layout) if label in ("X", "A"))
    target = (tuple(i for i, label in enumerate(layout) if label in ("X", "B"))
              if "B" in labels else None)
    assert len(source) == 3
    assert target is None or (len(target) == 3 and
                              len(set(source) & set(target)) == 1)
    return len(layout), source, target


def compress(height: int, source: tuple[int, ...], target: tuple[int, ...]):
    support = sorted(set(source) | set(target))
    kept = set(support)
    for low, high in zip((-1, *support), (*support, height)):
        if high > low + 1:
            kept.add(high - 1)
    positions = {original: new for new, original in enumerate(sorted(kept))}
    return (len(kept), tuple(positions[i] for i in source),
            tuple(positions[i] for i in target))


def guard_against_unit_row_overstatement():
    """An earlier b pivot constrains column a, not the whole row b."""
    data = matrix(5, (0, 1, 2), None)
    pivot = data[0][4]
    assert pivot == Q(1, 6)
    for column in range(4):
        coefficient = -data[0][column] / pivot
        for row in range(5):
            data[row][column] += coefficient * data[row][4]
    for row in range(1, 5):
        if data[row][4]:
            coefficient = -data[row][4] / pivot
            for column in range(5):
                data[row][column] += coefficient * data[0][column]
    for column in range(5):
        data[0][column] /= pivot
    assert data[4] == [Q(-4), Q(2), Q(2), Q(-1), Q(0)]
    assert data[4] != [Q(0), Q(0), Q(0), Q(-1), Q(0)]
    assert data[3] == [Q(0), Q(0), Q(0), Q(1), Q(0)]
    assert all(data[row][3] == 0 for row in range(3))
    return [str(value) for value in data[4]]


def certificate(stress: bool):
    counterexample_row = guard_against_unit_row_overstatement()
    seen_values: set[Q] = set()
    seen_coefficients: set[Q] = set()
    digest = hashlib.sha256()
    cases = records = pivots = 0
    patterns = sorted(set(permutations(("X", "A", "A", "B", "B"))))
    assert len(patterns) == 30
    for labels in (("X", "A", "A"), *patterns):
        for gaps in product((0, 1), repeat=len(labels) + 1):
            height, source, target = normal_form(labels, gaps)
            word, pairs = eliminate(matrix(height, source, target),
                                    seen_values, seen_coefficients)
            assert len(pairs) == height - (1 if target is None else 2)
            assert seen_values <= set(VALUES)
            assert seen_coefficients <= set(COEFFICIENTS)
            cases += 1
            records += len(word)
            pivots += len(pairs)
            digest.update((str(labels) + "/" + str(gaps) + "/" +
                           str(word) + "/" + str(pairs) + "\n").encode())
    assert (cases, records, pivots) == (1936, 65416, 11584)
    assert seen_values == set(VALUES)
    assert seen_coefficients == set(COEFFICIENTS)
    assert digest.hexdigest() == EXPECTED_DIGEST

    checks = 0
    if stress:
        for height in (7, 8, 9):
            for source in combinations(range(height), 3):
                for target in combinations(range(height), 3):
                    if len(set(source) & set(target)) != 1:
                        continue
                    full_values: set[Q] = set()
                    full_coefficients: set[Q] = set()
                    core_values: set[Q] = set()
                    core_coefficients: set[Q] = set()
                    eliminate(matrix(height, source, target),
                              full_values, full_coefficients)
                    core_height, core_source, core_target = compress(
                        height, source, target)
                    eliminate(matrix(core_height, core_source, core_target),
                              core_values, core_coefficients)
                    assert full_values <= core_values | {Q(0), Q(1), Q(-1)}
                    assert full_coefficients <= core_coefficients | {Q(1), Q(-1)}
                    checks += 1
        assert checks == 6090
    return {
        "status": "PASS_EXACT_GAP_SKELETON_SOURCE_LOOKUP",
        "skeletons": cases,
        "maximum_height": 11,
        "word_records": records,
        "pivots": pivots,
        "values": [str(value) for value in VALUES],
        "coefficients": [str(value) for value in COEFFICIENTS],
        "skeleton_digest": digest.hexdigest(),
        "optional_compression_checks": checks,
        "nonunit_row_b_guard": counterexample_row,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stress", action="store_true",
                        help="also check all h=7..9 neighboring two-line cases")
    options = parser.parse_args()
    print(json.dumps(certificate(options.stress), indent=2))

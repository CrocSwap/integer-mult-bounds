#!/usr/bin/env python3
"""Generating-basis check of the new concentration lemma. Apache-2.0."""

import hashlib
import json
import sys
from itertools import combinations, product
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "research/p112-root-simplex-exclusion/geometry.py"
SOURCE_HASH = "b8ac379e41f5ad83bdb6c7f7c55129fc3d9c07801ea61591478f25d72ff0b021"


def check(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    check(len(pairs) == len({key for key, _ in pairs}), "duplicate JSON key")
    return dict(pairs)


def load(path):
    check(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 262144,
        "bounded regular input",
    )
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def roots_and_labels():
    roots = []
    for row in product((-2, 0, 2), repeat=8):
        if sum(x != 0 for x in row) == 2 and next(x for x in row if x) == 2:
            roots.append(row)
    for tail in product((-1, 1), repeat=7):
        if sum(x == -1 for x in tail) % 2 == 0:
            roots.append((1, *tail))
    roots.sort()
    check(len(roots) == len(set(roots)) == 120, "independent root inventory")
    labels = [label(root) for root in roots]
    check(len(set(labels)) == 120, "independent label inventory")
    return roots, labels


def label(root):
    c = [0] * 8
    c[0] = root[7]
    c[7] = (root[6] + c[0]) // 2
    for j in range(6, 2, -1):
        c[j] = (root[j - 1] + c[0] + 2 * c[j + 1]) // 2
    numerators = [root[0] + root[1] + 2 * c[3], root[1] - root[0] + 2 * c[0] + 2 * c[3]]
    check(all(x % 4 == 0 for x in numerators), "branch divisibility")
    c[1], c[2] = [x // 4 for x in numerators]
    rebuilt = [c[0] + 2 * c[1] - 2 * c[2], -c[0] + 2 * c[1] + 2 * c[2] - 2 * c[3]]
    rebuilt += [-c[0] + 2 * c[j] - 2 * c[j + 1] for j in range(3, 7)]
    rebuilt += [-c[0] + 2 * c[7], c[0]]
    check(tuple(rebuilt) == tuple(root), "independent simple-coordinate reconstruction")
    return 1 + sum((x % 2) << (j + 1) for j, x in enumerate(c))


def echelon(values):
    rows = list(values)
    rank = 0
    for bit in range(9):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> bit & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> bit & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return tuple(rows[:rank])


def closure(rows, labels):
    points = {0}
    for row in rows:
        points |= {value ^ row for value in points}
    return sum(1 << i for i, value in enumerate(labels) if value in points)


def mask_digest(masks):
    return hashlib.sha256(
        b"".join(mask.to_bytes(15, "big") for mask in sorted(masks))
    ).hexdigest()


def generating_basis_check(labels, axis, dimension, threshold):
    seen, critical = set(), set()
    histogram = {}
    axis_mask = sum(1 << i for i in axis)
    count = 0
    for indices in combinations(axis, dimension):
        count += 1
        rows = echelon([labels[i] for i in indices])
        if len(rows) != dimension or rows in seen:
            continue
        seen.add(rows)
        mask = closure(rows, labels)
        size = (mask & axis_mask).bit_count()
        if size >= threshold:
            check(mask & ~axis_mask == 0, "independent critical closure escapes axis")
            critical.add(mask)
            histogram[str(size)] = histogram.get(str(size), 0) + 1
    check(count == comb(33, dimension), "incomplete generating-basis domain")
    check(
        histogram == ({"10": 512, "12": 120} if dimension == 5 else {"20": 16}),
        "independent critical histogram",
    )
    return {
        "dimension": dimension,
        "basis_subsets": count,
        "critical_histogram": histogram,
        "critical_sha256": mask_digest(critical),
    }


def audit(expected):
    roots, labels = roots_and_labels()
    a, b = (0, 0, 0, 0, 0, 2, -2, 0), (0, 2, -2, 0, 0, 0, 0, 0)
    axes = []
    for target, other in [(a, b), (b, a)]:
        axis = [
            i
            for i, root in enumerate(roots)
            if sum(x * y for x, y in zip(root, target, strict=True))
            and not sum(x * y for x, y in zip(root, other, strict=True))
        ]
        check(len(axis) == 33, "independent full-axis size")
        axes.append(
            [
                generating_basis_check(labels, axis, d, threshold)
                for d, threshold in [(5, 10), (6, 18)]
            ]
        )
    for observed, stored in zip(axes, expected["axes"], strict=True):
        for observed_row, stored_row in zip(observed, stored, strict=True):
            for key in ("dimension", "critical_histogram", "critical_sha256"):
                check(
                    observed_row[key] == stored_row[key],
                    "independent concentration receipt",
                )
    check(
        expected["incidence"]["support_budget"] == 84
        and expected["incidence"]["singleton_lower_bounds"] == [6, 10, 10, 10, 18, 18]
        and expected["incidence"]["E6_joint_allowance"] == 146,
        "independent incidence constants",
    )
    return {"schema": "p112-six-piece-basis-check/v1", "axes": axes}


def main():
    check(not sys.argv[1:], "no command-line arguments accepted")
    check(
        SOURCE.is_file()
        and not SOURCE.is_symlink()
        and SOURCE.stat().st_size <= 262144,
        "independent geometry input",
    )
    check(
        hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_HASH,
        "independent source hash",
    )
    result = audit(load(HERE / "RESULT.json"))
    check(
        result == load(HERE / "BASIS-CHECK.json"), "independent basis receipt differs"
    )
    print("PASS_INDEPENDENT_SIX_PIECE_CONCENTRATION")


if __name__ == "__main__":
    main()

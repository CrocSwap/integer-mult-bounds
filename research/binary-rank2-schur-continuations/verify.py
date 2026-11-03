#!/usr/bin/env python3
"""Exact next-pivot table for binary rank-two pairs; Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


TYPES = ("1111", "1011", "0111", "0000", "0001", "0010", "0011")
# Credited terminal split counts from codyw912 / PR4735, not new results.
TERMINAL = (10, 6, 6, 1, 3, 3, 4)
PARENT = (1, 2, 0, 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return (x & y).bit_count() & 1


def apply(matrix, vector):
    return sum(dot(row, vector) << i for i, row in enumerate(matrix))


def product(left, right):
    n = len(left)
    columns = [sum(((right[i] >> j) & 1) << i for i in range(n))
               for j in range(n)]
    return tuple(sum(dot(row, col) << j for j, col in enumerate(columns))
                 for row in left)


def rank(matrix, n):
    rows = list(matrix)
    pivot = 0
    for j in range(n):
        found = next((i for i in range(pivot, len(rows)) if rows[i] >> j & 1), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(pivot + 1, len(rows)):
            if rows[i] >> j & 1:
                rows[i] ^= rows[pivot]
        pivot += 1
    return pivot


def inverse(matrix):
    n = len(matrix)
    rows = [row | (1 << (n + i)) for i, row in enumerate(matrix)]
    for j in range(n):
        found = next((i for i in range(j, n) if rows[i] >> j & 1), None)
        require(found is not None, "singular matrix")
        rows[j], rows[found] = rows[found], rows[j]
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    return tuple(row >> n for row in rows)


def parent_classes():
    gl2 = [rows for rows in itertools.product(range(4), repeat=2)
           if rank(rows, 2) == 2]
    group = [(u[0], u[1], v[0] << 2, v[1] << 2) for u in gl2 for v in gl2]
    projectors = {rows for rows in itertools.product(range(16), repeat=4)
                  if product(rows, rows) == rows and rank(rows, 4) == 2}
    require(len(group) == 36 and len(projectors) == 560, "parent inventory")
    classes = {}
    for q in sorted(projectors):
        if q in classes:
            continue
        orbit = {product(product(g, q), inverse(g)) for g in group}
        require(q == min(orbit) and orbit <= projectors, "orbit construction")
        require(not any(item in classes for item in orbit), "overlapping classes")
        for item in orbit:
            classes[item] = (q, len(orbit))
    require(len(classes) == 560, "incomplete orbit cover")
    return classes


def residual(matrix, a, beta):
    """Coordinates on ker(beta), using its three nonpivot coordinates."""
    pivot = next(j for j in range(4) if beta >> j & 1)
    free = [j for j in range(4) if j != pivot]
    image = apply(matrix, a)
    columns = []
    for j in free:
        w = (1 << j) | (((beta >> j) & 1) << pivot)
        value = apply(matrix, w)
        value ^= image if dot(beta, value) else 0
        require(dot(beta, value) == 0, "residual outside complement")
        columns.append(sum(((value >> k) & 1) << i for i, k in enumerate(free)))
    rows = tuple(sum(((col >> i) & 1) << j for j, col in enumerate(columns))
                 for i in range(3))
    require(product(rows, rows) == rows and rank(rows, 3) == 1, "residual rank")
    return rows


def factor(matrix):
    columns = [sum(((matrix[i] >> j) & 1) << i for i in range(3))
               for j in range(3)]
    u = next(col for col in columns if col)
    phi = sum((col != 0) << j for j, col in enumerate(columns))
    require(all(col in (0, u) for col in columns) and dot(u, phi) == 1,
            "not a rank-one idempotent")
    return u, phi


def terminal_type(first, second):
    u, phi = factor(first)
    v, psi = factor(second)
    code = "".join(str(int(x)) for x in
                   (u == v, phi == psi, dot(phi, v), dot(psi, u)))
    require(code in TYPES, "unknown terminal state")
    return TYPES.index(code)


def transitions(q):
    counts = [0] * 7
    witnesses = [None] * 7
    for a in range(1, 16):
        pa, qa = apply(PARENT, a), apply(q, a)
        for beta in range(1, 16):
            if dot(beta, a) == dot(beta, pa) == dot(beta, qa) == 1:
                state = terminal_type(residual(PARENT, a, beta), residual(q, a, beta))
                counts[state] += 1
                if witnesses[state] is None:
                    witnesses[state] = [a, beta]
    return counts, witnesses


def inherited_parents(classes):
    # The seven PR4735 representatives use diag(0,0,1,1).
    old = ((0, 0, 4, 8), (0, 0, 4, 9), (0, 2, 0, 8), (0, 2, 2, 8),
           (0, 4, 4, 8), (0, 4, 4, 9), (0, 6, 0, 8))
    swap = (4, 8, 1, 2)
    return {classes[product(product(swap, q), swap)][0] for q in old}


def compute():
    classes = parent_classes()
    inherited = inherited_parents(classes)
    representatives = sorted({rep for rep, size in classes.values()})
    require(len(representatives) == 30 and len(inherited) == 7, "class cardinalities")
    rows = []
    for q in representatives:
        counts, witnesses = transitions(q)
        admitted = sum(counts)
        full = 6 * sum(n * g for n, g in zip(counts, TERMINAL, strict=True))
        rows.append({"q": list(q), "orbit_size": classes[q][1],
                     "inherited_parent": q in inherited,
                     "transitions": counts, "split_witnesses": witnesses,
                     "first_guard_headers": 168 * admitted,
                     "full_guard_headers": full,
                     "depth_counts": [20160 - 168 * admitted, 168 * admitted - full, full]})
    return {"parent": list(PARENT), "terminal_types": list(TYPES),
            "terminal_split_counts_inherited": list(TERMINAL), "rows": rows}


def controls(table):
    require(table["rows"][0]["q"] == [0, 0, 4, 8], "stable representative order")
    # Q=I+P makes beta(a)=beta(Pa)=beta(Qa)=1 inconsistent.
    require(table["rows"][0]["first_guard_headers"] == 0, "complementary control")
    require(sum(row["orbit_size"] for row in table["rows"]) == 560, "orbit mass")
    require(all(sum(row["depth_counts"]) == 20160 for row in table["rows"]), "depth mass")
    require(all(n >= 0 for row in table["rows"] for n in row["depth_counts"]), "negative mass")
    asymmetric = any(row["transitions"][1] != row["transitions"][2] for row in table["rows"])
    require(asymmetric, "ordered terminal types were merged")
    try:
        inverse((0, 0))
    except ValueError:
        return
    raise ValueError("singular inverse accepted")


def sharp_boundary(table):
    rows = table["rows"]
    positive = [row for row in rows if row["full_guard_headers"] > 0]
    minimum = min(row["full_guard_headers"] for row in positive)
    minimizers = [row["q"] for row in positive if row["full_guard_headers"] == minimum]
    zeros = [row["q"] for row in rows if row["full_guard_headers"] == 0]
    require(minimum == 144 and minimizers == [[0, 0, 4, 9], [0, 4, 4, 8]],
            "sharp positive boundary")
    require(zeros == [[0, 0, 4, 8]], "zero case classification")
    return {"new_parent_rows": sum(not row["inherited_parent"] for row in rows),
            "minimum_positive_headers": minimum, "total_headers": 20160,
            "minimum_positive_probability": "1/140", "minimizers": minimizers,
            "zero_cases": zeros}


def file_hashes():
    root = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py", "oracle.py")
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit a newly computed receipt")
    args = parser.parse_args()
    table = compute()
    controls(table)
    receipt = {"status": "PASS_BINARY_RANK2_SCHUR_CONTINUATIONS", "table": table,
               "summary": sharp_boundary(table),
               "files_sha256": file_hashes()}
    if not args.emit:
        expected = json.loads(Path(__file__).with_name("RESULT.json").read_text())
        require(json.dumps(expected, sort_keys=True) == json.dumps(receipt, sort_keys=True),
                "receipt or source hash mismatch")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent dense full-header oracle; no primary/predecessor imports."""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


def check(condition, message):
    if not condition:
        raise ValueError(message)


def unpack(rows, n=4):
    check(len(rows) == n, "matrix size")
    check(all(type(row) is int and 0 <= row < 2**n for row in rows), "matrix encoding")
    return tuple(tuple((row // 2**j) % 2 for j in range(n)) for row in rows)


def pack(matrix):
    return tuple(sum(x * 2**j for j, x in enumerate(row)) for row in matrix)


def inner(x, y):
    return sum(a * b for a, b in zip(x, y, strict=True)) % 2


def mv(matrix, vector):
    return tuple(inner(row, vector) for row in matrix)


def mm(left, right):
    return tuple(tuple(inner(row, col) for col in zip(*right, strict=True)) for row in left)


def invert(matrix):
    n = len(matrix)
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        chosen = next((i for i in range(j, n) if rows[i][j]), None)
        if chosen is None:
            return None
        rows[j], rows[chosen] = rows[chosen], rows[j]
        for i in range(n):
            if i != j and rows[i][j]:
                rows[i] = [(x + y) % 2 for x, y in zip(rows[i], rows[j], strict=True)]
    return tuple(tuple(row[n:]) for row in rows)


def headers():
    vectors = [tuple((x // 2**j) % 2 for j in range(4)) for x in range(1, 16)]
    result = []
    for columns in itertools.permutations(vectors, 4):
        matrix = tuple(zip(*columns, strict=True))
        inverse = invert(matrix)
        if inverse is not None:
            result.append((matrix, inverse, columns))
    check(len(result) == 20160, "full-header inventory")
    return result


def all_projectors(full):
    # M diag(1,1,0,0) M^-1, independently generated from full headers.
    return {tuple(tuple(sum(cols[k][i] * inv[k][j] for k in range(2)) % 2
                        for j in range(4)) for i in range(4))
            for matrix, inv, cols in full}


def orbit_cover(rows, full):
    p = unpack((1, 2, 0, 0))
    group = [(m, inv) for m, inv, cols in full if mm(m, p) == mm(p, m)]
    check(len(group) == 36, "centralizer inventory")
    cover = set()
    for row in rows:
        q = unpack(row["q"])
        orbit = {mm(mm(m, q), inv) for m, inv in group}
        check(tuple(row["q"]) == min(pack(item) for item in orbit), "noncanonical parent")
        check(type(row["orbit_size"]) is int and len(orbit) == row["orbit_size"], "orbit size")
        check(not (cover & orbit), "duplicate parent class")
        cover.update(orbit)
    check(cover == all_projectors(full) and len(cover) == 560, "incomplete parent coverage")


def rank_one_factor(matrix):
    columns = list(zip(*matrix, strict=True))
    u = next(col for col in columns if any(col))
    phi = tuple(int(any(col)) for col in columns)
    check(all(col == u or not any(col) for col in columns), "residual is not rank one")
    check(inner(u, phi) == 1, "residual is not idempotent")
    return u, phi


def block_type(p, q, matrix, inv):
    factors = []
    for operator in (p, q):
        a = mm(mm(inv, operator), matrix)
        check(a[0][0] == 1, "nonunit pivot")
        schur = tuple(tuple((a[i][j] + a[i][0] * a[0][j]) % 2 for j in range(1, 4))
                      for i in range(1, 4))
        factors.append(rank_one_factor(schur))
    (u, phi), (v, psi) = factors
    return "".join(str(int(x)) for x in
                   (u == v, phi == psi, inner(phi, v), inner(psi, u)))


def count_row(row, full, types):
    p, q = unpack((1, 2, 0, 0)), unpack(row["q"])
    vectors = [tuple((x // 2**j) % 2 for j in range(4)) for x in range(16)]
    images = {v: (mv(p, v), mv(q, v)) for v in vectors}
    first, both = 0, 0
    splits = {}
    for matrix, inv, cols in full:
        a, b = cols[:2]
        alpha, beta = inv[:2]
        pa, qa = images[a]
        if inner(alpha, pa) != 1 or inner(alpha, qa) != 1:
            continue
        first += 1
        pb, qb = images[b]
        d1 = (inner(beta, pb) + inner(alpha, pb) * inner(beta, pa)) % 2
        d2 = (inner(beta, qb) + inner(alpha, qb) * inner(beta, qa)) % 2
        both += int(d1 == d2 == 1)
        key = (sum(x * 2**i for i, x in enumerate(a)),
               sum(x * 2**i for i, x in enumerate(alpha)))
        if key not in splits:
            splits[key] = block_type(p, q, matrix, inv)
    counts = [sum(code == label for code in splits.values()) for label in types]
    witnesses = [min((list(key) for key, code in splits.items() if code == label), default=None)
                 for label in types]
    check(first == 168 * len(splits), "split completion fiber")
    return first, both, counts, witnesses


def validate_row(row, observed):
    first, both, counts, witnesses = observed
    check(type(row["first_guard_headers"]) is int and first == row["first_guard_headers"],
          "first-guard count")
    check(type(row["full_guard_headers"]) is int and both == row["full_guard_headers"],
          "full-guard count")
    check(row["transitions"] == counts and all(type(x) is int for x in row["transitions"]),
          "transition count")
    check(row["split_witnesses"] == witnesses, "split witness")
    check(row["depth_counts"] == [20160 - first, first - both, both], "depth distribution")


def controls(row, observed):
    cases = []
    for key in ("first_guard_headers", "full_guard_headers"):
        mutant = dict(row)
        mutant[key] = row[key] + 1
        cases.append((key, mutant))
    mutant = dict(row)
    mutant["transitions"] = [row["transitions"][0] + 1] + row["transitions"][1:]
    cases.append(("transition", mutant))
    rejected = 0
    for label, mutant in cases:
        try:
            validate_row(mutant, observed)
        except ValueError:
            rejected += 1
    check(rejected == 3, "false row accepted")
    check(invert(((0, 0), (0, 0))) is None, "singular inverse accepted")
    return rejected + 1


def source_hashes(receipt):
    root = Path(__file__).resolve().parent
    names = {"README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py", "oracle.py"}
    check(set(receipt["files_sha256"]) == names, "source inventory")
    for name in sorted(names):
        check(hashlib.sha256((root / name).read_bytes()).hexdigest() ==
              receipt["files_sha256"][name], "source hash: " + name)


def boundary_check(summary, rows, observations):
    successes = [item[1] for item in observations]
    minimum = min(count for count in successes if count > 0)
    minimizers = [row["q"] for row, count in zip(rows, successes, strict=True) if count == minimum]
    zeros = [row["q"] for row, count in zip(rows, successes, strict=True) if count == 0]
    check(minimum == 144 and Fraction(minimum, 20160) == Fraction(1, 140), "sharp minimum")
    check(summary["minimum_positive_headers"] == minimum and
          summary["minimum_positive_probability"] == "1/140" and
          summary["total_headers"] == 20160, "boundary receipt")
    check(summary["minimizers"] == minimizers and summary["zero_cases"] == zeros, "extremizers")
    check(summary["new_parent_rows"] == 23 and
          sum(not row["inherited_parent"] for row in rows) == 23, "new-row credit")


def main():
    receipt = json.loads(Path(__file__).with_name("RESULT.json").read_text())
    source_hashes(receipt)
    table = receipt["table"]
    check(table["parent"] == [1, 2, 0, 0], "first projector")
    types = ["1111", "1011", "0111", "0000", "0001", "0010", "0011"]
    check(table["terminal_types"] == types, "terminal order")
    rows = table["rows"]
    check(len(rows) == 30, "parent row count")
    full = headers()
    orbit_cover(rows, full)
    observations = [count_row(row, full, types) for row in rows]
    for row, observed in zip(rows, observations, strict=True):
        validate_row(row, observed)
    boundary_check(receipt["summary"], rows, observations)
    rejected = controls(rows[0], observations[0])
    mutant = [dict(row) for row in rows]
    mutant[0]["orbit_size"] += 1
    try:
        orbit_cover(mutant, full)
    except ValueError:
        rejected += 1
    check(rejected == 5, "false orbit accepted")
    print(json.dumps({"status": "PASS_BINARY_RANK2_DIRECT_HEADERS", "parents": len(rows),
                      "headers_per_parent": len(full), "direct_parent_headers": len(rows) * len(full),
                      "distinct_splits": sum(sum(x[2]) for x in observations),
                      "rejection_controls": rejected}, sort_keys=True))


if __name__ == "__main__":
    main()

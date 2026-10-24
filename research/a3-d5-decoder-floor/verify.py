#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite premises and witnesses for the fixed A3+D5 COPY optimum.

The normal matrix is mathematical fixture data from joaqcoo / PR1224.
No predecessor implementation, Git object, network, or dependency is imported.
"""

import argparse
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


# Four times the source's doubled normals, in its exact column order.
NORMALS = (
    (3, 5, -3, -1, -1, -1, -1, -1),
    (-5, -3, -3, -1, -1, -1, -1, -1),
    (-1, 1, 1, 3, 3, 3, 3, 3),
    (3, -3, 5, -1, -1, -1, -1, -1),
    (0, 0, 0, 8, -8, 0, 0, 0),
    (0, 0, 0, 8, 0, -8, 0, 0),
    (0, 0, 0, 8, 0, 0, -8, 0),
    (0, 0, 0, 8, 0, 0, 0, -8),
    (4, -4, -4, 4, 4, 4, -4, -4),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def binary_basis(rows):
    pivots = {}
    for row in rows:
        require(type(row) is int and 0 <= row < 1 << 120, "binary row")
        for _ in range(120):
            if not row:
                break
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
        else:
            raise ValueError("binary elimination bound")
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def roots():
    values = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            values.add(tuple(row))
    for tail in itertools.product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            values.add((1,) + tail)
    result = tuple(sorted(values, reverse=True))
    require(len(result) == 120, "root-line count")
    require(all(dot(row, row) == 8 for row in result), "root norms")
    return result


def inverse(matrix):
    require(len(matrix) == 8 and all(len(row) == 8 for row in matrix), "shape")
    work = [[Fraction(x) for x in row] +
            [Fraction(i == j) for j in range(8)] for i, row in enumerate(matrix)]
    for column in range(8):
        pivot = next((i for i in range(column, 8) if work[i][column]), None)
        require(pivot is not None, "normal basis is singular")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
        for i in range(8):
            if i != column:
                factor = work[i][column]
                work[i] = [a - factor * b for a, b in
                           zip(work[i], work[column], strict=True)]
    require(all(work[i][j] == (i == j) for i in range(8) for j in range(8)),
            "inverse reduction")
    return tuple(tuple(row[8:]) for row in work)


def coefficients(lines):
    require(all(sum(NORMALS[k][c] for k in range(4)) == 0 for c in range(8)),
            "common-shift dependency")
    inv = inverse(tuple(tuple(NORMALS[k][c] for k in range(1, 9))
                        for c in range(8)))
    result = tuple((Fraction(0),) + tuple(dot(row, tuple(8 * x for x in line))
                                        for row in inv) for line in lines)
    for line, row in zip(lines, result, strict=True):
        require(all(sum(row[k] * NORMALS[k][c] for k in range(9)) == 8 * line[c]
                    for c in range(8)), "coefficient equation")
    return result


def geometry(lines):
    grams = tuple(tuple(dot(a, b) // 4 for b in lines) for a in lines)
    require(all(dot(a, b) % 4 == 0 for a in lines for b in lines), "integral Gram")
    pairing = tuple(sum(((g + 1) % 2) << j for j, g in enumerate(row))
                    for row in grams)
    basis = binary_basis(pairing)
    require(len(basis) == 9, "pairing rank")
    columns = tuple(row.bit_length() - 1 for row in basis)
    labels = tuple(sum(((row >> column) & 1) << j
                       for j, column in enumerate(columns)) for row in pairing)
    require(len(binary_basis(labels)) == 9, "label projection")
    readers = tuple(sum((dot(line, normal) != 0) << i
                        for i, line in enumerate(lines)) for normal in NORMALS)
    require(all(len(binary_basis(row & mask for row in pairing)) == 9
                for mask in readers), "reader ranks")
    return grams, pairing, labels, readers


def selected_rows(values, mask):
    return tuple(value for i, value in enumerate(values) if (mask >> i) & 1)


def character_supports(labels):
    supports = tuple(sum(((label & w).bit_count() % 2) << i
                         for i, label in enumerate(labels)) for w in range(512))
    require(len(set(supports)) == 512 and supports[0] == 0, "character coverage")
    return supports


def partner_tables(anchor, base, labels, supports):
    tables, forced = {}, {}
    for k in range(4):
        if k == anchor:
            continue
        difference = sum((row[anchor] != row[k]) << i for i, row in enumerate(base))
        tables[k] = tuple(sum((not (left & right & difference)) << z
                              for z, right in enumerate(supports[1:], 1))
                          for left in supports)
        forced[k] = tuple(binary_basis(selected_rows(labels, mask & difference))
                          for mask in supports)
    return tables, forced


def plane_certificate(anchor, tables):
    histogram, signatures, count = Counter(), set(), 0
    for a in range(1, 512):
        for b in range(a + 1, 512):
            if b >= (a ^ b):
                continue
            count += 1
            signature = []
            for table in tables.values():
                nonzero = table[a] & table[b]
                require(nonzero.bit_count() <= 1, "partner dimension exceeds one")
                signature.append(nonzero.bit_length() - 1 if nonzero else 0)
            signatures.add(tuple(signature))
            histogram[sum(z != 0 for z in signature)] += 1
    require(count == 43435, "plane coverage")
    require(dict(histogram) == {0: 18211, 1: 18144, 2: 6237, 3: 843},
            "plane histogram")
    require(len(signatures) == 767, "signature count")
    return signatures, {"anchor": anchor, "planes": count,
                        "nonzero_partner_histogram": dict(sorted(histogram.items())),
                        "signatures": len(signatures)}


def forced_certificate(signatures, tables, forced):
    maximum, cases, missing_constraint_witness = 0, 0, False
    for signature in sorted(signatures):
        active = tuple((k, z) for k, z in zip(tables, signature, strict=True) if z)
        for mask in range(1 << len(active)):
            chosen = tuple(pair for j, pair in enumerate(active) if (mask >> j) & 1)
            rows = tuple(row for k, z in chosen for row in forced[k][z])
            rank = len(binary_basis(rows))
            bound = 9 - rank + len(chosen)
            require(bound <= 9, "deficiency bound")
            maximum = max(maximum, bound)
            cases += 1
            missing_constraint_witness |= bool(chosen) and bound == 9
    require(maximum == 9 and missing_constraint_witness, "sharp finite bound")
    literal_checks = 0
    for k, table in tables.items():
        for z in range(1, 512):
            equations = forced[k][z]
            annihilator = sum(all((w & row).bit_count() % 2 == 0 for row in equations)
                              << w for w in range(1, 512))
            require(annihilator == table[z], "literal annihilator disagreement")
            literal_checks += 1
    return {"subset_cases": cases, "maximum_deficiency_bound": maximum,
            "literal_annihilator_checks": literal_checks,
            "missing_constraint_bound_exceeds_nine": missing_constraint_witness}


def exact_identity(coeffs, lines, grams, normals=NORMALS):
    readers = tuple(tuple(Fraction(dot(line, normal), 16) for normal in normals)
                    for line in lines)
    return all(dot(row, reader) == 2 * grams[i][j]
               for i, row in enumerate(coeffs) for j, reader in enumerate(readers))


def rank_profile(coeffs, pairing, readers):
    profile = []
    for k in range(9):
        rows = tuple(pairing[i] & readers[k] for i, row in enumerate(coeffs) if row[k])
        profile.append(len(binary_basis(rows)))
    return profile


def witness_certificate(base, lines, grams, pairing, readers):
    require(exact_identity(base, lines, grams), "eight-active witness")
    inactive = rank_profile(base, pairing, readers)
    require(inactive == [0] + [9] * 8, "eight-active ranks")
    active = [list(row) for row in base]
    require(lines[0] == (2, 2, 0, 0, 0, 0, 0, 0) and base[0][1] == -4,
            "active-witness row")
    for k in range(4):
        active[0][k] += 4
    require(exact_identity(active, lines, grams), "nine-active witness")
    profile = rank_profile(active, pairing, readers)
    require(profile == [1, 8] + [9] * 7, "nine-active ranks")
    return active, {"eight_active_profile": inactive, "nine_active_profile": profile,
                    "identity_entries_per_witness": 14400, "optimum": 72}


def controls(active, lines, grams):
    changed = [row[:] for row in active]
    changed[0][0] += 1
    require(not exact_identity(changed, lines, grams), "coefficient control")
    missing = [row[:] for row in active]
    for row in missing:
        row[4] = 0
    require(not exact_identity(missing, lines, grams), "forced-term control")
    swapped = list(NORMALS)
    swapped[0], swapped[4] = swapped[4], swapped[0]
    require(not exact_identity(active, lines, grams, tuple(swapped)), "reader control")
    generic_shift = [row[:] for row in active]
    for k in range(4):
        generic_shift[0][k] += Fraction(1, 3)
    require(exact_identity(generic_shift, lines, grams), "noncritical-shift control")
    return {"rejected_identity_mutations": 3, "noncritical_shift_identity": True}


def run():
    lines = roots()
    base = coefficients(lines)
    grams, pairing, labels, readers = geometry(lines)
    supports = character_supports(labels)
    anchors = []
    for anchor in range(4):
        tables, forced = partner_tables(anchor, base, labels, supports)
        signatures, record = plane_certificate(anchor, tables)
        record.update(forced_certificate(signatures, tables, forced))
        anchors.append(record)
    active, witnesses = witness_certificate(base, lines, grams, pairing, readers)
    return {"marker": "PASS_A3_D5_DECODER_FLOOR", "claim_type": "scoped proof",
            "root_lines": len(lines), "anchors": anchors, "witnesses": witnesses,
            "controls": controls(active, lines, grams), "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a generated receipt outside the package")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(package), "receipt inside package")
    result = run()
    filenames = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in filenames:
        path = package / name
        require(path.is_file() and not path.is_symlink(), "package source file")
        require(path.stat().st_size <= 1048576, "package source size")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result["source_sha256"] = hashes
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as stream:
            require(stream.write(payload) == len(payload), "receipt write")
    print(payload, end="")


if __name__ == "__main__":
    main()

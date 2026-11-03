#!/usr/bin/env python3
"""Exact dense B3/C3 term tariffs. Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tariff(left, right):
    require(type(left) is int and 1 <= left <= 7, "invalid left support")
    require(type(right) is int and 1 <= right <= 7, "invalid right support")
    return 3 if min(left.bit_count(), right.bit_count()) == 1 else 5


def binary_rank(rows):
    pivots = [0] * 9
    for original in rows:
        row = original
        for bit in range(8, -1, -1):
            if row & (1 << bit):
                if pivots[bit]:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return sum(value != 0 for value in pivots)


def span_rank(rows):
    """Independent finite span enumeration, without elimination."""
    span = {0}
    for row in rows:
        if row not in span:
            span |= {old ^ row for old in tuple(span)}
    require(len(span) <= 512, "span capacity exceeded")
    require(len(span) & (len(span) - 1) == 0, "nonbinary span size")
    return len(span).bit_length() - 1


def roots(kind):
    require(kind in ("B", "C"), "unknown root family")
    scale = 1 if kind == "B" else 2
    axes = [tuple(scale * int(i == j) for i in range(3)) for j in range(3)]
    edges = []
    for i, j in itertools.combinations(range(3), 2):
        for sign in (-1, 1):
            edges.append(tuple(int(k == i) + sign * int(k == j) for k in range(3)))
    return axes + edges


def literal_pairing(lines):
    require(len(lines) == 9, "root inventory must contain nine lines")
    return [[int(i == j or sum(a * b for a, b in zip(x, y)) == 0)
             for j, y in enumerate(lines)] for i, x in enumerate(lines)]


def coefficient_support(lines, vector, prime):
    values = [sum(a * b for a, b in zip(line, vector)) for line in lines]
    if prime:
        values = [value % prime for value in values]
    return tuple(i for i, value in enumerate(values) if value != 0)


def coordinate_mask(vector):
    return sum(1 << i for i, value in enumerate(vector) if value != 0)


def restricted_rows(matrix, left, right):
    return [sum(matrix[i][j] << bit for bit, j in enumerate(right)) for i in left]


def reduced_pairing(left, right):
    """Unsigned edge labels; build from incidence, not root dot products."""
    axes_left = [i for i in range(3) if left & (1 << i)]
    axes_right = [i for i in range(3) if right & (1 << i)]
    edges = list(itertools.combinations(range(3), 2))
    rows = [(i,) for i in axes_left] + [e for e in edges if any(left & (1 << i) for i in e)]
    columns = [(i,) for i in axes_right] + [e for e in edges if any(right & (1 << i) for i in e)]
    matrix = []
    for row in rows:
        values = []
        for column in columns:
            if len(row) == len(column) == 1:
                value = 1
            elif len(row) == len(column) == 2:
                value = int(row == column or set(row).isdisjoint(column))
            else:
                value = int(set(row).isdisjoint(column))
            values.append(value)
        matrix.append(sum(value << j for j, value in enumerate(values)))
    return matrix


def support_census():
    histogram = {"3": 0, "5": 0}
    transcript = []
    for left, right in itertools.product(range(1, 8), repeat=2):
        rows = reduced_pairing(left, right)
        measured = binary_rank(rows)
        require(measured == span_rank(rows), "rank engines disagree")
        require(measured == tariff(left, right), "support formula failed")
        histogram[str(measured)] += 1
        transcript.append([left, right, rows, measured])
    require(sum(histogram.values()) == 49, "support inventory incomplete")
    return {"pairs": 49, "tariffs": histogram, "transcript_sha256": digest(transcript)}


def coefficient_census(kind, prime):
    lines = roots(kind)
    matrix = literal_pairing(lines)
    alphabet = range(prime) if prime else range(-2, 3)
    vectors = [v for v in itertools.product(alphabet, repeat=3) if any(v)]
    supports = [coefficient_support(lines, v, prime) for v in vectors]
    masks = [coordinate_mask(v) for v in vectors]
    cache = {}
    histogram = {"3": 0, "5": 0}
    checked = 0
    for a, left in enumerate(supports):
        for b, right in enumerate(supports):
            key = (left, right)
            if key not in cache:
                cache[key] = binary_rank(restricted_rows(matrix, left, right))
            measured = cache[key]
            require(measured == tariff(masks[a], masks[b]), "literal root formula failed")
            histogram[str(measured)] += 1
            checked += 1
    require(checked == len(vectors) ** 2, "coefficient inventory incomplete")
    return {"family": kind, "prime": prime, "vectors": len(vectors),
            "pairs": checked, "literal_support_pairs": len(cache), "tariffs": histogram}


def expect_bad_support(left, right):
    try:
        tariff(left, right)
    except ValueError:
        return
    raise ValueError("invalid boundary was accepted")


def controls():
    for left, right in ((0, 1), (1, 0), (8, 1), (-1, 1), (True, 1), (1, "1")):
        expect_bad_support(left, right)
    lines = roots("B")
    pairing = literal_pairing(lines)
    axis = coefficient_support(lines, (1, 0, 0), 0)
    dense = coefficient_support(lines, (1, 1, 1), 0)
    require(binary_rank(restricted_rows(pairing, dense, dense)) == 5, "dense witness failed")
    require(tariff(7, 7) != 3 and tariff(7, 7) != 4, "surcharge mutations survived")
    identity = [[int(i == j) for j in range(9)] for i in range(9)]
    require(binary_rank(restricted_rows(identity, axis, axis)) == 5, "pairing escape failed")
    punctured = tuple(i for i in axis if i != 0)
    require(binary_rank(restricted_rows(pairing, punctured, punctured)) == 2, "puncture escape failed")
    binary = coefficient_support(lines, (1, 1, 1), 2)
    require(binary_rank(restricted_rows(pairing, binary, binary)) == 1, "field escape failed")
    require(not coefficient_support(roots("C"), (1, 1, 1), 2), "C3 binary collapse failed")
    return {"invalid_supports": 6, "wrong_tariffs": 2, "boundary_escapes": 4}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify():
    supports = support_census()
    cases = [coefficient_census(kind, prime)
             for kind in ("B", "C") for prime in (0, 3, 5, 7)]
    bounds = controls()
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    directory = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in names}
    return {"schema": "dense-bc3-term-tariff/v1", "support_census": supports,
            "coefficient_cases": cases, "coefficient_pairs": sum(case["pairs"] for case in cases),
            "controls": bounds, "package_sha256": hashes,
            "claim_type": "scoped written proof with finite corroboration", "new_kappa": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new external receipt; never overwrite")
    arguments = parser.parse_args()
    result = verify()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        package = Path(__file__).resolve().parent
        require(not arguments.output.resolve().is_relative_to(package), "receipt must be external")
        with arguments.output.open("x", encoding="utf-8") as stream:
            require(stream.write(rendered) == len(rendered), "short receipt write")
    print(rendered, end="")
    print("PASS_DENSE_BC3_TERM_TARIFF support_pairs=49 coefficient_pairs="
          + str(result["coefficient_pairs"]) + " tariffs=3,5 no_new_kappa")


if __name__ == "__main__":
    main()

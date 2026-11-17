#!/usr/bin/env python3
"""Exact phase-preserving widths for H plus one radical. Apache-2.0."""

import hashlib
import itertools
import json
import math
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return (left & right).bit_count() % 2


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {value ^ vector for value in tuple(values)}
    return values


def combine(rows, value):
    result = 0
    for index in range(3):
        if value >> index & 1:
            result ^= rows[index]
    return result


def phase(phases, value):
    return ((value & 1) * (value >> 1 & 1)
            + sum(phases[index] * (value >> index & 1)
                  for index in range(3))) % 2


def validate_embedding(phases, width, rows):
    require(type(width) is int and 0 <= width <= 6, "width outside 0..6")
    require(len(phases) == 3 and all(type(x) is int and x in (0, 1)
                                   for x in phases), "invalid phases")
    require(len(rows) == 3 and all(type(x) is int and 0 <= x < 1 << width
                                 for x in rows), "invalid image rows")
    require(all(row.bit_count() % 2 == 0 for row in rows), "odd image")
    images = tuple(combine(rows, value) for value in range(8))
    require(len(set(images)) == 8, "noninjective image")
    for value, image in enumerate(images):
        require(image.bit_count() // 2 % 2 == phase(phases, value),
                "quadratic phase mismatch")
        for other, other_image in enumerate(images):
            target = ((value & 1) * (other >> 1 & 1)
                      + (other & 1) * (value >> 1 & 1)) % 2
            require(dot(image, other_image) == target, "Gram mismatch")


def row_census():
    """Enumerate literal even-weight row triples, including zero rows."""
    counts = []
    candidates = 0
    for width in range(7):
        table = [0] * 8
        points = tuple(x for x in range(1 << width) if x.bit_count() % 2 == 0)
        for first, second, radical in itertools.product(points, repeat=3):
            candidates += 1
            if not dot(first, second) or dot(first, radical) or dot(second, radical):
                continue
            if len(span((first, second, radical))) != 8:
                continue
            index = (first.bit_count() // 2 % 2
                     + 2 * (second.bit_count() // 2 % 2)
                     + 4 * (radical.bit_count() // 2 % 2))
            table[index] += 1
        counts.append(table)
    require(candidates == 37450, "incomplete row census")
    return counts, candidates


def column_census():
    """Enumerate column multisets and count their labelled permutations."""
    counts = []
    candidates = 0
    for width in range(7):
        table = [0] * 8
        for columns in itertools.combinations_with_replacement(range(8), width):
            candidates += 1
            weights = tuple(sum(column >> bit & 1 for column in columns)
                            for bit in range(3))
            if any(weight % 2 for weight in weights) or len(span(columns)) != 8:
                continue
            pairings = tuple(sum((column >> a & 1) * (column >> b & 1)
                                 for column in columns) % 2
                             for a, b in ((0, 1), (0, 2), (1, 2)))
            if pairings != (1, 0, 0):
                continue
            index = sum((weight // 2 % 2) << bit
                        for bit, weight in enumerate(weights))
            multiplicity = math.factorial(width)
            for value in range(8):
                multiplicity //= math.factorial(columns.count(value))
            table[index] += multiplicity
        counts.append(table)
    require(candidates == 3003, "incomplete column census")
    return counts, candidates


def minimum_and_witness(phases):
    first, second, radical = phases
    if radical:
        return 5, (15 ^ (3 * first), 23 ^ (3 * second), 3)
    if first == second == 1:
        return 4, (3, 5, 15)
    if first:
        return 6, (24, 23, 57)
    if second:
        return 6, (15, 24, 57)
    return 6, (15, 23, 57)


def rejection_controls():
    fixtures = (
        ((0, 0, 0), 4, (3, 5, 15)),
        ((1, 1, 1), 4, (3, 5, 15)),
        ((1, 1, 0), 4, (3, 5, 0)),
        ((1, 1, 0), 4, (3, 5, 6)),
        ((1, 1, 0), 6, (3, 12, 39)),
        ((1, 1, 0), 4, (3, 5, 7)),
        ((0, 0, 0), 5, (15, 23, 57)),
        ((0, 0, 0), 7, (15, 23, 57)),
        ((0, 0, 2), 6, (15, 23, 57)),
        ((0, 0), 6, (15, 23, 57)),
        ((0, 0, 0), 6, (15, 23)),
        ((0, 0, 0), 6, (15, 23, -1)),
    )
    for phases, width, rows in fixtures:
        try:
            validate_embedding(phases, width, rows)
        except ValueError:
            continue
        raise ValueError("accepted a rejecting fixture")
    return len(fixtures)


def file_hashes():
    root = Path(__file__).resolve().parent
    result = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py"):
        with (root / name).open("rb") as source:
            data = source.read(131073)
        require(len(data) <= 131072, "receipt file exceeds 128 KiB")
        result[name] = hashlib.sha256(data).hexdigest()
    return result


def main():
    rows, row_candidates = row_census()
    columns, column_candidates = column_census()
    require(rows == columns, "independent census disagreement")
    results = []
    for phases in itertools.product(range(2), repeat=3):
        index = sum(value << bit for bit, value in enumerate(phases))
        minimum, witness = minimum_and_witness(phases)
        observed = next(width for width in range(7) if rows[width][index])
        require(observed == minimum, "incorrect minimum")
        validate_embedding(phases, minimum, witness)
        results.append({"phases": phases, "minimum": minimum,
                        "witness": witness,
                        "embeddings_by_width": [table[index] for table in rows]})
    receipt = {"result": "PASS_QUADRATIC_HYPERBOLIC_RADICAL_WIDTH",
               "row_candidates": row_candidates,
               "column_multisets": column_candidates,
               "ordered_embeddings": sum(map(sum, rows)),
               "minimum_cases": len(results), "results": results,
               "rejection_controls": rejection_controls(),
               "package_sha256": file_hashes()}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

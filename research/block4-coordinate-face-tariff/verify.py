#!/usr/bin/env python3
"""Exact block-four face certificate, with no external mathematical inputs."""

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
import sys

PRIME = 65537
ROOT_I = 256
DEGREE = 5
ADDRESSES = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def face_of(subset):
    faces = [(bit, (subset[0] >> bit) & 1) for bit in range(4)
             if all(((x >> bit) & 1) == ((subset[0] >> bit) & 1)
                    for x in subset)]
    require(len(faces) <= 1, "five distinct points cannot share two faces")
    return faces[0] if faces else None


def face_basis():
    basis = tuple(combinations(range(ADDRESSES), DEGREE))
    inside = tuple(s for s in basis if face_of(s) is not None)
    require(len(basis) == 4368 and len(inside) == 448, "basis dimensions")
    for bit in range(4):
        for value in range(2):
            require(sum(face_of(s) == (bit, value) for s in inside) == 56,
                    "face dimension")
    return basis, inside


def determinant(matrix):
    """Fraction-free integer elimination, on matrices of size at most five."""
    size = len(matrix)
    require(1 <= size <= DEGREE and all(len(r) == size for r in matrix),
            "determinant dimensions")
    a = [list(row) for row in matrix]
    sign, previous = 1, 1
    for col in range(size - 1):
        pivot = next((r for r in range(col, size) if a[r][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            sign = -sign
        entry = a[col][col]
        for row in range(col + 1, size):
            for j in range(col + 1, size):
                value = a[row][j] * entry - a[row][col] * a[col][j]
                require(value % previous == 0, "Bareiss exact division")
                a[row][j] = value // previous
            a[row][col] = 0
        previous = entry
    return sign * a[-1][-1]


def target_compression(inside):
    """All 448-by-448 compression entries, each a fifth Walsh minor."""
    walsh = [[1 if (x & y).bit_count() % 2 == 0 else -1
              for y in range(ADDRESSES)] for x in range(ADDRESSES)]
    for x in range(ADDRESSES):
        for y in range(ADDRESSES):
            require(sum(walsh[z][x] * walsh[z][y]
                        for z in range(ADDRESSES)) == (16 if x == y else 0),
                    "Walsh unitarity")
    rows = []
    for target in inside:
        row = {}
        for j, source in enumerate(inside):
            value = determinant([[walsh[x][y] for y in source] for x in target])
            if value:
                row[j] = value
                require(face_of(target)[0] == face_of(source)[0],
                        "cross-face compression must vanish")
        rows.append(row)
    return rows


def gram(rows, size, gaussian=False):
    result = [{} for _ in range(size)]
    for row in rows:
        for j, left in row.items():
            for k, right in row.items():
                if gaussian:
                    value = (left[0] * right[0] + left[1] * right[1],
                             left[0] * right[1] - left[1] * right[0])
                    old = result[j].get(k, (0, 0))
                    result[j][k] = (old[0] + value[0], old[1] + value[1])
                else:
                    result[j][k] = result[j].get(k, 0) + left * right
    zero = (0, 0) if gaussian else 0
    return [{k: v for k, v in row.items() if v != zero} for row in result]


def check_scalar_gram(rows, size, scalar, gaussian=False):
    actual = gram(rows, size, gaussian)
    for j, row in enumerate(actual):
        require(row == {j: (scalar, 0) if gaussian else scalar},
                "compression Gram identity")


def gaussian_product(left, right):
    return (left[0] * right[0] - left[1] * right[1],
            left[0] * right[1] + left[1] * right[0])


def call_columns(inside, direction):
    """Expand wedge^5(2 C_v) using each of the 32 choices per column."""
    require(1 <= direction < ADDRESSES, "nonzero direction")
    coefficients = []
    for mask in range(1 << DEGREE):
        value = (1, 0)
        for bit in range(DEGREE):
            value = gaussian_product(value, (1, -1) if mask >> bit & 1 else (1, 1))
        coefficients.append(value)
    columns = []
    for source in inside:
        column = {}
        for mask, value in enumerate(coefficients):
            points = tuple(x ^ (direction if mask >> j & 1 else 0)
                           for j, x in enumerate(source))
            if len(set(points)) < DEGREE:
                continue
            inversions = sum(points[j] > points[k] for j in range(DEGREE)
                             for k in range(j + 1, DEGREE))
            sign = -1 if inversions % 2 else 1
            target = tuple(sorted(points))
            old = column.get(target, (0, 0))
            column[target] = (old[0] + sign * value[0], old[1] + sign * value[1])
        columns.append({s: v for s, v in column.items() if v != (0, 0)})
    return columns


def columns_to_rows(columns):
    rows = {}
    for j, column in enumerate(columns):
        for target, value in column.items():
            rows.setdefault(target, {})[j] = value
    return rows


def modular_rank(columns, row_ids):
    require(PRIME == 65537 and ROOT_I * ROOT_I % PRIME == PRIME - 1,
            "Gaussian residue embedding")
    pivots = {}
    for column in columns:
        current = {row_ids[s]: (a + ROOT_I * b) % PRIME
                   for s, (a, b) in column.items() if (a + ROOT_I * b) % PRIME}
        for _ in range(len(columns) + 1):
            if not current:
                break
            lead = min(current)
            if lead not in pivots:
                inverse = pow(current[lead], -1, PRIME)
                pivots[lead] = {r: v * inverse % PRIME for r, v in current.items()}
                break
            factor = current[lead]
            for row, value in pivots[lead].items():
                updated = (current.get(row, 0) - factor * value) % PRIME
                if updated:
                    current[row] = updated
                else:
                    current.pop(row, None)
        else:
            raise ValueError("elimination exceeded the column bound")
    return len(pivots)


def check_call(inside, outside_ids, direction):
    columns = call_columns(inside, direction)
    rows = columns_to_rows(columns)
    check_scalar_gram(rows.values(), len(inside), 1024, gaussian=True)
    leakage = [{s: value for s, value in c.items() if s in outside_ids}
               for c in columns]
    unaffected = [j for j, s in enumerate(inside)
                  if not (direction >> face_of(s)[0]) & 1]
    require(all(not leakage[j] for j in unaffected), "unaffected faces are kept")
    upper = len(inside) - len(unaffected)
    require(upper == 112 * direction.bit_count(), "direction-weight upper bound")
    lower = modular_rank(leakage, outside_ids)
    require(lower == upper, "sharp call rank")
    return lower


def expect_rejection(function):
    try:
        function()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def controls(compression, ranks):
    controls_run = 0
    for wrong in (0, 65535, 65537, 1048576):
        expect_rejection(lambda: check_scalar_gram(compression, 448, wrong))
        controls_run += 1
    corrupted = [dict(row) for row in compression]
    key = next(iter(corrupted[0]))
    corrupted[0][key] += 1
    expect_rejection(lambda: check_scalar_gram(corrupted, 448, 65536))
    controls_run += 1
    expect_rejection(lambda: call_columns((), 0))
    controls_run += 1
    for direction in (3, 7, 15):
        expect_rejection(lambda: require(ranks[str(direction)] <= 112,
                                        "diagonal call is not an axis call"))
        controls_run += 1
    return controls_run


def scientific_result():
    require(sys.version_info >= (3, 12), "Python 3.12 or later required")
    require(all(PRIME % d for d in range(2, 257)), "residue modulus is prime")
    basis, inside = face_basis()
    inside_set = set(inside)
    outside_ids = {s: j for j, s in enumerate(s for s in basis if s not in inside_set)}
    compression = target_compression(inside)
    check_scalar_gram(compression, 448, 65536)
    ranks = {str(v): check_call(inside, outside_ids, v) for v in range(1, 16)}
    require(max(ranks.values()) == 448, "no useful uniform call cap here")
    return {"claim_type": "scoped proof with exact finite certificate",
            "dimension": len(basis), "face_dimension": len(inside),
            "target_compression_scale": 1024, "compression_gram": 65536,
            "leakage_gram": "15/16 I_448", "target_demand": 448,
            "call_ranks": ranks, "controls": controls(compression, ranks),
            "target_minors_checked": len(inside) ** 2}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = scientific_result()
    package = Path(__file__).resolve().parent
    result["source_sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in ("verify.py", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")}
    payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt is not None:
        require(not args.receipt.resolve().is_relative_to(package.parent.parent),
                "receipt must be outside the checkout")
        with args.receipt.open("x", encoding="utf-8") as stream:
            require(stream.write(payload) == len(payload), "complete receipt write")
    print("PASS_BLOCK4_COORDINATE_FACE_TARIFF " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

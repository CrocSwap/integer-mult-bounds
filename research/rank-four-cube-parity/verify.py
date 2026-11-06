#!/usr/bin/env python3
"""Exact finite certificate for a rank-four cube/parity obstruction.

Produced by Nick Petalas. Apache-2.0.
"""

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def construction():
    signs = tuple((1, *tail) for tail in itertools.product((1, -1), repeat=3))
    columns = signs + ((1, 1, 0, 0), (1, 0, 1, 0))
    rows = tuple(tuple(column[i] for column in columns) for i in range(4))
    doubled_h = tuple(sum(row[j] for row in rows) for j in range(10))
    require(all(value % 2 == 0 for value in doubled_h), "nonintegral h")
    h = tuple(value // 2 for value in doubled_h)
    return rows, h, rows[:3] + (h,)


def determinant(matrix):
    size = len(matrix)
    require(1 <= size <= 4, "determinant size outside certificate")
    require(all(len(row) == size for row in matrix), "nonsquare matrix")
    result = 0
    for permutation in itertools.permutations(range(size)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(size) for j in range(i + 1, size))
        term = (-1) ** inversions
        for i in range(size):
            term *= matrix[i][permutation[i]]
        result += term
    return result


def rank_mod_two(rows):
    require(1 <= len(rows) <= 5, "binary row count outside certificate")
    require(all(len(row) == 10 for row in rows), "binary width is not ten")
    packed = [sum((value % 2) << j for j, value in enumerate(row))
              for row in rows]
    rank = 0
    for column in range(10):
        pivot = next((i for i in range(rank, len(packed))
                      if (packed[i] >> column) & 1), None)
        if pivot is None:
            continue
        packed[rank], packed[pivot] = packed[pivot], packed[rank]
        for i in range(rank + 1, len(packed)):
            if (packed[i] >> column) & 1:
                packed[i] ^= packed[rank]
        rank += 1
    return rank


def minor_data(rows):
    divisor = 0
    histogram = {}
    for columns in itertools.combinations(range(10), 4):
        minor = tuple(tuple(row[j] for j in columns) for row in rows)
        value = determinant(minor)
        histogram[value] = histogram.get(value, 0) + 1
        divisor = math.gcd(divisor, value)
    require(sum(histogram.values()) == 210, "incomplete minor census")
    return {"gcd": divisor, "histogram": dict(sorted(histogram.items()))}


def inverse_unimodular(matrix):
    det = determinant(matrix)
    require(abs(det) == 1, "pivot is not unimodular")
    inverse = []
    for i in range(4):
        row = []
        for j in range(4):
            minor = tuple(tuple(matrix[a][b] for b in range(4) if b != i)
                          for a in range(4) if a != j)
            row.append(((-1) ** (i + j)) * determinant(minor) // det)
        inverse.append(tuple(row))
    for i in range(4):
        for j in range(4):
            require(sum(matrix[i][a] * inverse[a][j] for a in range(4))
                    == int(i == j), "incorrect inverse")
    return tuple(inverse)


def combine(coefficients, rows):
    require(len(coefficients) == len(rows) == 4, "combination size")
    return tuple(sum(coefficients[i] * rows[i][j] for i in range(4))
                 for j in range(10))


def ambient_cube_census(basis):
    # A unit pivot makes membership in the full rational row space exact.
    pivot = (0, 1, 8, 9)
    inverse = inverse_unimodular(tuple(tuple(row[j] for j in pivot)
                                      for row in basis))
    members = []
    checked = 0
    for vector in itertools.product((-1, 0, 1), repeat=10):
        checked += 1
        coefficients = tuple(sum(vector[pivot[j]] * inverse[j][i]
                                 for j in range(4)) for i in range(4))
        if combine(coefficients, basis) == vector:
            members.append(vector)
    require(checked == 59049, "incomplete ambient cube")
    return checked, tuple(members)


def half_integral_census(rows):
    # This second domain uses the proved lattice parameterization. It does
    # not replace the independent enumeration of the entire ambient cube.
    bounded = []
    checked = 0
    eligible = 0
    for numerator in itertools.product(range(-4, 5), repeat=4):
        checked += 1
        if len({value % 2 for value in numerator}) != 1:
            continue
        eligible += 1
        doubled = combine(numerator, rows)
        require(all(value % 2 == 0 for value in doubled), "lattice failure")
        vector = tuple(value // 2 for value in doubled)
        if max(map(abs, vector)) <= 2:
            bounded.append((numerator, vector))
    require((checked, eligible) == (6561, 881), "incomplete coefficient box")
    require(len(bounded) == 57, "height-two count")
    missing = [vector for numerator, vector in bounded if numerator[0] % 2]
    require(len(missing) == 16, "missing-coset count")
    require(all(max(map(abs, vector)) == 2 for vector in missing),
            "a missing-coset representative fits in the cube")
    return {"box_points": checked, "lattice_points_in_box": eligible,
            "height_at_most_two": len(bounded),
            "missing_coset_at_height_two": len(missing)}


def omission_controls(rows):
    # Each deleted sign column admits an explicit cube vector from the
    # otherwise excluded half-integral coefficient coset.
    controls = []
    for removed in range(8):
        numerator = tuple(row[removed] for row in rows)
        doubled = combine(numerator, rows)
        require(all(value % 2 == 0 for value in doubled), "nonintegral control")
        witness = tuple(value // 2 for value in doubled)
        require(witness[removed] == 2, "control fails to detect omitted column")
        require(all(abs(witness[j]) <= 1 for j in range(10) if j != removed),
                "control still exceeds cube after column omission")
        controls.append({"removed_column": removed, "witness": witness})
    return controls


def certificate():
    rows, h, basis = construction()
    row_minors, basis_minors = minor_data(rows), minor_data(basis)
    require((row_minors["gcd"], basis_minors["gcd"]) == (2, 1),
            "wrong saturation index")
    checked, members = ambient_cube_census(basis)
    expected = {(0,) * 10}
    for row in rows:
        expected.add(row)
        expected.add(tuple(-value for value in row))
    require(set(members) == expected, "cube intersection is not zero and ±rows")
    require(rank_mod_two(rows) == 3, "cube parity rank")
    require(rank_mod_two(basis) == 4, "full lattice parity rank")
    require(rank_mod_two(rows + (h,)) == 4, "missing class is not missing")
    require(max(map(abs, h)) == 2, "sharp height-two witness")
    return {"status": "PASS_RANK_FOUR_CUBE_PARITY", "rows": rows,
            "saturated_basis": basis, "missing_class_witness": h,
            "ambient_cube_vectors_checked": checked, "cube_members": members,
            "nonzero_cube_members": len(members) - 1,
            "cube_parity_rank": 3, "lattice_parity_rank": 4,
            "cube_generated_index": 2, "missing_coset_minimum_height": 2,
            "row_minors": row_minors, "basis_minors": basis_minors,
            "coefficient_census": half_integral_census(rows),
            "sign_column_omission_controls": omission_controls(rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path,
                        help="write a generated hash-bound receipt outside the package")
    args = parser.parse_args()
    result = certificate()
    if args.receipt is not None:
        package = Path(__file__).resolve().parent
        destination = args.receipt.resolve()
        require(not destination.is_relative_to(package), "receipt must be external")
        names = ("verify.py", "PROOF.md", "README.md", "TASK.json",
                 "SOURCES.json", "VERIFY.json")
        hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                  for name in names}
        receipt = {"schema": "rank-four-cube-parity-receipt-v1",
                   "source_sha256": hashes, "certificate": result,
                   "environment": {"python": sys.version,
                                   "executable": sys.executable,
                                   "platform": platform.platform()}}
        args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

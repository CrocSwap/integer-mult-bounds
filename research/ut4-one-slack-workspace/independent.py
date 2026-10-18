#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Faithful active-corner compression checks with literal UT4 matrices.

No primary or predecessor executable is imported. The checks concern
common triangular orientation, not attainment by a 14/15-call word.
"""
import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

EDGES = ((0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3))
LETTER_CODES = {"a": 1, "b": 2, "c": 4}
ADDRESS_MASK = (1 << 64) - 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def literal_matrix(code):
    require(type(code) is int and 0 <= code < 64, "invalid UT4 address")
    matrix = [[int(i == j) for j in range(4)] for i in range(4)]
    for bit, (i, j) in enumerate(EDGES):
        matrix[i][j] = (code >> bit) & 1
    return matrix


def multiply_addresses(left, right):
    a, b = literal_matrix(left), literal_matrix(right)
    product = [[sum(a[i][k] * b[k][j] for k in range(4)) % 2
                for j in range(4)] for i in range(4)]
    require(all(product[i][i] == 1 and all(product[i][j] == 0 for j in range(i))
                for i in range(4)), "literal product leaves UT4")
    return sum(product[i][j] << bit for bit, (i, j) in enumerate(EDGES))


@lru_cache(maxsize=None)
def address_permutation(code):
    image = tuple(multiply_addresses(code, h) for h in range(64))
    require(len(set(image)) == 64, "left-regular address action is not a permutation")
    return image


def paid_factors(word, r):
    require(type(r) is int and r >= 1, "positive integer role count required")
    checked = []
    for factor in word:
        require(isinstance(factor, (tuple, list)) and len(factor) == 3,
                "factor must have letter,x,y")
        letter, x, y = factor
        require(letter in LETTER_CODES, "unknown paid letter")
        require(type(x) is int and type(y) is int and 0 < x < (1 << r) and 0 < y < (1 << r),
                "coupling must use two nonzero r-bit vectors")
        checked.append((letter, x, y))
    return checked


def regular_columns(word, r):
    """Return all 64r operator columns, role-major then group-code order."""
    factors = paid_factors(word, r)
    result = []
    for column in range(64 * r):
        state = 1 << column
        for letter, x, y in reversed(factors):
            source = 0
            for role in range(r):
                if (y >> role) & 1:
                    source ^= (state >> (64 * role)) & ADDRESS_MASK
            translated = 0
            remaining, image = source, address_permutation(LETTER_CODES[letter])
            while remaining:
                bit = remaining & -remaining
                translated ^= 1 << image[bit.bit_length() - 1]
                remaining ^= bit
            update = source ^ translated
            for role in range(r):
                if (x >> role) & 1:
                    state ^= update << (64 * role)
        result.append(state)
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify_compression(word, r, w):
    require(type(w) is int and 1 <= w <= r, "target width must satisfy 1<=w<=r")
    factors = paid_factors(word, r)
    all_columns_active = all(x >> w == 0 for _, x, _ in factors)
    all_rows_active = all(y >> w == 0 for _, _, y in factors)
    require(all_columns_active or all_rows_active, "no common triangular orientation")
    mask = (1 << w) - 1
    projected = [(letter, x & mask, y & mask) for letter, x, y in factors if x & mask and y & mask]
    full = regular_columns(factors, r)
    active_mask = (1 << (64 * w)) - 1
    active_corner = [column & active_mask for column in full[:64 * w]]
    compressed = regular_columns(projected, w)
    require(active_corner == compressed, "faithful active corner differs from compressed operator")
    orientation = "both" if all_columns_active and all_rows_active else "columns" if all_columns_active else "rows"
    return {"r": r, "w": w, "input_calls": len(factors), "kept_calls": len(projected),
            "dropped_zero_calls": len(factors) - len(projected),
            "common_orientation": orientation, "active_basis_columns": 64 * w,
            "active_output_rows": 64 * w, "active_corner_sha256": digest(active_corner)}


def self_checks():
    # The known sixteen-call endpoint is a positive fixture, not a new optimum.
    coordinate = [(letter, 1 << role, 1 << role) for role in range(2) for letter in "abcbabcb"]
    target = [1 << (64 * role + address_permutation(32)[h]) if role < 2
              else 1 << (64 * role + h) for role in range(3) for h in range(64)]
    require(regular_columns(coordinate, 3) == target, "coordinate target fixture failed")
    records = [verify_compression(coordinate, 3, 2)]
    # outer(3,3)^2=0; its factor still is an involution and commutes with z on active roles.
    nilpotent = [("b", 3, 3)] + coordinate + [("b", 3, 3)]
    require(regular_columns(nilpotent, 3) == target, "nilpotent active fixture failed")
    records.append(verify_compression(nilpotent, 3, 2))

    upper = [("a", 1, 1), ("b", 2, 2), ("c", 1, 4),
             ("a", 3, 5), ("b", 2, 1), ("c", 2, 2)]
    lower = [(letter, y, x) for letter, x, y in upper]
    records.extend((verify_compression(upper, 3, 2), verify_compression(lower, 3, 2)))
    require(records[-2]["dropped_zero_calls"] == records[-1]["dropped_zero_calls"] == 1,
            "triangular fixtures omit the expected zero projection")

    # Mixed upper/lower factors can feed a dirty role back into the active corner.
    mixed = [("a", 1, 2), ("b", 2, 1)]
    try:
        verify_compression(mixed, 2, 1)
    except ValueError as error:
        require(str(error) == "no common triangular orientation", "mixed fixture failed for another reason")
    else:
        raise ValueError("mixed orientation was accepted")
    full = regular_columns(mixed, 2)
    active = [column & ADDRESS_MASK for column in full[:64]]
    require(active != regular_columns([], 1), "mixed orientation does not exhibit active feedback")

    # Involutions and formal order are checked on all address columns.
    for letter in LETTER_CODES:
        twice = regular_columns([(letter, 3, 5), (letter, 3, 5)], 3)
        require(twice == [1 << i for i in range(192)], "simultaneous rank-one update is not an involution")
    ab = regular_columns([("a", 1, 1), ("b", 1, 1)], 1)
    ab_code = multiply_addresses(1, 2)
    require(ab == [1 << h for h in address_permutation(ab_code)], "factor application order is wrong")
    require(ab != regular_columns([("b", 1, 1), ("a", 1, 1)], 1), "reversed product order control failed")
    return {"schema_version": 1, "method": "literal 4x4 binary matrices and full regular columns",
            "address_bit_positions": [list(edge) for edge in EDGES],
            "basis_order": "64*role+group_code", "positive_compressions": records,
            "mixed_orientation_rejected": True, "mixed_active_feedback_sha256": digest(active),
            "involution_controls": 3, "product_order_controls": 1,
            "scope": "compression fixtures and known16-call endpoint; no14/15-call attainment claim"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, help="compare complete self-check receipt")
    parser.add_argument("--write", type=Path, help="create a fresh receipt; never overwrite")
    args = parser.parse_args()
    try:
        if args.write:
            require(not args.write.exists(), "output already exists")
        receipt = self_checks()
        if args.check:
            require(json.loads(args.check.read_text()) == receipt, "independent receipt differs")
        if args.write:
            with args.write.open("x") as stream:
                json.dump(receipt, stream, indent=2, sort_keys=True)
                stream.write("\n")
    except (ValueError, OSError) as error:
        parser.exit(1, "FAIL_UT4_ONE_SLACK_INDEPENDENT: " + str(error) + "\n")
    print("PASS_UT4_ONE_SLACK_INDEPENDENT positive_compressions=4 "
          "mixed_orientation_control=1 involutions=3 product_order=1")


if __name__ == "__main__":
    main()

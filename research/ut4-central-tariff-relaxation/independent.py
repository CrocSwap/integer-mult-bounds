#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Faithful left-regular UT4(F2) checker using literal binary matrices.

Address bits are (01,12,23,02,13,03). Role-major basis columns have
index 64*role+group_code. A formal product F1...Fn applies its factors
in reverse order to each column. No predecessor or primary code is used.
"""
import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

POSITIONS = ((0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3))
LETTERS = {"a": 1, "b": 2, "c": 4}
MASK64 = (1 << 64) - 1
HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def address_matrix(code):
    require(type(code) is int and 0 <= code < 64, "address code outside 0..63")
    rows = [[int(i == j) for j in range(4)] for i in range(4)]
    for bit, (i, j) in enumerate(POSITIONS):
        rows[i][j] = (code >> bit) & 1
    return tuple(tuple(row) for row in rows)


def matrix_code(matrix):
    require(len(matrix) == 4 and all(len(row) == 4 for row in matrix), "address matrix is not four by four")
    require(all(value in (0, 1) for row in matrix for value in row), "address matrix is not binary")
    require(all(matrix[i][i] == 1 and all(matrix[i][j] == 0 for j in range(i))
                for i in range(4)), "address matrix is not upper unitriangular")
    return sum(matrix[i][j] << bit for bit, (i, j) in enumerate(POSITIONS))


def matrix_product(left, right):
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(4)) % 2
                       for j in range(4)) for i in range(4))


@lru_cache(maxsize=1)
def _table():
    matrices = [address_matrix(code) for code in range(64)]
    return tuple(tuple(matrix_code(matrix_product(left, right)) for right in matrices)
                 for left in matrices)


def group_multiplication_table():
    """Return [left_code][right_code], computed by literal matrix products."""
    return [list(row) for row in _table()]


def permute_address_bits(bits, left_code):
    """Left multiplication sends basis address h to left_code*h."""
    require(0 <= bits <= MASK64, "address vector exceeds 64 bits")
    image, permutation = 0, _table()[left_code]
    while bits:
        bit = bits & -bits
        address = bit.bit_length() - 1
        image ^= 1 << permutation[address]
        bits ^= bit
    return image


def validate_word(word, roles):
    require(type(roles) is int and roles >= 1, "positive integer role count required")
    encoded = []
    for factor in word:
        require(isinstance(factor, (tuple, list)) and len(factor) == 3, "factor must be (letter,x,y)")
        letter, x, y = factor
        require(letter in LETTERS, "factor letter outside a,b,c")
        require(type(x) is int and type(y) is int and 0 < x < (1 << roles) and 0 < y < (1 << roles),
                "rank-one coupling vectors must be nonzero role masks")
        encoded.append((LETTERS[letter], x, y))
    return encoded


def _factor(state, left_code, x, y, roles):
    # The source must be gathered before any target role is changed.
    source = 0
    for role in range(roles):
        if (y >> role) & 1:
            source ^= (state >> (64 * role)) & MASK64
    delta = source ^ permute_address_bits(source, left_code)
    out = state
    for role in range(roles):
        if (x >> role) & 1:
            out ^= delta << (64 * role)
    return out


def regular_columns(word, r):
    """Full columns of product I+(I+L_letter) tensor (x y^T).

    The register vector is over F2, including arbitrary initial dirty roles.
    Idempotent and nilpotent rank-one couplings use the same exact routine.
    """
    factors = validate_word(word, r)
    columns = []
    for column in range(64 * r):
        state = 1 << column
        for left_code, x, y in reversed(factors):
            state = _factor(state, left_code, x, y, r)
        columns.append(state)
    return columns


def binary_rank(columns):
    pivots = {}
    for vector in columns:
        while vector:
            pivot = vector & -vector
            if pivot in pivots:
                vector ^= pivots[pivot]
            else:
                pivots[pivot] = vector
                break
    return len(pivots)


def apply_columns(columns, vector):
    require(vector >= 0 and vector.bit_length() <= len(columns), "test vector is outside the operator domain")
    image = 0
    while vector:
        bit = vector & -vector
        image ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return image


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def self_checks():
    table = group_multiplication_table()
    require([matrix_code(address_matrix(code)) for code in range(64)] == list(range(64)),
            "matrix-code roundtrip differs")
    require(all(table[0][code] == table[code][0] == code for code in range(64)), "identity law fails")
    require(all(len(set(row)) == 64 for row in table), "left multiplication is not bijective")
    require(all(len({table[left][right] for left in range(64)}) == 64 for right in range(64)),
            "right multiplication is not bijective")
    # Every matrix associativity case is cheap at this fixed group order.
    require(all(table[table[a][b]][c] == table[a][table[b][c]]
                for a in range(64) for b in range(64) for c in range(64)), "associativity law fails")
    require(all(table[g][g] == 0 for g in (*LETTERS.values(), 32)), "generator or centre is not an involution")
    require(all(table[32][code] == table[code][32] for code in range(64)), "z is not central")
    require(table[1][2] != table[2][1], "adjacent generators unexpectedly commute")

    fixtures = [(1, 1, 1)]
    fixtures.extend((2, x, y) for x in range(1, 4) for y in range(1, 4))
    fixtures.extend(((3, 1, 2), (3, 7, 5), (5, 1, 16), (5, 21, 22)))
    fixture_rows = []
    for roles, x, y in fixtures:
        coupling_columns = [x if (y >> column) & 1 else 0 for column in range(roles)]
        require(binary_rank(coupling_columns) == 1, "nonzero outer product lacks rank one")
        nilpotent = bin(x & y).count("1") % 2 == 0
        for letter, code in LETTERS.items():
            columns = regular_columns([(letter, x, y)], roles)
            update_columns = [image ^ (1 << column) for column, image in enumerate(columns)]
            require(binary_rank(update_columns) == 32, "rank-one generator update does not have rank 32")
            require(binary_rank(columns) == 64 * roles, "factor is not invertible")
            twice = regular_columns([(letter, x, y), (letter, x, y)], roles)
            require(twice == [1 << column for column in range(64 * roles)], "factor is not an involution")
            # On a single source address, the update has exactly the stated two addresses in each x-role.
            source_role = next(role for role in range(roles) if (y >> role) & 1)
            input_column = 64 * source_role
            expected = 1 << input_column
            for role in range(roles):
                if (x >> role) & 1:
                    expected ^= (1 << (64 * role)) | (1 << (64 * role + code))
            require(columns[input_column] == expected, "literal source-address factor check fails")
            fixture_rows.append({"r": roles, "letter": letter, "x": x, "y": y,
                                 "nilpotent": nilpotent, "update_rank": 32,
                                 "columns_sha256": digest(columns)})

    # Product order is visible on the identity address: formal ab acts as a*b.
    ab = regular_columns([("a", 1, 1), ("b", 1, 1)], 1)
    require(ab == [1 << table[table[1][2]][h] for h in range(64)], "formal product applies in the wrong order")
    require(ab != regular_columns([("b", 1, 1), ("a", 1, 1)], 1), "order mutation is not detected")

    # One nonzero common-kernel vector cannot certify equality of regular operators.
    common_kernel = sum(1 << code for code in (0, 1, 32, table[32][1]))
    a_columns = regular_columns([("a", 1, 1)], 1)
    z_columns = [1 << table[32][h] for h in range(64)]
    require(apply_columns(a_columns, common_kernel) == common_kernel
            == apply_columns(z_columns, common_kernel), "common-kernel fixture changed")
    require(a_columns != z_columns and a_columns[0] == (1 << 1) and z_columns[0] == (1 << 32),
            "faithful columns do not distinguish the common-kernel operators")
    return {"schema_version": 1, "method": "literal binary 4x4 matrices and faithful left-regular columns",
            "group_order": 64, "group_products_checked": 4096, "associativity_cases": 262144,
            "multiplication_table_sha256": digest(table), "role_order": "64*role+group_code",
            "address_bit_positions": [list(pair) for pair in POSITIONS],
            "factor_order": "reverse the formal word when applying columns",
            "factor_fixtures": fixture_rows, "fixture_count": len(fixture_rows),
            "common_kernel_address_mask": common_kernel,
            "common_kernel_scope": "a and z agree on (1+z)(1+a), but their full regular operators differ"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, help="compare complete finite self-check receipt")
    parser.add_argument("--write", type=Path, help="create a fresh self-check receipt, never overwrite")
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
        parser.exit(1, "FAIL_UT4_CENTRAL_TARIFF_INDEPENDENT: " + str(error) + "\n")
    print("PASS_UT4_CENTRAL_TARIFF_INDEPENDENT group_products=4096 "
          f"factor_fixtures={receipt['fixture_count']} faithful_common_kernel_control=1")


if __name__ == "__main__":
    main()

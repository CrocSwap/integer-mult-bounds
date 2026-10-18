# SPDX-License-Identifier: Apache-2.0
"""Audit the published inverse with integer Laurent identities and unit divisors.

The inverse is Sagar Thakrar's PR3297 result. This is a separate implementation
of its certificate check, not an independent discovery of that inverse.
"""

from source import require

DIMENSION = 20
ZERO = (0,) * DIMENSION
MAX_TERMS = 256
ONE = {ZERO: 1}


def variable(index: int) -> dict:
    return {tuple(int(j == index) for j in range(DIMENSION)): 1}


def add(left: dict, right: dict, sign: int = 1) -> dict:
    result = dict(left)
    for exponent, coefficient in right.items():
        result[exponent] = result.get(exponent, 0) + sign * coefficient
    result = {key: value for key, value in result.items() if value}
    require(len(result) <= MAX_TERMS, "Laurent sum capacity")
    return result


def multiply(left: dict, right: dict) -> dict:
    require(len(left) * len(right) <= MAX_TERMS * MAX_TERMS, "Laurent product capacity")
    result = {}
    for a, x in left.items():
        for b, y in right.items():
            exponent = tuple(i + j for i, j in zip(a, b, strict=True))
            result[exponent] = result.get(exponent, 0) + x * y
    result = {key: value for key, value in result.items() if value}
    require(len(result) <= MAX_TERMS, "Laurent output capacity")
    return result


def quotient(numerator: dict, denominator: dict, divisions: list) -> dict:
    require(len(denominator) == 1, "denominator is not a nonzero monomial")
    powers, coefficient = next(iter(denominator.items()))
    require(coefficient in (-1, 1), "denominator coefficient is not an integer unit")
    divisions.append([list(powers), coefficient])
    return {tuple(a - b for a, b in zip(key, powers, strict=True)): value * coefficient
            for key, value in numerator.items()}


def polynomial_entries(rows: list) -> list:
    require(len(rows) <= 256, "matrix term bound")
    matrix = [[{} for _ in range(8)] for _ in range(8)]
    for row, column, mask, ambient, coefficient in rows:
        require(0 <= row < 8 and 0 <= column < 8 and 0 <= mask < 1 << DIMENSION,
                "matrix term range")
        require(ambient in (0, -1) and type(coefficient) is int, "matrix coefficient/phase")
        # Remove the common nonzero g from an odd-row/even-column entry.
        require(ambient == (-1 if row % 2 and column % 2 == 0 else 0), "ambient entry pattern")
        exponent = tuple(mask >> i & 1 for i in range(DIMENSION))
        matrix[row][column] = add(matrix[row][column], {exponent: coefficient})
    return matrix


def recover(matrix: list) -> tuple[list, list]:
    """Substitute the exact map into PR3297's stated triangular inverse."""
    m, z, divisions = matrix, [{} for _ in range(DIMENSION)], []

    def divide(a: dict, b: dict) -> dict:
        return quotient(a, b, divisions)

    z[13], z[12] = m[0][0], m[1][1]
    z[0] = divide(add(m[0][2], m[2][2]), z[13])
    z[1] = add(ONE, divide(m[1][2], multiply(z[0], z[12])))
    z[15] = divide(m[2][2], multiply(z[0], z[1]))
    u = add(z[12], m[3][1], -1)
    z[14] = add(m[3][0], u)
    z[3], z[2] = divide(u, z[14]), divide(m[3][3], u)
    z[4] = divide(add(m[4][4], m[0][4], -1), z[15])
    z[5] = add(ONE, divide(m[3][4], multiply(z[4], z[14])))
    z[17] = divide(m[4][4], multiply(z[4], z[5]))
    p = add(divide(m[5][1], z[3]), z[14])
    z[16] = divide(add(add(divide(m[5][2], z[0]),
                          multiply(z[14], add(ONE, z[1], -1)), -1), p), z[1])
    z[7], z[6] = divide(p, z[16]), divide(m[5][5], p)
    z[8] = divide(add(m[0][6], m[6][6]), z[17])
    z[9] = add(ONE, divide(m[5][6], multiply(z[8], z[16])))
    z[19] = divide(m[6][6], multiply(z[8], z[9]))
    p = add(z[16], divide(m[7][1], multiply(z[3], z[7])), -1)
    z[18] = divide(add(add(divide(m[7][4], z[4]),
                          multiply(z[16], add(ONE, z[5], -1)), -1), p), z[5])
    z[11], z[10] = divide(p, z[18]), divide(m[7][7], p)
    require(z == [variable(i) for i in range(DIMENSION)], "inverse coordinate identity")
    return z, divisions


def certify(rows: list) -> dict:
    matrix = polynomial_entries(rows)
    _, divisions = recover(matrix)
    require(all(sum(entry.values()) == int(i == j)
                for i, row in enumerate(matrix) for j, entry in enumerate(row)), "baseline identity")
    return {"coordinates": DIMENSION, "unit_divisions": divisions,
            "all_denominators_are_integer_unit_monomials": True}

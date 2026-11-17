#!/usr/bin/env python3
"""Finite exact corroboration for the Phi3/Phi5 no-mixing proof.

Produced by Nick Petalas. Apache-2.0.
The all-width statement is proved in PROOF.md, not by this finite census.
"""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import platform


ZERO = (F(0), F(0))
ONE = (F(1), F(0))
PHASES = (ONE, (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1)))
PHI3 = (1, 1, 1)
PHI5 = (1, 1, 1, 1, 1)
PRODUCT = (1, 2, 3, 3, 3, 2, 1)
MAX_QUBITS = 18


def require(condition, message):
    if not condition:
        raise ValueError(message)


def plus(a, b):
    return (a[0] + b[0], a[1] + b[1])


def times(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def identity(size):
    require(1 <= size <= 8, "matrix capacity")
    return tuple(tuple(ONE if i == j else ZERO for j in range(size))
                 for i in range(size))


def multiply(a, b):
    size = len(a)
    require(1 <= size <= 8 and len(b) == size, "matrix dimensions")
    require(all(len(row) == size for row in a + b), "square matrices")
    result = [[ZERO] * size for _ in range(size)]
    for i in range(size):
        for k in range(size):
            if a[i][k] == ZERO:
                continue
            for j in range(size):
                result[i][j] = plus(result[i][j], times(a[i][k], b[k][j]))
    return tuple(tuple(row) for row in result)


def adjoint(a):
    return tuple(tuple((a[j][i][0], -a[j][i][1]) for j in range(len(a)))
                 for i in range(len(a)))


def polynomial(coefficients, a):
    require(1 <= len(coefficients) <= 16, "polynomial capacity")
    size = len(a)
    result = tuple(tuple(ZERO for _ in range(size)) for _ in range(size))
    for coefficient in reversed(coefficients):
        result = multiply(result, a)
        result = tuple(tuple(plus(value, (F(coefficient), F(0)))
                             if i == j else value for j, value in enumerate(row))
                       for i, row in enumerate(result))
    return result


def vanishes(coefficients, a):
    return all(value == ZERO for row in polynomial(coefficients, a) for value in row)


def tensor(a, b):
    require(len(a) * len(b) <= 8, "tensor capacity")
    return tuple(tuple(times(a[i][j], b[k][l])
                       for j in range(len(a)) for l in range(len(b)))
                 for i in range(len(a)) for k in range(len(b)))


def direct_sum(blocks):
    size = sum(map(len, blocks))
    require(1 <= size <= 8 and len(blocks) <= 4, "direct sum capacity")
    result = [[ZERO] * size for _ in range(size)]
    offset = 0
    for block in blocks:
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                result[offset + i][offset + j] = value
        offset += len(block)
    require(offset == size, "direct sum endpoint")
    return tuple(tuple(row) for row in result)


def pauli(qubits, x, z):
    require(1 <= qubits <= 3, "Pauli capacity")
    size = 1 << qubits
    require(0 <= x < size and 0 <= z < size, "Pauli label")
    result = [[ZERO] * size for _ in range(size)]
    phase = PHASES[(x & z).bit_count() % 4]
    for column in range(size):
        sign = -1 if (z & column).bit_count() % 2 else 1
        result[column ^ x][column] = (sign * phase[0], sign * phase[1])
    return tuple(tuple(row) for row in result)


def clifford_generator_images(a):
    qubits = len(a).bit_length() - 1
    require(len(a) == 1 << qubits and 1 <= qubits <= 3, "qubit dimension")
    require(multiply(adjoint(a), a) == identity(len(a)), "unitarity")
    signed_paulis = set()
    for x in range(1 << qubits):
        for z in range(1 << qubits):
            p = pauli(qubits, x, z)
            signed_paulis.add(p)
            signed_paulis.add(tuple(tuple((-v[0], -v[1]) for v in row) for row in p))
    results = []
    for bit in range(qubits):
        for x, z in ((1 << bit, 0), (0, 1 << bit)):
            image = multiply(multiply(a, pauli(qubits, x, z)), adjoint(a))
            results.append(image in signed_paulis)
    return results


def power_of_two(value):
    return value > 0 and value & (value - 1) == 0


def multiplicity_census():
    cases = mixed = admissible = 0
    for qubits in range(1, MAX_QUBITS + 1):
        dimension = 1 << qubits
        for quintic in range(dimension // 4 + 1):
            cubic = (dimension - 4 * quintic) // 2
            require(2 * cubic + 4 * quintic == dimension, "dimension equation")
            trace_magnitude = cubic + quintic
            trace_test = power_of_two(trace_magnitude * trace_magnitude)
            endpoint = cubic == 0 or quintic == 0
            require(trace_test == endpoint, "mixed multiplicity passed trace gate")
            if not endpoint:
                require(dimension < 4 * trace_magnitude < 2 * dimension,
                        "strict consecutive-power bracket")
                mixed += 1
            admissible += int(trace_test)
            cases += 1
    return {"maximum_qubits": MAX_QUBITS, "multiplicity_pairs": cases,
            "mixed_pairs_excluded": mixed, "pure_pairs_admitted": admissible}


def fixtures():
    cubic = tuple(tuple((F(r, 2), F(i, 2)) for r, i in row) for row in (
        ((-1, 1), (1, 1)), ((-1, 1), (-1, -1))))
    # The explicit quintic matrix is credited to #6192; it is a test fixture.
    quintic = tuple(tuple((F(r, 2), F(i, 2)) for r, i in row) for row in (
        ((0, -1), (0, -1), (0, -1), (0, -1)),
        ((0, -1), (0, 1), (0, -1), (0, 1)),
        ((1, 0), (-1, 0), (-1, 0), (1, 0)),
        ((1, 0), (1, 0), (-1, 0), (-1, 0))))
    return {"pure_cubic": cubic, "pure_quintic": quintic,
            "mixed_nonclifford": direct_sum((cubic, cubic, quintic)),
            "order_fifteen_clifford": tensor(cubic, quintic)}


def matrix_checks():
    rows = []
    expected = {"pure_cubic": (True, False, True, True),
                "pure_quintic": (False, True, True, True),
                "mixed_nonclifford": (False, False, True, False),
                "order_fifteen_clifford": (False, False, False, True)}
    for name, matrix in fixtures().items():
        images = clifford_generator_images(matrix)
        actual = (vanishes(PHI3, matrix), vanishes(PHI5, matrix),
                  vanishes(PRODUCT, matrix), all(images))
        require(actual == expected[name], "matrix hypothesis control: " + name)
        power = identity(len(matrix))
        exact_order = 0
        for exponent in range(1, 16):
            power = multiply(power, matrix)
            if power == identity(len(matrix)):
                exact_order = exponent
                break
        require(exact_order == {"pure_cubic": 3, "pure_quintic": 5,
                                "mixed_nonclifford": 15,
                                "order_fifteen_clifford": 15}[name], "exact order")
        trace = ZERO
        for i in range(len(matrix)):
            trace = plus(trace, matrix[i][i])
        require(trace[1] == 0 and trace[0].denominator == 1, "integer real trace")
        rows.append({"name": name, "dimension": len(matrix), "trace": int(trace[0]),
                     "exact_order": exact_order, "phi3_zero": actual[0],
                     "phi5_zero": actual[1], "product_zero": actual[2],
                     "pauli_generator_tests": images})
    return rows


def algebra_controls():
    product = [0] * 7
    for i, a in enumerate(PHI3):
        for j, b in enumerate(PHI5):
            product[i + j] += a * b
    require(tuple(product) == PRODUCT, "polynomial convolution")
    require(not power_of_two(0) and not power_of_two(9), "trace rejection controls")
    require(power_of_two(1) and power_of_two(16), "trace acceptance controls")
    # Non-qubit dimension permits both multiplicities through the trace test.
    require(2 * 2 + 4 * 2 == 12 and power_of_two((2 + 2) ** 2),
            "power-of-two dimension premise control")
    for size in (0, 9):
        try:
            identity(size)
        except ValueError as exc:
            require(str(exc) == "matrix capacity", "wrong boundary rejection")
        else:
            raise ValueError("matrix capacity was not enforced")
    return {"convolution": 1, "trace_predicate_controls": 4,
            "nonqubit_arithmetic_control": 1, "capacity_rejections": 2}


def receipt():
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        data = (package / name).read_bytes()
        require(len(data) <= 100000, "package file capacity")
        hashes[name] = sha256(data).hexdigest()
    return {"claim_type": "scoped proof with finite exact corroboration",
            "census": multiplicity_census(), "matrices": matrix_checks(),
            "controls": algebra_controls(), "package_sha256": hashes,
            "python": platform.python_version()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the computed hash-bound receipt")
    args = parser.parse_args()
    result = receipt()
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print(json.dumps(result["census"], sort_keys=True))
        print("PASS_TWO_CYCLOTOMIC_NO_MIXING")


if __name__ == "__main__":
    main()

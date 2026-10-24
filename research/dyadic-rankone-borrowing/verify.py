"""Bounded exact corroboration of the borrowed-hub theorem.

Produced by Nick Petalas. Apache-2.0. No generated files are written.
"""

import hashlib
import json
from fractions import Fraction
from itertools import product
from pathlib import Path
from random import Random

from compiler import allowance, compile_shear, factor, need, validate


def identity(size):
    return [[Fraction(i == j) for j in range(size)] for i in range(size)]


def execute(size, gates):
    rows = identity(size)
    for target, source, coefficient in gates:
        need(target != source, "distinct ADD roles")
        need(0 <= target < size and 0 <= source < size, "existing roles only")
        rows[target] = [x + coefficient * y
                        for x, y in zip(rows[target], rows[source], strict=True)]
    return rows


def expected(matrix):
    n, m = len(matrix[0]), len(matrix)
    result = identity(n + m)
    for j in range(m):
        result[n + j][:n] = list(matrix[j])
    return result


def check_case(raw):
    matrix = validate(raw)
    n, m = len(matrix[0]), len(matrix)
    prep, read, restore = compile_shear(matrix)
    gates = prep + read + restore
    need(execute(n + m, gates) == expected(matrix), "literal dirty shear")
    need(all(i < n and j < n for i, j, _ in prep + restore), "source-only basis")
    need(all(i >= n and j == 0 for i, j, _ in read), "one readout hub")
    need(len(read) == sum(any(row) for row in matrix), "one read per live target")
    factors = factor(matrix)
    if factors is not None:
        a, b = factors
        prepared = execute(n, prep)
        need(prepared[0] == list(b), "hub is primitive source sum")
        need(all(q.denominator == 1 for _, _, q in prep), "integral preparation")
        bill = 2 * sum(allowance(q) for _, _, q in prep)
        bill += sum(allowance(q) for q in a if q)
        need(bill == sum(allowance(q) for _, _, q in gates), "complete invoice")
    return len(gates), sum(allowance(q) for _, _, q in gates)


def no_legal_pivot(matrix):
    matrix = validate(matrix)
    rows = list(matrix)
    columns = list(zip(*matrix, strict=True))
    for values in rows + columns:
        for pivot in values:
            if pivot and all((x / pivot).denominator.bit_count() == 1 for x in values):
                return False
    return True


def expect_reject(raw):
    try:
        compile_shear(raw)
    except (ValueError, TypeError, ZeroDivisionError):
        return
    raise ValueError("invalid input was accepted")


def exhaustive():
    count = 0
    maximum = (0, 0)
    for entries in product(range(-6, 7), repeat=4):
        a, b, c, d = entries
        if a * d != b * c:
            continue
        for denominator in (1, 2, 4):
            matrix = [[Fraction(a, denominator), Fraction(b, denominator)],
                      [Fraction(c, denominator), Fraction(d, denominator)]]
            gates, bill = check_case(matrix)
            maximum = max(maximum, (gates, bill))
            count += 1
    return count, maximum


def wider():
    rng = Random(4502)
    count = 0
    for n in range(1, 9):
        for m in range(1, 9):
            for _ in range(12):
                a = [Fraction(rng.randrange(-31, 32), 1 << rng.randrange(5))
                     for _ in range(m)]
                b = [Fraction(rng.randrange(-31, 32), 1 << rng.randrange(5))
                     for _ in range(n)]
                check_case([[x * y for y in b] for x in a])
                count += 1
    return count


def controls():
    invalid = ([], [[]], [[1], [1, 2]], [[1, 0], [0, 1]], [[Fraction(1, 3)]],
               [[1 << 64]], [[Fraction(1, 1 << 17)]], [[0] * 9], [[0]] * 9)
    for matrix in invalid:
        expect_reject(matrix)
    matrix = [[9, 15], [15, 25]]
    prep, read, restore = compile_shear(matrix)
    target = expected(validate(matrix))
    need(execute(4, prep + read) != target, "missing restoration control")
    need(execute(4, read + restore) != target, "missing preparation control")
    wrong = read[:-1] + ((read[-1][0], 1, read[-1][2]),)
    need(execute(4, prep + wrong + restore) != target, "wrong hub control")
    wrong_restore = tuple((i, j, -q) for i, j, q in prep)
    need(execute(4, prep + read + wrong_restore) != target, "inverse order control")
    need(execute(4, prep + read[:-1] + restore) != target, "missing readout control")
    return len(invalid), 5


def boundaries():
    # Accepted denominator/numerator caps and a long Euclidean quotient chain.
    check_case([[Fraction((1 << 64) - 1, 1 << 16)]])
    check_case([[1, 0, 0, 0, 0, 0, 0, Fraction(1, 1 << 16)]] * 8)
    check_case([[7540113804746346429, 4660046610375530309]])
    return 3


def main():
    fixture = [[9, 15], [15, 25]]
    need(no_legal_pivot(fixture), "fixture outside single-pivot alphabet")
    fixture_gates, fixture_bill = check_case(fixture)
    direct_bill = sum(allowance(q) for row in fixture for q in row)
    need(direct_bill == 76, "literal direct fixture invoice")
    # Triple gcd one despite no unit coordinate and no coprime coordinate pair.
    check_case([[6, 10, 15], [-3, -5, Fraction(-15, 2)]])
    count, maximum = exhaustive()
    wide_count = wider()
    invalid, omissions = controls()
    boundary_count = boundaries()
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "compiler.py", "verify.py", "TASK.json",
                 "SOURCES.json", "VERIFY.json"):
        data = (package / name).read_bytes()
        need(len(data) <= 1 << 20, "bounded package hash input")
        hashes[name] = hashlib.sha256(data).hexdigest()
    receipt = {"schema": "dyadic-rankone-borrowing/v1", "sha256": hashes,
               "exhaustive_2x2_cases": count, "wider_cases": wide_count,
               "invalid_inputs": invalid, "omission_controls": omissions,
               "fixture_gates": fixture_gates, "fixture_allowance": fixture_bill,
               "fixture_direct_allowance": direct_bill,
               "boundary_cases": boundary_count,
               "lexicographic_max_gates_and_bill": maximum}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_DYADIC_RANKONE_BORROWING")


if __name__ == "__main__":
    main()

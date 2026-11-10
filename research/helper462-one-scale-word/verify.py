#!/usr/bin/env python3
"""One-scale zero-swap witness for the pinned helper-462 matcher.

The rational elementary alphabet admits an explicit word with zero axis swaps
and one scale. Integer shear coefficients cannot. No new kappa is claimed.
Standard library only.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb, gcd
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
WORD_PATH = Path(__file__).resolve().parent / "WORD.json"
N = 8
SCALE_ROW = 0
SCALE = Fraction(-16)


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def eye(n=N):
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


def rows_of(raw):
    return [[Fraction(entry) for entry in row] for row in raw]


def matmul(left, right):
    width = len(right[0])
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(width)] for i in range(len(left))]


def determinant(matrix):
    work = [[Fraction(entry) for entry in row] for row in matrix]
    size = len(work)
    det = Fraction(1)
    sign = 1
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        pivot_value = work[column][column]
        det *= pivot_value
        for row in range(column + 1, size):
            if work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for index in range(column, size):
                work[row][index] -= factor * work[column][index]
    return sign * det


def apply_row(op, matrix):
    out = [row[:] for row in matrix]
    kind = op[0]
    if kind == "add":
        target, source, coefficient = op[1:]
        need(target != source, "a shear must use two distinct rows")
        for column in range(len(out)):
            out[target][column] += coefficient * out[source][column]
    elif kind == "scale":
        target, coefficient = op[1:]
        need(coefficient != 0, "a scale coefficient must be nonzero")
        for column in range(len(out)):
            out[target][column] *= coefficient
    elif kind == "swap":
        left, right = op[1], op[2]
        out[left], out[right] = out[right], out[left]
    else:
        raise AssertionError(kind)
    return out


def product(ops, size=N):
    matrix = eye(size)
    for op in ops:
        matrix = apply_row(op, matrix)
    return matrix


def elementary_matrix(op, size=N):
    matrix = eye(size)
    kind = op[0]
    if kind == "add":
        target, source, coefficient = op[1:]
        matrix[target][source] += coefficient
    elif kind == "scale":
        target, coefficient = op[1:]
        matrix[target][target] = coefficient
    elif kind == "swap":
        left, right = op[1], op[2]
        matrix[left], matrix[right] = matrix[right], matrix[left]
    else:
        raise AssertionError(kind)
    return matrix


def matrix_product(ops, size=N):
    matrix = eye(size)
    for op in ops:
        matrix = matmul(elementary_matrix(op, size), matrix)
    return matrix


def signature(ops):
    value = Fraction(1)
    for op in ops:
        if op[0] == "swap":
            value = -value
        elif op[0] == "scale":
            value *= op[2]
    return value


def coefficient_text(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return "%d/%d" % (value.numerator, value.denominator)


def parse_coefficient(text):
    return Fraction(text)


def op_to_json(op):
    if op[0] == "add":
        return {"op": "add", "target": op[1], "source": op[2],
                "coefficient": coefficient_text(op[3])}
    if op[0] == "scale":
        return {"op": "scale", "target": op[1], "coefficient": coefficient_text(op[2])}
    raise AssertionError(op[0])


def op_from_json(raw):
    if raw["op"] == "add":
        return ("add", raw["target"], raw["source"], parse_coefficient(raw["coefficient"]))
    if raw["op"] == "scale":
        return ("scale", raw["target"], parse_coefficient(raw["coefficient"]))
    raise AssertionError(raw["op"])


def classify_matrix(factor):
    matrix = rows_of(factor)
    diffs = []
    for row in range(N):
        for column in range(N):
            expected = Fraction(int(row == column))
            if matrix[row][column] != expected:
                diffs.append((row, column, matrix[row][column]))
    if len(diffs) == 4:
        positions = {(row, column) for row, column, _ in diffs}
        off = [(row, column) for row, column, _ in diffs if row != column]
        (a, b), (c, d) = off
        if a == d and b == c and positions == {(a, a), (b, b), (a, b), (b, a)}:
            if (matrix[a][b] == 1 and matrix[b][a] == 1
                    and matrix[a][a] == 0 and matrix[b][b] == 0):
                return ("swap", a, b)
    if len(diffs) == 1:
        row, column, value = diffs[0]
        if row == column:
            return ("scale", row, value)
        return ("add", row, column, value)
    raise AssertionError("factor is not one elementary letter")


def published_word(factors):
    ops = []
    for factor in factors:
        kind = classify_matrix(factor)
        if kind[0] == "swap":
            ops.append(("swap", kind[1], kind[2]))
        elif kind[0] == "scale":
            ops.append(("scale", kind[1], kind[2]))
        else:
            ops.append(("add", kind[1], kind[2], kind[3]))
    return ops


def factor_special_linear(matrix):
    """Shears whose row-action on I equals a determinant-1 matrix.

    Reduce to I by the signed row exchange, the four-shear balanced scale and
    ordinary clearing. Reverse and negate. The caller supplies det 1.
    """
    size = len(matrix)
    work = [row[:] for row in matrix]
    reduction = []

    def add(target, source, coefficient):
        coefficient = Fraction(coefficient)
        if coefficient == 0:
            return
        for column in range(size):
            work[target][column] += coefficient * work[source][column]
        reduction.append(("add", target, source, coefficient))

    def balanced_scale(row_i, row_j, unit):
        # Left action of diag(unit, 1/unit) on rows (row_i, row_j).
        unit = Fraction(unit)
        add(row_i, row_j, -1 / unit)
        add(row_j, row_i, unit - 1)
        add(row_i, row_j, 1)
        add(row_j, row_i, 1 / unit - 1)

    def signed_exchange(row_a, row_b):
        # (Ra, Rb) -> (Rb, -Ra).
        add(row_a, row_b, 1)
        add(row_b, row_a, -1)
        add(row_a, row_b, 1)

    for column in range(size - 1):
        if work[column][column] == 0:
            source = next(row for row in range(column + 1, size) if work[row][column] != 0)
            signed_exchange(column, source)
        pivot = work[column][column]
        need(pivot != 0, "singular column in a determinant-1 reduction")
        if pivot != 1:
            balanced_scale(column, column + 1, 1 / pivot)
        for row in range(column + 1, size):
            if work[row][column] != 0:
                add(row, column, -work[row][column])
    need(work[size - 1][size - 1] == 1, "last pivot of a determinant-1 matrix")
    for column in range(size - 1, -1, -1):
        for row in range(column):
            if work[row][column] != 0:
                add(row, column, -work[row][column])
    need(work == eye(size), "reduction did not reach I")
    return [("add", target, source, -coefficient)
            for _, target, source, coefficient in reversed(reduction)]


def one_scale_word(matcher, scale_row=SCALE_ROW):
    """Shears for D^{-1} S, then the single scale by det(S) on scale_row.

    D scales that one row by -16, so D^{-1} S has determinant 1.
    """
    special = [row[:] for row in matcher]
    for column in range(N):
        special[scale_row][column] *= 1 / SCALE
    need(determinant(special) == 1, "cleared scale did not leave determinant 1")
    shears = factor_special_linear(special)
    return shears + [("scale", scale_row, SCALE)]


def rank_mod_two(matrix):
    work = [[entry % 2 for entry in row] for row in matrix]
    rank = 0
    used = set()
    for column in range(len(work[0])):
        pivot = next((row for row in range(rank, len(work))
                      if row not in used and work[row][column] % 2 == 1), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for row in range(len(work)):
            if row != rank and work[row][column] % 2 == 1:
                for index in range(len(work[0])):
                    work[row][index] = (work[row][index] + work[rank][index]) % 2
        used.add(rank)
        rank += 1
    return rank


def determinantal_divisors(matrix):
    size = len(matrix)
    divisors = []
    for order in range(1, size + 1):
        value = 0
        seen = 0
        for rows in combinations(range(size), order):
            for cols in combinations(range(size), order):
                minor = [[matrix[row][col] for col in cols] for row in rows]
                det = determinant(minor)
                need(det.denominator == 1, "minor determinant left Z")
                value = gcd(value, abs(int(det)))
                seen += 1
        need(seen == comb(size, order) ** 2, "minor census missed a combination")
        divisors.append(value)
    return divisors


def invariant_factors(divisors):
    factors = []
    previous = 1
    for value in divisors:
        need(value % previous == 0, "determinantal divisors are not chained")
        factors.append(value // previous)
        previous = value
    for earlier, later in zip(factors, factors[1:]):
        need(later % earlier == 0, "invariant factors do not divide")
    return factors


def field_two_rank_proof(matcher):
    """Human reduction: three repeated rows, then five pivots."""
    mod = [[int(entry) % 2 for entry in row] for row in matcher]
    need(mod[2] == mod[1] and mod[6] == mod[5] and mod[7] == mod[4],
         "the three mod-2 row relations changed")
    need(all(mod[row][0] == 0 and mod[row][1] == 0 for row in range(N)),
         "columns 0 and 1 are not identically even")
    rows = [mod[0][:], mod[5][:], mod[3][:], mod[1][:], mod[4][:]]
    for index in range(N):
        rows[3][index] = (rows[3][index] + rows[1][index]) % 2
    for index in range(N):
        rows[4][index] = (rows[4][index] + rows[3][index]) % 2
    expected = [
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 1],
    ]
    need(rows == expected, "the written mod-2 echelon changed")
    # First nonzero positions 4, 3, 6, 2, 5 are pairwise distinct, so these five
    # rows are independent over F2 even though the later rows are not cleared.
    leading = []
    for row in rows:
        leading.append(next(index for index, entry in enumerate(row) if entry == 1))
    need(leading == [4, 3, 6, 2, 5], "written leading columns changed")
    need(len(set(leading)) == 5, "written leading columns are not distinct")
    need(rank_mod_two(matcher) == 5, "generic mod-2 rank disagrees with the echelon")


def balanced_scale_identity():
    samples = [Fraction(2), Fraction(-16), Fraction(1, 2), Fraction(3, 7), Fraction(-1)]
    for unit in samples:
        row_i = [Fraction(1), Fraction(0)]
        row_j = [Fraction(0), Fraction(1)]
        rows = [row_i, row_j]
        ops = [
            ("add", 0, 1, -1 / unit),
            ("add", 1, 0, unit - 1),
            ("add", 0, 1, 1),
            ("add", 1, 0, 1 / unit - 1),
        ]
        for op in ops:
            target, source, coefficient = op[1:]
            rows[target] = [rows[target][k] + coefficient * rows[source][k] for k in range(2)]
        need(rows[0] == [unit, 0] and rows[1] == [0, 1 / unit],
             "balanced scale identity failed for %s" % unit)
        # (Ra, Rb) -> (Rb, -Ra).
        swapped = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
        for op in (("add", 0, 1, 1), ("add", 1, 0, -1), ("add", 0, 1, 1)):
            target, source, coefficient = op[1:]
            swapped[target] = [swapped[target][k] + coefficient * swapped[source][k]
                               for k in range(2)]
        need(swapped == [[0, 1], [-1, 0]], "signed exchange identity failed")


def diagonal_scale(row, coefficient, size=N):
    matrix = eye(size)
    matrix[row][row] = Fraction(coefficient)
    return matrix


def main():
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == "781451/250000000", "selected kappa moved")
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    matcher = rows_of(payload["matcher"])
    need(determinant(matcher) == SCALE, "pinned determinant is not -16")

    published = published_word(payload["right_route_factors"])
    published_counts = Counter(op[0] for op in published)
    need(published_counts == Counter({"swap": 5, "scale": 5, "add": 14}),
         "pinned elimination counts changed")
    # RESULT stores S = F0 F1 ... F23, so the leftmost factor is applied last.
    need(product(list(reversed(published))) == matcher, "pinned factors miss S")
    need(matrix_product(list(reversed(published))) == matcher,
         "matrix product of the pinned factors misses S")
    need(signature(published) == SCALE, "pinned signature misses det S")

    balanced_scale_identity()
    word = one_scale_word(matcher, SCALE_ROW)
    frozen = json.loads(WORD_PATH.read_text(encoding="utf-8"))
    frozen_ops = [op_from_json(raw) for raw in frozen["letters"]]
    need(word == frozen_ops, "regenerated word differs from WORD.json")
    need(frozen["scale_row"] == SCALE_ROW, "frozen scale row")
    need(parse_coefficient(frozen["scale_coefficient"]) == SCALE, "frozen scale coefficient")
    need(product(word) == matcher, "one-scale word misses S")
    need(matrix_product(word) == matcher, "matrix product of the one-scale word misses S")
    counts = Counter(op[0] for op in word)
    need(counts == Counter({"add": 53, "scale": 1}), "unexpected letter counts %s" % dict(counts))
    need(word[-1] == ("scale", SCALE_ROW, SCALE), "the unique scale is not the final letter")
    need(signature(word) == SCALE, "one-scale signature misses det S")
    denominators = sorted({op[3].denominator for op in word if op[0] == "add"})
    need(denominators == [1, 2, 4, 16], "unexpected shear denominators %s" % denominators)
    need(any(op[3].denominator != 1 for op in word if op[0] == "add"),
         "the witness collapsed to integer shears")

    for index in range(len(word)):
        shortened = word[:index] + word[index + 1:]
        need(product(shortened) != matcher, "dropping letter %d still realized S" % index)
    mutated_scale = list(word)
    mutated_scale[-1] = ("scale", SCALE_ROW, Fraction(-8))
    need(product(mutated_scale) != matcher, "scale -8 still realized S")
    mutated_scale[-1] = ("scale", SCALE_ROW, Fraction(16))
    need(product(mutated_scale) != matcher, "scale +16 still realized S")
    mutated_shear = list(word)
    shear = mutated_shear[0]
    need(shear[0] == "add", "expected the witness to start with a shear")
    mutated_shear[0] = ("add", shear[1], shear[2], shear[3] + 1)
    need(product(mutated_shear) != matcher, "a shear coefficient change still realized S")

    # The same elimination with the final scale on each coordinate. These eight
    # schedules are explicit witnesses. Their common shear count is not a minimum.
    expected_denominators = {
        0: [1, 2, 4, 16],
        1: [1, 2, 4, 8],
        2: [1, 2, 4, 8],
        3: [1, 2, 4],
        4: [1, 2, 4, 16],
        5: [1, 2, 4, 8],
        6: [1, 2, 4, 8],
        7: [1, 2, 4, 8, 16],
    }
    for scale_row, expected in expected_denominators.items():
        schedule = one_scale_word(matcher, scale_row)
        schedule_counts = Counter(op[0] for op in schedule)
        need(product(schedule) == matcher, "scale row %d misses S" % scale_row)
        need(schedule_counts == Counter({"add": 53, "scale": 1}),
             "scale row %d letter counts %s" % (scale_row, dict(schedule_counts)))
        need(schedule[-1] == ("scale", scale_row, SCALE), "scale row %d letter moved" % scale_row)
        found = sorted({op[3].denominator for op in schedule if op[0] == "add"})
        need(found == expected, "scale row %d denominators %s" % (scale_row, found))

    # Determinant-1 controls: no scale is introduced, and a pure scale pair factors.
    need(factor_special_linear(eye()) == [], "identity reduction added shears")
    paired = eye()
    paired[0][0] = Fraction(2)
    paired[1][1] = Fraction(1, 2)
    paired_word = factor_special_linear(paired)
    need(product(paired_word) == paired, "balanced-scale factorization missed diag(2, 1/2)")
    need(all(op[0] == "add" for op in paired_word), "a determinant-1 word gained a scale")

    # Integer-coefficient obstruction.
    field_two_rank_proof(matcher)
    divisors = determinantal_divisors([[int(entry) for entry in row] for row in matcher])
    need(divisors == [1, 1, 1, 1, 1, 2, 4, 16], "determinantal divisors changed %s" % divisors)
    need(invariant_factors(divisors) == [1, 1, 1, 1, 1, 2, 2, 4], "invariant factors changed")
    diagonal = diagonal_scale(0, -16)
    identity_minor_rows = list(range(1, 7))
    identity_minor_cols = list(range(1, 7))
    identity_minor = [[diagonal[row][col] for col in identity_minor_cols] for row in identity_minor_rows]
    need(identity_minor == eye(6), "the scale matrix lost its 6x6 identity minor")
    need(rank_mod_two([[int(entry) for entry in row] for row in diagonal]) == 7,
         "the single scale matrix is not rank 7 over F2")

    scale_free = [op for op in word if op[0] != "scale"]
    need(signature(scale_free) == 1, "shears alone changed the determinant")
    need(signature(scale_free) != determinant(matcher), "a scale-free word could realize det S")
    need(product([]) == eye() and determinant(eye()) == 1, "identity control")
    print(
        "PASS_HELPER462_ONE_SCALE_WORD"
        " swaps=0 scales=1 scale_row=0 scale=-16 shears=53"
        " shear_denominators=1,2,4,16"
        " det=-16 mod2_rank=5 delta6_matcher=2 delta6_one_integer_scale=1"
        " integer_one_scale=impossible rational_one_scale=witness"
        " no_new_kappa=1 selected=781451/250000000"
    )


if __name__ == "__main__":
    main()

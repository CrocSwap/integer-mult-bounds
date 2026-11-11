#!/usr/bin/env python3
"""Intermediate carries of the published frame-506 inverse elimination.

Proof for one fixed word, plus exhaustive censuses at the odd primes 3, 5 and 7.
No new kappa. Standard library only.
"""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
QMIN_NAMED = 5
QMIN_TAIL = 7
CLOSED = (F(0), F(-3, 2), F(-1, 2), F(0), F(-1, 2), F(-1, 2), F(-1, 2), F(-1, 2))
# Carry digits of the 5 scales and 14 shears, in word order, on u(q) for odd q >= 7.
TAIL_CARRIES = (
    F(0), F(0), F(-1, 2), F(-1, 2), F(0), F(0), F(1, 2), F(1, 2), F(-1),
    F(0), F(-1), F(1, 2), F(-1, 2), F(-1), F(0), F(-1), F(-1), F(-1, 2), F(-1, 2),
)
# The single odd integer q = 5, where q - 6 is negative. Direct evaluation.
FIVE_CARRIES = (
    F(0), F(0), F(-1, 2), F(-1, 2), F(0), F(0), F(1, 2), F(1, 2), F(-1),
    F(-1), F(0), F(1, 2), F(-1, 2), F(-1), F(0), F(-1), F(-1), F(-1, 2), F(-1, 2),
)
# First base-q row that attains the census maximum. Coordinates are base-q digits.
CENSUS = {
    3: {
        "max": 18,
        "witness": (1, 1, 1, 2, 0, 0, 0, 1),
        "hist": (36, 36, 189, 351, 423, 675, 702, 693, 918, 747, 639, 450, 270, 189, 117, 72, 45, 0, 9, 0),
    },
    5: {
        "max": 18,
        "witness": (1, 1, 1, 4, 0, 0, 0, 1),
        "hist": (225, 625, 3350, 7650, 15175, 26475, 28700, 35600, 50700, 50525, 42475, 38200, 32650, 25150, 15000, 9650, 5675, 2225, 575, 0),
    },
    7: {
        "max": 19,
        "witness": (5, 5, 6, 3, 0, 0, 0, 4),
        "hist": (784, 4655, 23324, 65611, 161749, 305025, 344715, 447615, 688744, 741419, 651406, 620879, 576436, 463050, 287875, 188895, 119903, 57869, 14602, 245),
    },
}


def need(ok, message):
    if not ok:
        raise SystemExit(message)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum((x * y for x, y in zip(row, col)), F(0)) for col in zip(*b)] for row in a]


def transpose(rows):
    return [list(col) for col in zip(*rows)]


def load_pins():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        data = path.read_bytes()
        need(sha256(data).hexdigest() == row["sha256"], "sha256 mismatch: " + row["path"])
        pinned[row["path"]] = data
    return pinned


def matcher_from_frame(raw):
    frame = json.loads(raw)["frames"]["506"]
    need(frame["dim"] == 4, "frame 506 rank")
    blocks = [[F(x) for x in row] for row in frame["B"] + frame["A"]]
    need(len(blocks) == 8 and all(len(row) == 8 for row in blocks), "frame 506 shape")
    return transpose(blocks)


def decompose(matrix):
    """Published deterministic elimination. Factors are the right-product for matrix."""
    work = [row[:] for row in matrix]
    n = len(matrix)
    factors = []
    for column in range(n):
        pivot = next(row for row in range(column, n) if work[row][column])
        elementary = eye(n)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            elementary[column], elementary[pivot] = elementary[pivot], elementary[column]
            factors.append(elementary)
            elementary = eye(n)
        pivot_value = work[column][column]
        if pivot_value != 1:
            work[column] = [entry / pivot_value for entry in work[column]]
            elementary[column][column] = pivot_value
            factors.append(elementary)
            elementary = eye(n)
        for row in range(n):
            if row != column and work[row][column]:
                coefficient = -work[row][column]
                work[row] = [entry + coefficient * source for entry, source in zip(work[row], work[column])]
                elementary = eye(n)
                elementary[row][column] = -coefficient
                factors.append(elementary)
    need(work == eye(n), "elimination did not reach I")
    product = eye(n)
    for factor in factors:
        product = mm(product, factor)
    need(product == matrix, "right product is not the matcher")
    return factors


def transposition(factor):
    n = len(factor)
    images = []
    for row in factor:
        hits = [column for column, entry in enumerate(row) if entry != 0]
        if len(hits) != 1 or row[hits[0]] != 1:
            return None
        images.append(hits[0])
    if sorted(images) != list(range(n)):
        return None
    moved = [index for index, image in enumerate(images) if image != index]
    if len(moved) != 2:
        return None
    left, right = moved
    if images[left] != right or images[right] != left:
        return None
    return left, right


def classify(factor):
    """Right action on one row: swap, scale one coordinate, or add into one coordinate."""
    swapped = transposition(factor)
    if swapped:
        return ("swap", swapped[0], swapped[1], F(1))
    n = len(factor)
    off = [(row, column, factor[row][column]) for row in range(n) for column in range(n) if row != column and factor[row][column] != 0]
    if len(off) == 1:
        source, target, coefficient = off[0]
        for row in range(n):
            for column in range(n):
                if (row, column) == (source, target):
                    continue
                need(factor[row][column] == (1 if row == column else 0), "shear is not elementary")
        return ("add", target, source, coefficient)
    need(not off, "factor is not an elementary scale")
    changed = [(index, factor[index][index]) for index in range(n) if factor[index][index] != 1]
    need(len(changed) == 1 and changed[0][1] != 0, "scale is not a single nonzero unit")
    index, coefficient = changed[0]
    return ("scale", index, index, coefficient)


def inverse_word(factors):
    word = []
    matrices = []
    n = len(factors[0])
    for factor in reversed(factors):
        kind = classify(factor)
        inverse = eye(n)
        if kind[0] == "swap":
            left, right = kind[1], kind[2]
            inverse[left], inverse[right] = inverse[right], inverse[left]
        elif kind[0] == "scale":
            inverse[kind[1]][kind[1]] = 1 / kind[3]
        else:
            target, source, coefficient = kind[1], kind[2], kind[3]
            inverse[source][target] = -coefficient
        need(mm(factor, inverse) == eye(n), "elementary inverse")
        matrices.append(inverse)
        word.append(classify(inverse))
    return word


def prove_range(constant, slope, qmin):
    """True when constant + slope*q is an integer in {0, ..., q-1} for every odd integer q >= qmin.

    The slope has to lie in [0, 1]. Integrality is checked on every odd residue class modulo the
    power-of-two denominator. Both the value and the slack q - value are then nondecreasing along
    that class, because a step by the period adds a nonnegative integer to each.
    """
    if not (F(0) <= slope <= 1):
        return False
    denominator = max(constant.denominator, slope.denominator)
    if denominator & (denominator - 1):
        return False
    if (slope * denominator).denominator != 1 or (constant * denominator).denominator != 1:
        return False
    period = denominator
    classes = 1 if period == 1 else period // 2
    start = qmin if qmin % 2 else qmin + 1
    seen = {}
    q = start
    while len(seen) < classes:
        residue = q % period
        if residue not in seen:
            value = constant + slope * q
            if value.denominator != 1 or not (0 <= value < q):
                return False
            seen[residue] = q
        q += 2
        if q > start + 4 * period + 4:
            return False
    step = 2 if period == 1 else period
    if (slope * step).denominator != 1:
        return False
    if slope * step < 0 or step * (1 - slope) < 0:
        return False
    return len(seen) == classes


def choose_slope(constant, linear, qmin):
    found = []
    for numerator in range(5):
        slope = F(numerator, 4)
        if prove_range(constant, slope, qmin):
            found.append((slope, linear - slope))
    need(len(found) == 1, "carry slope is not unique at qmin %s" % qmin)
    return found[0]


def affine_tail(word):
    """Closed form of every scale and shear carry on u(q) for odd q >= 7."""
    low = [
        (F(-2), F(1)), (F(-2), F(1)), (F(-5), F(1)), (F(-5), F(1)),
        (F(0), F(0)), (F(-1), F(1)), (F(0), F(0)), (F(0), F(0)),
    ]
    for constant, slope in low:
        need(prove_range(constant, slope, QMIN_NAMED), "u(q) digit leaves range")
    high = [F(0)] * 8
    carries = []
    for kind, target, source, coefficient in word:
        if kind == "swap":
            low[target], low[source] = low[source], low[target]
            high[target], high[source] = high[source], high[target]
            continue
        if kind == "scale":
            unreduced_constant = coefficient * low[target][0]
            unreduced_linear = coefficient * low[target][1]
            slope, carry = choose_slope(unreduced_constant, unreduced_linear, QMIN_TAIL)
            high[target] = coefficient * high[target] + carry
            low[target] = (unreduced_constant, slope)
        else:
            unreduced_constant = low[target][0] + coefficient * low[source][0]
            unreduced_linear = low[target][1] + coefficient * low[source][1]
            slope, carry = choose_slope(unreduced_constant, unreduced_linear, QMIN_TAIL)
            high[target] = high[target] + coefficient * high[source] + carry
            low[target] = (unreduced_constant, slope)
        carries.append(carry)
    return low, high, carries


def split(value, q):
    residue = (value.numerator * pow(value.denominator, -1, q)) % q
    return residue, (value - residue) / q


def direct(word, row, q):
    low = list(row)
    high = [F(0)] * 8
    carries = []
    for kind, target, source, coefficient in word:
        if kind == "swap":
            low[target], low[source] = low[source], low[target]
            high[target], high[source] = high[source], high[target]
            continue
        if kind == "scale":
            residue, carry = split(low[target] * coefficient, q)
            high[target] = coefficient * high[target] + carry
            low[target] = residue
        else:
            residue, carry = split(low[target] + coefficient * low[source], q)
            high[target] = high[target] + coefficient * high[source] + carry
            low[target] = residue
        carries.append(carry)
    return low, high, carries


def direct_without_carry(word, row, q):
    low = list(row)
    high = [F(0)] * 8
    for kind, target, source, coefficient in word:
        if kind == "swap":
            low[target], low[source] = low[source], low[target]
            high[target], high[source] = high[source], high[target]
        elif kind == "scale":
            residue, _carry = split(low[target] * coefficient, q)
            high[target] = coefficient * high[target]
            low[target] = residue
        else:
            residue, _carry = split(low[target] + coefficient * low[source], q)
            high[target] = high[target] + coefficient * high[source]
            low[target] = residue
    return high


def integer_nonzero(kind, target_digit, source_digit, coefficient, q):
    """Equivalent to a nonzero rational quotient for coefficients in {±1, ±1/2}."""
    inverse_two = pow(2, -1, q)
    if kind == "scale":
        if coefficient.denominator == 1:
            value = target_digit * int(coefficient)
            return value != value % q
        multiple = target_digit * int(coefficient.numerator)
        residue = (multiple * inverse_two) % q
        return multiple != 2 * residue
    if coefficient.denominator == 1:
        value = target_digit + int(coefficient) * source_digit
        return value != value % q
    multiple = 2 * target_digit + int(coefficient.numerator) * source_digit
    residue = (multiple * inverse_two) % q
    return multiple != 2 * residue


def fraction_nonzero(kind, target_digit, source_digit, coefficient, q):
    if kind == "scale":
        _residue, carry = split(target_digit * coefficient, q)
    else:
        _residue, carry = split(target_digit + coefficient * source_digit, q)
    return carry != 0


def census(word, q):
    inverse_two = pow(2, -1, q)
    prepared = []
    for kind, target, source, coefficient in word:
        if kind == "swap":
            prepared.append(("swap", target, source))
            continue
        need(coefficient.denominator in (1, 2), "census coefficient outside the proved family")
        prepared.append((kind, target, source, int(coefficient.numerator), coefficient.denominator))
    counts = [0] * 20
    total = q ** 8
    for code in range(total):
        digits = [(code // q ** index) % q for index in range(8)]
        nonzero = 0
        for op in prepared:
            if op[0] == "swap":
                digits[op[1]], digits[op[2]] = digits[op[2]], digits[op[1]]
                continue
            kind, target, source, numerator, denominator = op
            if kind == "scale":
                if denominator == 1:
                    value = digits[target] * numerator
                    residue = value % q
                    hit = value != residue
                else:
                    multiple = digits[target] * numerator
                    residue = (multiple * inverse_two) % q
                    hit = multiple != 2 * residue
                digits[target] = residue
            else:
                if denominator == 1:
                    value = digits[target] + numerator * digits[source]
                    residue = value % q
                    hit = value != residue
                else:
                    multiple = 2 * digits[target] + numerator * digits[source]
                    residue = (multiple * inverse_two) % q
                    hit = multiple != 2 * residue
                digits[target] = residue
            nonzero += hit
        counts[nonzero] += 1
    need(sum(counts) == total, "census missed a row at q=%s" % q)
    return counts


def named_row(q):
    return (q - 2, q - 2, q - 5, q - 5, 0, q - 1, 0, 0)


def returned_row(q):
    return (0, q - 1, q - 2, 0, q - 1, q - 1, q - 1, 1)


def main():
    pinned = load_pins()
    selected = json.loads(pinned["certificates/selected-result.json"])
    need(selected["kappa"] == "363005817/100000000000", "selected frontier string")
    word_record = json.loads(gzip.decompress(pinned["research/bit-completed-backend-api/independent/inputs/WORD.json.gz"]))
    need(word_record["start"][462] == 0 and word_record["final"][462] == 506, "helper 462 endpoints")
    matrix = matcher_from_frame(pinned["research/bit-completed-backend-api/independent/inputs/frames.json"])
    published = json.loads(pinned["research/bit-completed-backend-api/science/RESULT.json"])
    need([[F(entry) for entry in row] for row in published["matcher"]] == matrix, "published matcher")
    need(published["right_route_elimination_counts"] == {"swap": 5, "scale": 5, "add": 14}, "published counts")
    factors = decompose(matrix)
    published_factors = [[[F(entry) for entry in row] for row in factor] for factor in published["right_route_factors"]]
    need(factors == published_factors, "elimination differs from the published factors")
    word = inverse_word(factors)
    n = 8
    product = eye(n)
    for factor in reversed(factors):
        kind = classify(factor)
        inverse = eye(n)
        if kind[0] == "swap":
            inverse[kind[1]], inverse[kind[2]] = inverse[kind[2]], inverse[kind[1]]
        elif kind[0] == "scale":
            inverse[kind[1]][kind[1]] = 1 / kind[3]
        else:
            inverse[kind[2]][kind[1]] = -kind[3]
        product = mm(product, inverse)
    inverse_matrix = mm(matrix, product)
    need(inverse_matrix == eye(n), "inverse word is not S^{-1}")
    scales = [op for op in word if op[0] == "scale"]
    shears = [op for op in word if op[0] == "add"]
    swaps = [op for op in word if op[0] == "swap"]
    need(len(scales) == 5 and len(shears) == 14 and len(swaps) == 5, "inverse word shape")
    need(len(scales) + len(shears) == 19 < 48, "site bound")

    # The range prover rejects the q = 5 boundary and accepts the tail.
    need(not prove_range(F(-6), F(1), 5), "q-6 must leave range at q=5")
    need(prove_range(F(-6), F(1), 7), "q-6 must stay in range for odd q>=7")

    low, high, carries = affine_tail(word)
    need(tuple(carries) == TAIL_CARRIES, "tail carry digits")
    need(sum(carry != 0 for carry in carries) == 13, "tail nonzero count")
    need(tuple(high) == CLOSED, "tail high part is not the closed-form correction")
    for index, (constant, slope) in enumerate(low):
        need((constant, slope) == ((F(0), F(0)), (F(-1), F(1)), (F(-2), F(1)), (F(0), F(0)), (F(-1), F(1)), (F(-1), F(1)), (F(-1), F(1)), (F(1), F(0)))[index], "tail final low digit")

    for q in (5, 7, 9, 11, 15, 21, 401):
        row, carried_high, carried = direct(word, named_row(q), q)
        need(tuple(row) == returned_row(q), "direct return low digits at q=%s" % q)
        need(tuple(carried_high) == CLOSED, "direct return high digits at q=%s" % q)
        expected = FIVE_CARRIES if q == 5 else TAIL_CARRIES
        need(tuple(carried) == expected, "direct carry digits at q=%s" % q)
        omitted = direct_without_carry(word, named_row(q), q)
        need(tuple(omitted) != CLOSED, "dropping the intermediate carries still matched at q=%s" % q)
        zero_row, _zero_high, zero_carries = direct(word, (0,) * 8, q)
        need(zero_row == [0] * 8 and all(carry == 0 for carry in zero_carries), "zero row emitted a carry")

    changed = [index for index, (left, right) in enumerate(zip(FIVE_CARRIES, TAIL_CARRIES)) if left != right]
    need(changed == [9, 10], "q=5 and the tail differ in more than the q-6 step and the next shear")
    need(sum(carry != 0 for carry in FIVE_CARRIES) == 13, "q=5 nonzero count")

    coefficients = {op[3] for op in word if op[0] != "swap"}
    need(coefficients <= {F(1), F(-1), F(1, 2), F(-1, 2)}, "unexpected coefficient")
    for q in (3, 5, 7):
        for kind, target, source, coefficient in word:
            if kind == "swap":
                continue
            for left in range(q):
                rights = range(q) if kind == "add" else (0,)
                for right in rights:
                    need(
                        integer_nonzero(kind, left, right, coefficient, q)
                        == fraction_nonzero(kind, left, right, coefficient, q),
                        "integer carry test diverges from the quotient",
                    )

    for q, record in CENSUS.items():
        counts = census(word, q)
        need(tuple(counts) == record["hist"], "census histogram at q=%s" % q)
        need(sum(counts) == q ** 8, "census domain at q=%s" % q)
        need(max(index for index, count in enumerate(counts) if count) == record["max"], "census maximum")
        _row, _high, witness_carries = direct(word, record["witness"], q)
        need(sum(carry != 0 for carry in witness_carries) == record["max"], "witness count at q=%s" % q)
        need(record["max"] < 48, "census row reached 48")

    print("PASS_FRAME506_INVERSE_ROW_CARRIES nonzero=13 sites=19 census_max=18,18,19")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        if exc.code not in (0, None):
            print(exc, file=sys.stderr)
        raise

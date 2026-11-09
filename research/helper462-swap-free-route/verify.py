#!/usr/bin/env python3
"""Swap-free elementary route for the pinned helper-462 matcher.

The predecessor elimination of this one 8x8 matcher uses five axis swaps.
Those swaps are a Gaussian schedule. They are not required by the elementary
alphabet. No new kappa is claimed. Standard library only.
"""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
N = 8


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def eye():
    return [[Fraction(int(i == j)) for j in range(N)] for i in range(N)]


def rows_of(raw):
    return [[Fraction(entry) for entry in row] for row in raw]


def apply(op, matrix):
    out = [row[:] for row in matrix]
    kind = op[0]
    if kind == "add":
        target, source, coefficient = op[1:]
        for column in range(N):
            out[target][column] += coefficient * out[source][column]
    elif kind == "scale":
        target, coefficient = op[1:]
        for column in range(N):
            out[target][column] *= coefficient
    elif kind == "swap":
        left, right = op[1], op[2]
        out[left], out[right] = out[right], out[left]
    else:
        raise AssertionError(kind)
    return out


def product(ops):
    matrix = eye()
    for op in ops:
        matrix = apply(op, matrix)
    return matrix


def determinant(matrix):
    work = [row[:] for row in matrix]
    det = Fraction(1)
    sign = 1
    for column in range(N):
        pivot = next((row for row in range(column, N) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        pivot_value = work[column][column]
        det *= pivot_value
        for row in range(column + 1, N):
            if work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for index in range(column, N):
                work[row][index] -= factor * work[column][index]
    return sign * det


def signature(ops):
    """Determinant contributed by swaps and scales. Shears contribute 1."""
    value = Fraction(1)
    for op in ops:
        if op[0] == "swap":
            value = -value
        elif op[0] == "scale":
            value *= op[2]
    return value


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
        (a, b), (c, d) = [(row, column) for row, column, value in diffs if row != column]
        if a == d and b == c and positions == {(a, a), (b, b), (a, b), (b, a)}:
            if matrix[a][b] == 1 and matrix[b][a] == 1 and matrix[a][a] == 0 and matrix[b][b] == 0:
                return ("swap", a, b)
    if len(diffs) == 1:
        row, column, value = diffs[0]
        if row == column:
            return ("scale", row, value)
        return ("add", row, column, value)
    raise AssertionError("factor is not one elementary alphabet letter: %r" % diffs)


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


def swap_free_word(matcher):
    """Eliminate without axis swaps, then invert the row operations.

    When a diagonal entry is zero, add a later nonzero row into it. Scale the
    pivot to 1, clear below, then clear above. Inverting that reduction is a
    word in scales and shears whose left-to-right product is the matcher.
    """
    matrix = [row[:] for row in matcher]
    reduction = []
    for column in range(N):
        if matrix[column][column] == 0:
            source = next(row for row in range(column + 1, N) if matrix[row][column] != 0)
            for index in range(N):
                matrix[column][index] += matrix[source][index]
            reduction.append(("add", column, source, Fraction(1)))
        if matrix[column][column] != 1:
            coefficient = 1 / matrix[column][column]
            for index in range(N):
                matrix[column][index] *= coefficient
            reduction.append(("scale", column, coefficient))
        for row in range(column + 1, N):
            if matrix[row][column] == 0:
                continue
            coefficient = -matrix[row][column]
            for index in range(N):
                matrix[row][index] += coefficient * matrix[column][index]
            reduction.append(("add", row, column, coefficient))
    for column in range(N - 1, -1, -1):
        for row in range(column):
            if matrix[row][column] == 0:
                continue
            coefficient = -matrix[row][column]
            for index in range(N):
                matrix[row][index] += coefficient * matrix[column][index]
            reduction.append(("add", row, column, coefficient))
    identity = eye()
    need(matrix == identity, "swap-free reduction did not reach I")
    word = []
    for op in reversed(reduction):
        if op[0] == "add":
            word.append(("add", op[1], op[2], -op[3]))
        else:
            word.append(("scale", op[1], 1 / op[2]))
    return word


def pair_bill(counts):
    # Predecessor accounting: each cover-row letter acts on all 8 high rows,
    # and the inverse route repeats the same letter counts.
    return {kind: 16 * counts.get(kind, 0) for kind in ("swap", "scale", "add")}


def main():
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    matcher = rows_of(payload["matcher"])
    published = published_word(payload["right_route_factors"])
    published_counts = Counter(op[0] for op in published)
    ledger = payload["selected_route_pair_high_matrix_ledger"]
    need(published_counts == Counter({"swap": 5, "scale": 5, "add": 14}),
         "pinned elimination counts changed")
    # RESULT stores S = F0 F1 ... F23, so the leftmost factor is applied last.
    need(product(list(reversed(published))) == matcher,
         "pinned factors do not multiply to the matcher")
    need(signature(published) == determinant(matcher) == Fraction(-16),
         "pinned word breaks the determinant identity")
    need(ledger["ordinary_chunk_interchanges"] == 80, "pinned ordinary ledger")
    need(ledger["fixed_unit_scalings"] == 80, "pinned scale ledger")
    need(ledger["linear_ordered_shifts"] == 224, "pinned shift ledger")
    need(pair_bill(published_counts) == {"swap": 80, "scale": 80, "add": 224},
         "high-row multiplier does not reproduce the pinned pair ledger")

    word = swap_free_word(matcher)
    counts = Counter(op[0] for op in word)
    need(product(word) == matcher, "swap-free word does not multiply to the matcher")
    need(counts["swap"] == 0 and counts["scale"] == 7 and counts["add"] == 27,
         "unexpected swap-free shape %s" % dict(counts))
    need(signature(word) == Fraction(-16), "swap-free scales do not multiply to det S")
    bill = pair_bill(counts)
    need(bill == {"swap": 0, "scale": 112, "add": 432}, "unexpected pair bill %s" % bill)

    # Every letter is invertible, swaps and shears have determinant ±1, and a
    # scale by c has determinant c. Zero scales would force det ±1.
    need(determinant(matcher) not in (1, -1), "determinant control")
    scale_free = [op for op in word if op[0] != "scale"]
    need(signature(scale_free) in (1, -1), "scale-free signature must be a swap sign")
    need(signature(scale_free) != determinant(matcher),
         "a scale-free word cannot realize this determinant")

    # Identity is realized with no scales and no swaps, so the scale lower
    # bound is not an artifact of the checker demanding a scale for every matrix.
    need(product([]) == eye() and signature([]) == determinant(eye()) == 1,
         "identity control")

    dropped = word[:-1]
    need(product(dropped) != matcher, "dropping the last letter still realized S")
    mutated = list(word)
    last = mutated[-1]
    need(last[0] == "add", "expected the constructive word to end in a shear")
    mutated[-1] = ("add", last[1], last[2], last[3] + 1)
    need(product(mutated) != matcher, "a shear coefficient change still realized S")

    # The published schedule remains a correct word. The new fact is that its
    # five swaps are not the only legal letter count.
    need(published_counts["swap"] > counts["swap"] == 0, "swap count did not drop")
    print(
        "PASS_HELPER462_SWAP_FREE_ROUTE"
        " swaps=0 scales=7 shears=27"
        " pair_ordinary=0 pair_scales=112 pair_shifts=432"
        " published_pair_ordinary=80 published_pair_scales=80 published_pair_shifts=224"
        " det=-16 minimum_scales=1 no_new_kappa=1"
    )


if __name__ == "__main__":
    main()

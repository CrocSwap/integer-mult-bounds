#!/usr/bin/env python3
"""Zero-swap helper-462 word with at least two scales and 25 shears.

The alphabet is row swaps, single-coordinate scales and shears. This witness
uses no swaps. It is restricted to at least two scales: a one-scale word is a
different question, and 25 is not claimed to be minimal. No tariff and no new
kappa. Standard library only.
"""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
N = 8

# Seven integer shears and five scales take the pinned matcher to the
# permutation matrix whose row i holds the basis vector e_{LANDING[i]}.
CLEANUP = (
    ("add", 2, 1, Fraction(-1)),
    ("scale", 2, Fraction(1, 2)),
    ("add", 1, 2, Fraction(1)),
    ("add", 4, 7, Fraction(1)),
    ("scale", 4, Fraction(1, 2)),
    ("add", 7, 4, Fraction(-1)),
    ("scale", 7, Fraction(-1)),
    ("add", 1, 7, Fraction(-1)),
    ("add", 5, 1, Fraction(-1)),
    ("scale", 5, Fraction(1, 2)),
    ("add", 6, 1, Fraction(-1)),
    ("scale", 6, Fraction(1, 2)),
)
LANDING = (4, 3, 5, 6, 7, 0, 1, 2)
# Selection sort of that permutation. Each pair is one content exchange.
EXCHANGES = ((0, 5), (1, 6), (2, 7), (3, 6), (4, 5), (5, 7))


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
        need(target != source and coefficient != 0, "shear letter is not elementary")
        for column in range(N):
            out[target][column] += coefficient * out[source][column]
    elif kind == "scale":
        target, coefficient = op[1:]
        need(coefficient not in (0, 1), "scale letter is not a non-identity scale")
        for column in range(N):
            out[target][column] *= coefficient
    elif kind == "swap":
        left, right = op[1], op[2]
        out[left], out[right] = out[right], out[left]
    else:
        raise AssertionError(kind)
    return out


def product(ops, matrix=None):
    if matrix is None:
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
    value = Fraction(1)
    for op in ops:
        if op[0] == "swap":
            value = -value
        elif op[0] == "scale":
            value *= op[2]
    return value


def content_swap(left, right):
    """Exchange two row contents: (A, B) goes to (B, A).

    The three shears send (A, B) to (B, -A). The scale by -1 corrects the sign.
    """
    return (
        ("add", left, right, Fraction(1)),
        ("add", right, left, Fraction(-1)),
        ("add", left, right, Fraction(1)),
        ("scale", right, Fraction(-1)),
    )


def invert(op):
    if op[0] == "add":
        return ("add", op[1], op[2], -op[3])
    if op[0] == "scale":
        return ("scale", op[1], 1 / op[2])
    raise AssertionError(op)


def reduction():
    ops = list(CLEANUP)
    for left, right in EXCHANGES:
        ops.extend(content_swap(left, right))
    return ops


def forward_word():
    """Left-to-right letters whose product is the matcher.

    The reduction R satisfies R(S) = I, so S = R^{-1}. Row operations are left
    multiplications, and the inverse of a product reverses order.
    """
    return [invert(op) for op in reversed(reduction())]


def basis_column(row):
    nonzero = [(column, value) for column, value in enumerate(row) if value != 0]
    need(len(nonzero) == 1 and nonzero[0][1] == 1, "row is not a positive basis vector")
    return nonzero[0][0]


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
        off = [(row, column) for row, column, _value in diffs if row != column]
        need(len(off) == 2, "swap shape")
        (left_row, left_column), (right_row, right_column) = off
        if (left_row == right_column and left_column == right_row
                and positions == {(left_row, left_row), (right_row, right_row),
                                  (left_row, left_column), (right_row, right_column)}
                and matrix[left_row][left_column] == 1 and matrix[right_row][right_column] == 1
                and matrix[left_row][left_row] == 0 and matrix[right_row][right_row] == 0):
            return ("swap", left_row, right_row)
    if len(diffs) == 1:
        row, column, value = diffs[0]
        if row == column:
            return ("scale", row, value)
        return ("add", row, column, value)
    raise AssertionError("factor is not one elementary letter")


def published_word(factors):
    return [classify_matrix(factor) for factor in factors]


def recorded_swap_free_word(matcher):
    """The elimination recorded by the 27-shear schedule, recomputed here.

    It is a comparison control. It is not this package's word, and its shear
    count is not a lower bound.
    """
    matrix = [row[:] for row in matcher]
    steps = []
    for column in range(N):
        if matrix[column][column] == 0:
            source = next(row for row in range(column + 1, N) if matrix[row][column] != 0)
            for index in range(N):
                matrix[column][index] += matrix[source][index]
            steps.append(("add", column, source, Fraction(1)))
        if matrix[column][column] != 1:
            coefficient = 1 / matrix[column][column]
            for index in range(N):
                matrix[column][index] *= coefficient
            steps.append(("scale", column, coefficient))
        for row in range(column + 1, N):
            if matrix[row][column] == 0:
                continue
            coefficient = -matrix[row][column]
            for index in range(N):
                matrix[row][index] += coefficient * matrix[column][index]
            steps.append(("add", row, column, coefficient))
    for column in range(N - 1, -1, -1):
        for row in range(column):
            if matrix[row][column] == 0:
                continue
            coefficient = -matrix[row][column]
            for index in range(N):
                matrix[row][index] += coefficient * matrix[column][index]
            steps.append(("add", row, column, coefficient))
    need(matrix == eye(), "recorded elimination did not reach I")
    word = []
    for op in reversed(steps):
        word.append(invert(op))
    return word


def check_content_swap():
    start = eye()
    start[0] = [Fraction(x) for x in (3, -5, 0, 8, 1, 0, 2, -1)]
    start[1] = [Fraction(x) for x in (0, 4, 7, -2, 0, 1, 0, 3)]
    saved = [row[:] for row in start]
    got = product(content_swap(0, 1), [row[:] for row in start])
    need(got[0] == saved[1] and got[1] == saved[0], "content swap failed on a non-basis pair")
    for row in range(2, N):
        need(got[row] == saved[row], "content swap changed a spectator row")
    # The three shears alone send (A, B) to (B, -A). That is the sign this
    # scale corrects, not a second independent exchange.
    unsigned = product(content_swap(0, 1)[:3], [row[:] for row in start])
    need(unsigned[0] == saved[1], "unsigned exchange did not move the first row")
    need(unsigned[1] == [-value for value in saved[0]], "unsigned exchange sign")


def main():
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == "781451/250000000", "selected kappa pin changed")
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    matcher = rows_of(payload["matcher"])
    need(determinant(matcher) == Fraction(-16), "pinned determinant")

    published = published_word(payload["right_route_factors"])
    published_counts = Counter(op[0] for op in published)
    need(published_counts == Counter({"swap": 5, "scale": 5, "add": 14}),
         "pinned elimination counts changed")
    need(product(list(reversed(published))) == matcher,
         "pinned factors do not multiply to the matcher")
    need(signature(published) == Fraction(-16), "published word breaks the determinant identity")

    check_content_swap()

    current = [row[:] for row in matcher]
    for op in CLEANUP:
        current = apply(op, current)
    need(tuple(basis_column(row) for row in current) == LANDING,
         "cleanup did not reach the pinned permutation")
    seen = []
    for left, _right in EXCHANGES:
        source = next(row for row in range(N) if basis_column(current[row]) == left)
        seen.append((left, source))
        for op in content_swap(left, source):
            current = apply(op, current)
    need(seen == list(EXCHANGES), "exchange sequence drifted: %s" % (seen,))
    need(current == eye(), "reduction did not reach I")

    word = forward_word()
    counts = Counter(op[0] for op in word)
    need(product(word) == matcher, "forward word does not multiply to the matcher")
    need(counts == Counter({"add": 25, "scale": 11}), "unexpected shape %s" % dict(counts))
    need(counts["scale"] >= 2 and counts["add"] < 27 and counts.get("swap", 0) == 0,
         "witness left the declared two-scale zero-swap band")
    need(signature(word) == Fraction(-16), "scale product is not det S")
    shear_coefficients = {op[3] for op in word if op[0] == "add"}
    scale_coefficients = [op[2] for op in word if op[0] == "scale"]
    need(shear_coefficients <= {Fraction(-1), Fraction(1)}, "shear left Z")
    need(sorted(scale_coefficients) == [Fraction(-1)] * 7 + [Fraction(2)] * 4,
         "unexpected scale multiset %s" % [str(c) for c in scale_coefficients])

    recorded = recorded_swap_free_word(matcher)
    recorded_counts = Counter(op[0] for op in recorded)
    need(product(recorded) == matcher, "recorded 27-shear schedule missed S")
    need(recorded_counts == Counter({"add": 27, "scale": 7}),
         "recorded schedule shape changed: %s" % dict(recorded_counts))
    need(counts["add"] < recorded_counts["add"], "new word is not strictly shorter")
    # Same restricted class: the recorded schedule also has at least two scales.
    # The new fact is the shear count, not a tariff.
    need(recorded_counts["scale"] >= 2 and counts["scale"] != 1, "scale restriction")

    dropped = word[:-1]
    need(product(dropped) != matcher, "dropping the last letter still realized S")
    need(word[-1][0] == "add", "expected the forward word to end in a shear")
    last = word[-1]
    mutated = list(word)
    mutated[-1] = ("add", last[1], last[2], last[3] + 1)
    need(product(mutated) != matcher, "a shear coefficient change still realized S")
    scaled = list(word)
    scale_at = next(index for index, op in enumerate(word) if op[0] == "scale" and op[2] == 2)
    scaled[scale_at] = ("scale", word[scale_at][1], Fraction(4))
    need(product(scaled) != matcher, "replacing a scale by 2 with a scale by 4 still realized S")
    need(product([]) == eye() and signature([]) == determinant(eye()) == 1, "identity control")
    need(signature([op for op in word if op[0] != "scale"]) != determinant(matcher),
         "scale-free signature cannot realize det -16")

    print(
        "PASS_HELPER462_TWO_SCALE_SHEAR"
        " swaps=0 scales=11 shears=25"
        " scale_product=-16 integer_shears=1"
        " at_least_two_scales=1 below_recorded_27=1"
        " minimum_claimed=0 one_scale_case=0 tariff_comparison=0"
        " selected_kappa=781451/250000000 no_new_kappa=1"
    )


if __name__ == "__main__":
    main()

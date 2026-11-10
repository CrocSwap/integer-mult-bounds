#!/usr/bin/env python3
"""A 26-shear one-scale zero-swap word for the pinned helper-462 matcher.

The word is a constructive witness. It is shorter than the 29-shear word of
open PR #7030 and the 53-shear word of merged PR #6954. Rank gives a lower
bound of 8, rechecked here. Twenty-six is not a minimum, and there is no new
kappa.
"""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
WORD_PATH = Path(__file__).resolve().parent / "WORD.json"
N = 8
SCALE_ROW = 0
SCALE = Fraction(-16)
SIGNED_DIAGONAL = tuple(Fraction(-1 if row in (0, 6) else 1) for row in range(N))


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def eye(size=N):
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def rows_of(raw):
    return [[Fraction(entry) for entry in row] for row in raw]


def matmul(left, right):
    width = len(right[0])
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(width)] for i in range(len(left))]


def apply_row(op, matrix):
    out = [row[:] for row in matrix]
    kind = op[0]
    if kind == "add":
        target, source, coefficient = op[1:]
        need(target != source and coefficient != 0, "a shear must be a nonzero off-diagonal")
        for column in range(len(out[0])):
            out[target][column] += coefficient * out[source][column]
    elif kind == "scale":
        target, coefficient = op[1:]
        need(coefficient not in (0, 1), "a scale must be a non-identity coefficient")
        for column in range(len(out[0])):
            out[target][column] *= coefficient
    elif kind == "swap":
        left, right_index = op[1], op[2]
        out[left], out[right_index] = out[right_index], out[left]
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
        left, right_index = op[1], op[2]
        matrix[left], matrix[right_index] = matrix[right_index], matrix[left]
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


def op_from_json(raw):
    if raw["op"] == "add":
        return ("add", raw["target"], raw["source"], parse_coefficient(raw["coefficient"]))
    if raw["op"] == "scale":
        return ("scale", raw["target"], parse_coefficient(raw["coefficient"]))
    raise AssertionError(raw["op"])


def rank(matrix):
    work = [row[:] for row in matrix]
    found = 0
    row_count = len(work)
    column_count = len(work[0])
    for column in range(column_count):
        pivot = next((row for row in range(found, row_count) if work[row][column] != 0), None)
        if pivot is None:
            continue
        work[found], work[pivot] = work[pivot], work[found]
        pivot_value = work[found][column]
        for row in range(row_count):
            if row != found and work[row][column] != 0:
                factor = work[row][column] / pivot_value
                for index in range(column_count):
                    work[row][index] -= factor * work[found][index]
        found += 1
    return found


def determinant(matrix):
    work = [row[:] for row in matrix]
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
        (left_row, left_column), (right_row, right_column) = off
        if (left_row == right_column and left_column == right_row
                and positions == {(left_row, left_row), (right_row, right_row),
                                  (left_row, left_column), (right_row, right_column)}
                and matrix[left_row][left_column] == 1
                and matrix[right_row][right_column] == 1
                and matrix[left_row][left_row] == 0
                and matrix[right_row][right_row] == 0):
            return ("swap", left_row, right_row)
    if len(diffs) == 1:
        row, column, value = diffs[0]
        if row == column:
            return ("scale", row, value)
        return ("add", row, column, value)
    raise AssertionError("factor is not one elementary letter")


def cleared_scale(matcher, scale_row):
    special = [row[:] for row in matcher]
    for column in range(N):
        special[scale_row][column] *= 1 / SCALE
    return special


def balanced_scale_ops(row_i, row_j, unit):
    """Four shears implementing diag(unit, 1/unit) on rows (row_i, row_j)."""
    unit = Fraction(unit)
    return (
        ("add", row_i, row_j, -1 / unit),
        ("add", row_j, row_i, unit - 1),
        ("add", row_i, row_j, 1),
        ("add", row_j, row_i, 1 / unit - 1),
    )


def record_add(work, reduction, counts, target, source, coefficient, kind):
    coefficient = Fraction(coefficient)
    if coefficient == 0:
        return
    for column in range(len(work)):
        work[target][column] += coefficient * work[source][column]
    reduction.append(("add", target, source, coefficient))
    counts[kind] += 1


def predecessor_reduction(matrix):
    """The merged 53-shear elimination: signed exchange, then balanced scale."""
    size = len(matrix)
    work = [row[:] for row in matrix]
    reduction = []
    counts = Counter()

    def add(target, source, coefficient, kind):
        record_add(work, reduction, counts, target, source, coefficient, kind)

    for column in range(size - 1):
        if work[column][column] == 0:
            source = next(row for row in range(column + 1, size) if work[row][column] != 0)
            add(column, source, 1, "exchange")
            add(source, column, -1, "exchange")
            add(column, source, 1, "exchange")
        pivot = work[column][column]
        need(pivot != 0, "predecessor pivot vanished")
        if pivot != 1:
            for op in balanced_scale_ops(column, column + 1, 1 / pivot):
                add(op[1], op[2], op[3], "balanced")
        for row in range(column + 1, size):
            if work[row][column] != 0:
                add(row, column, -work[row][column], "clear")
    need(work[size - 1][size - 1] == 1, "predecessor last pivot")
    for column in range(size - 1, -1, -1):
        for row in range(column):
            if work[row][column] != 0:
                add(row, column, -work[row][column], "back")
    need(work == eye(size), "predecessor reduction missed I")
    return reduction, counts


def canonical_reduction(matrix):
    """The column-ordered one-shear repair of open PR #7030, one branch only.

    This recomputes that branch's length. It does not rerun the repair-family
    census.
    """
    size = len(matrix)
    work = [row[:] for row in matrix]
    reduction = []
    counts = Counter()
    for column in range(size - 1):
        pivot = work[column][column]
        below = [row for row in range(column + 1, size) if work[row][column] != 0]
        if pivot != 1:
            need(below, "canonical repair has no lower nonzero at column %d" % column)
            record_add(work, reduction, counts, column, below[0],
                       (1 - pivot) / work[below[0]][column], "normalize")
        need(work[column][column] == 1, "canonical pivot did not become 1")
        for row in range(column + 1, size):
            if work[row][column] != 0:
                record_add(work, reduction, counts, row, column, -work[row][column], "clear")
    need(work[size - 1][size - 1] == 1, "canonical last pivot")
    for column in range(size - 1, -1, -1):
        for row in range(column):
            if work[row][column] != 0:
                record_add(work, reduction, counts, row, column, -work[row][column], "back")
    need(work == eye(size), "canonical reduction missed I")
    return reduction, counts


def forward_word(reduction, scale_row):
    shears = [("add", target, source, -coefficient)
              for _, target, source, coefficient in reversed(reduction)]
    return shears + [("scale", scale_row, SCALE)]


def conjugate_coefficient(coefficient, target, source, scale_row, scale):
    diagonal_target = scale if target == scale_row else Fraction(1)
    diagonal_source = scale if source == scale_row else Fraction(1)
    return coefficient * diagonal_target / diagonal_source


def scale_after_prefix(word, prefix_length):
    need(word[-1][0] == "scale", "conjugation expects a final scale")
    scale_row, scale = word[-1][1], word[-1][2]
    shears = word[:-1]
    prefix = list(shears[:prefix_length])
    suffix = [("add", target, source,
               conjugate_coefficient(coefficient, target, source, scale_row, scale))
              for _, target, source, coefficient in shears[prefix_length:]]
    return prefix + [("scale", scale_row, scale)] + suffix


def poly_add(left, right):
    total = dict(left)
    for key, value in right.items():
        total[key] = total.get(key, 0) + value
        if total[key] == 0:
            del total[key]
    return total


def poly_mul(left, right):
    total = {}
    for (i_left, j_left), left_value in left.items():
        for (i_right, j_right), right_value in right.items():
            key = (i_left + i_right, j_left + j_right)
            total[key] = total.get(key, 0) + left_value * right_value
            if total[key] == 0:
                del total[key]
    return total


def poly_const(value):
    value = Fraction(value)
    if value == 0:
        return {}
    return {(0, 0): value}


def poly_matmul(left, right):
    size = len(left)
    product_matrix = []
    for row in range(size):
        product_row = []
        for column in range(size):
            total = {}
            for index in range(size):
                total = poly_add(total, poly_mul(left[row][index], right[index][column]))
            product_row.append(total)
        product_matrix.append(product_row)
    return product_matrix


def shear_polynomial(target, source, variable):
    """I + c E_{target,source}, with c the indeterminate named by variable."""
    matrix = [[poly_const(int(row == column)) for column in range(N)] for row in range(N)]
    matrix[target][source] = poly_add(matrix[target][source], {variable: Fraction(1)})
    return matrix


def two_shear_diagonal_identity():
    """Every product of two shears changes at most one diagonal entry.

    For every ordered pair of positions, the diagonal of
    (I + a E_{t1,s1})(I + b E_{t2,s2}) is computed as a polynomial. Each
    diagonal polynomial is either the constant 1, or 1 + a b at exactly one
    index. The identity is exhaustive in the eight row indices and holds for
    every rational coefficient.
    """
    positions = [(target, source) for target in range(N) for source in range(N) if target != source]
    one = poly_const(1)
    ab = {(1, 1): Fraction(1)}
    changed_cases = 0
    for target_1, source_1 in positions:
        first = shear_polynomial(target_1, source_1, (1, 0))
        for target_2, source_2 in positions:
            second = shear_polynomial(target_2, source_2, (0, 1))
            product_matrix = poly_matmul(first, second)
            changed = []
            for row in range(N):
                diagonal = product_matrix[row][row]
                if diagonal == one:
                    continue
                need(diagonal == poly_add(one, ab),
                     "two-shear diagonal left the 1 + ab form at %s,%s -> %s"
                     % ((target_1, source_1), (target_2, source_2), diagonal))
                changed.append(row)
            need(len(changed) <= 1, "two shears changed more than one diagonal entry")
            if changed:
                changed_cases += 1
                need(changed == [target_1], "the ab term landed on an unexpected diagonal")
                need(source_1 == target_2 and target_1 == source_2,
                     "a diagonal change was not the reciprocal pair")
    need(changed_cases == N * (N - 1), "reciprocal pairs did not all change a diagonal")


def balanced_scale_identity():
    samples = (Fraction(2), Fraction(-16), Fraction(1, 2), Fraction(3, 7), Fraction(-1))
    for unit in samples:
        rows = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
        for op in balanced_scale_ops(0, 1, unit):
            target, source, coefficient = op[1:]
            rows[target] = [rows[target][k] + coefficient * rows[source][k] for k in range(2)]
        need(rows[0] == [unit, 0] and rows[1] == [0, 1 / unit],
             "balanced scale identity failed for %s" % unit)


def diagonal_entries(matrix):
    return tuple(matrix[row][row] for row in range(N))


def main():
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    need(selected["kappa"] == "781451/250000000", "selected kappa moved")
    payload = json.loads(RESULT.read_text(encoding="utf-8"))
    matcher = rows_of(payload["matcher"])
    need(determinant(matcher) == SCALE, "pinned determinant is not -16")

    published = [classify_matrix(factor) for factor in payload["right_route_factors"]]
    published_counts = Counter(op[0] for op in published)
    need(published_counts == Counter({"swap": 5, "scale": 5, "add": 14}),
         "pinned elimination counts changed")
    need(product(list(reversed(published))) == matcher, "pinned factors miss S")
    need(matrix_product(list(reversed(published))) == matcher,
         "matrix product of the pinned factors misses S")
    need(signature(published) == SCALE, "pinned signature misses det S")

    balanced_scale_identity()
    two_shear_diagonal_identity()

    special = cleared_scale(matcher, SCALE_ROW)
    need(determinant(special) == 1, "clearing the scale did not leave determinant 1")

    old_reduction, old_counts = predecessor_reduction(special)
    need(old_counts == Counter({"exchange": 15, "balanced": 28, "clear": 4, "back": 6}),
         "predecessor breakdown changed: %s" % dict(old_counts))
    need(len(old_reduction) == 53, "predecessor shear count changed")
    old_word = forward_word(old_reduction, SCALE_ROW)
    need(product(old_word) == matcher, "53-shear word misses S")

    repair, repair_counts = canonical_reduction(special)
    need(repair_counts == Counter({"normalize": 6, "clear": 10, "back": 13}),
         "canonical 29-shear breakdown changed: %s" % dict(repair_counts))
    need(len(repair) == 29, "canonical repair length changed")
    repair_word = forward_word(repair, SCALE_ROW)
    need(product(repair_word) == matcher, "29-shear repair misses S")
    need(matrix_product(repair_word) == matcher, "matrix product of the 29-shear repair misses S")

    frozen = json.loads(WORD_PATH.read_text(encoding="utf-8"))
    word = [op_from_json(raw) for raw in frozen["letters"]]
    shears = [op for op in word if op[0] == "add"]
    need(len(word) == 27 and len(shears) == 26, "frozen letter count")
    need(word[-1] == ("scale", SCALE_ROW, SCALE), "the unique scale is not the final letter")
    need(Counter(op[0] for op in word) == Counter({"add": 26, "scale": 1}), "letter counts")
    need(frozen["letter_counts"] == {"swap": 0, "scale": 1, "add": 26}, "frozen counts")
    need(frozen["scale_row"] == SCALE_ROW, "frozen scale row")
    need(parse_coefficient(frozen["scale_coefficient"]) == SCALE, "frozen scale coefficient")
    need(frozen["not_a_minimum"] is True, "the witness file must keep the minimum flag")
    denominators = sorted({op[3].denominator for op in shears})
    need(denominators == [1, 2, 4, 8, 16], "unexpected denominators %s" % denominators)
    need(product(word) == matcher, "26-shear word misses S")
    need(matrix_product(word) == matcher, "matrix product of the 26-shear word misses S")
    need(signature(word) == SCALE, "26-shear signature misses det S")
    need(product(shears) == special, "the shears do not rebuild D^{-1} S")
    need(len(shears) < len(repair) < len(old_reduction), "26 is not strictly under both predecessors")

    opening = shears[:4]
    opening_matrix = product(opening)
    need(diagonal_entries(opening_matrix) == SIGNED_DIAGONAL, "opening block is not the signed diagonal")
    need(all(opening_matrix[row][column] == 0
             for row in range(N) for column in range(N) if row != column),
         "opening block is not diagonal")
    balanced = list(balanced_scale_ops(0, 6, -1))
    need(len(balanced) == 4, "balanced scale of unit -1 is not four shears")
    need(product(balanced) == opening_matrix,
         "opening block differs from the balanced scale of unit -1")
    tail = shears[4:]
    need(len(tail) == 22, "tail length")
    # The tail is applied after the opening block: W = tail(opening(I)).
    need(product(opening + tail) == special, "opening plus tail misses D^{-1} S")
    signed_then_tail = opening_matrix
    for op in tail:
        signed_then_tail = apply_row(op, signed_then_tail)
    need(signed_then_tail == special, "the tail does not carry the signed diagonal to W")

    exchange = shears[18:21]
    need(exchange == [
        ("add", 6, 3, Fraction(1)),
        ("add", 3, 6, Fraction(-1)),
        ("add", 6, 3, Fraction(1)),
    ], "the signed-exchange block moved")
    exchange_matrix = product(exchange)
    four_shear_exchange = [
        ("add", 3, 6, Fraction(-2)),
        ("add", 6, 3, Fraction(1)),
        ("add", 3, 6, Fraction(-1)),
        ("add", 6, 3, Fraction(-1)),
    ]
    need(product(four_shear_exchange) == exchange_matrix,
         "the four-shear block is not the three-shear signed exchange")
    need(exchange_matrix[3] == [Fraction(int(column == 6)) * Fraction(-1) for column in range(N)],
         "signed exchange did not send row 3 to -row 6")
    need(exchange_matrix[6] == [Fraction(int(column == 3)) for column in range(N)],
         "signed exchange did not send row 6 to row 3")
    for row in range(N):
        if row in (3, 6):
            continue
        need(exchange_matrix[row] == [Fraction(int(column == row)) for column in range(N)],
             "signed exchange moved row %d" % row)
    longer = shears[:18] + four_shear_exchange + shears[21:]
    need(len(longer) == 27, "restoring the four-shear block did not give 27 shears")
    need(product(longer) == special, "the 27-shear expansion misses D^{-1} S")
    need(product(longer + [("scale", SCALE_ROW, SCALE)]) == matcher,
         "the 27-shear expansion misses S")
    expanded_tail = shears[4:18] + four_shear_exchange + shears[21:]
    need(len(expanded_tail) == 23, "expanded tail length")
    inverse_tail = [("add", target, source, -coefficient)
                    for _, target, source, coefficient in reversed(expanded_tail)]
    reduced = [row[:] for row in special]
    for op in inverse_tail:
        reduced = apply_row(op, reduced)
    need(diagonal_entries(reduced) == SIGNED_DIAGONAL and
         all(reduced[row][column] == 0 for row in range(N) for column in range(N) if row != column),
         "the inverse of the 23-shear tail does not reach the signed diagonal")
    inverse_opening = [("add", target, source, -coefficient)
                       for _, target, source, coefficient in reversed(opening)]
    finished = reduced
    for op in inverse_opening:
        finished = apply_row(op, finished)
    need(finished == eye(), "the inverse of the opening block does not finish at I")

    block = product(shears[7:11])
    nonunit_diagonal = [row for row in range(N) if block[row][row] != 1]
    need(nonunit_diagonal == [0, 1],
         "shears 7..10 no longer have exactly the two non-unit diagonal entries")
    # The polynomial identity already covers every coefficient, so this block
    # cannot be a product of two shears.

    for scale_row in range(N):
        cleared = cleared_scale(matcher, scale_row)
        difference = [[cleared[row][column] - Fraction(int(row == column))
                       for column in range(N)] for row in range(N)]
        need(rank(difference) == 8, "rank lower bound changed on row %d" % scale_row)
    witness_difference = [[special[row][column] - Fraction(int(row == column))
                           for column in range(N)] for row in range(N)]
    need(rank(witness_difference) == 8, "the witness matrix left the rank bound")
    need(len(shears) >= rank(witness_difference), "witness is below its own rank bound")

    for prefix in (0, 10, 26):
        moved = scale_after_prefix(word, prefix)
        need(sum(op[0] == "add" for op in moved) == 26, "moving the scale changed the shear count")
        need(sum(op[0] == "scale" for op in moved) == 1, "moving the scale duplicated it")
        need(product(moved) == matcher, "scale position %d misses S" % prefix)
        need(signature(moved) == SCALE, "scale position %d changes the determinant" % prefix)

    for index in range(len(word)):
        shortened = word[:index] + word[index + 1:]
        need(product(shortened) != matcher, "dropping letter %d still realized S" % index)
    for bad_scale in (Fraction(-8), Fraction(16)):
        mutated = list(word)
        mutated[-1] = ("scale", SCALE_ROW, bad_scale)
        need(product(mutated) != matcher, "scale %s still realized S" % bad_scale)
    mutated_shear = list(word)
    first = mutated_shear[0]
    need(first[0] == "add", "the witness does not start with a shear")
    mutated_shear[0] = ("add", first[1], first[2], first[3] + 1)
    need(product(mutated_shear) != matcher, "a shear coefficient change still realized S")
    need(product([]) == eye() and determinant(eye()) == 1, "identity control")
    need(signature(shears) == 1, "shears alone changed the determinant")

    print(
        "PASS_HELPER462_ONE_SCALE_26_SHEAR"
        " swaps=0 scales=1 scale_row=0 scale=-16 shears=26"
        " predecessor_shears=29 merged_53=53"
        " opening_balanced_scale=4 signed_exchange=3"
        " block_7_10_nonunit_diagonal=2 two_shear_diagonal_changes_at_most=1"
        " shear_denominators=1,2,4,8,16"
        " rank_lower_bound=8 minimum_claimed=0"
        " no_new_kappa=1 selected=781451/250000000"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""A 29-shear one-scale zero-swap word for the pinned helper-462 matcher.

The merged elimination has 53 shears. Replacing each signed exchange and each
4-shear balanced scale by a one-shear pivot repair produces a word with 29
shears and the same final scale by -16. A finite census of that repair family
finds nothing shorter. Rank gives a lower bound of 8. Neither number is a
minimum over every rational word, and there is no new kappa.
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


def published_word(factors):
    return [classify_matrix(factor) for factor in factors]


def cleared_scale(matcher, scale_row):
    """D^{-1} S, where D scales one row by -16. The result has determinant 1."""
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
    """The merged 53-shear elimination: signed exchange, then balanced scale.

    This is the procedure of research/helper462-one-scale-word. It is a
    comparison, not the witness.
    """
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


def repair_family_minimum(matrix):
    """Minimum shear count in one finite column-ordered repair family.

    Columns run from 0 through n-2, and the pivot row is the column index.
    If the pivot is already 1, the only continuation is to clear below it.
    If not, each strictly lower row with a nonzero in the column is one legal
    one-shear normalization. When the pivot is nonzero, each strictly lower
    row is also one legal 4-shear balanced scale. After the pivot equals 1,
    every nonzero strictly below it is cleared. Back-substitution then clears
    above the unit diagonal.

    A partial branch is discarded only when the shears already chosen are at
    least as many as a completed word. Every later shear adds a positive
    amount, so a discarded branch cannot contain a shorter completed word.
    The search starts with no incumbent, so the first completed word is
    accepted before any such discard.
    """
    size = len(matrix)
    best = [None]
    completed = [0]

    def consider(reduction):
        completed[0] += 1
        if best[0] is None or len(reduction) < len(best[0]):
            best[0] = list(reduction)

    def rec(work, column, reduction):
        if best[0] is not None and len(reduction) >= len(best[0]):
            return
        if column == size - 1:
            if work[size - 1][size - 1] != 1:
                return
            extra = []
            current = [row[:] for row in work]
            for back_column in range(size - 1, -1, -1):
                for row in range(back_column):
                    if current[row][back_column] == 0:
                        continue
                    coefficient = -current[row][back_column]
                    for index in range(size):
                        current[row][index] += coefficient * current[back_column][index]
                    extra.append(("add", row, back_column, coefficient))
            if current != eye(size):
                return
            if best[0] is not None and len(reduction) + len(extra) >= len(best[0]):
                return
            consider(reduction + extra)
            return
        pivot = work[column][column]
        below = [row for row in range(column + 1, size) if work[row][column] != 0]
        options = []
        if pivot == 1:
            options.append(("ready", None))
        else:
            for row in below:
                options.append(("normalize", row))
            if pivot != 0:
                for row in range(column + 1, size):
                    options.append(("balanced", row))
        for kind, partner in options:
            current = [row[:] for row in work]
            chosen = list(reduction)

            def add(target, source, coefficient):
                coefficient = Fraction(coefficient)
                if coefficient == 0:
                    return
                for index in range(size):
                    current[target][index] += coefficient * current[source][index]
                chosen.append(("add", target, source, coefficient))

            if kind == "normalize":
                add(column, partner, (1 - pivot) / current[partner][column])
            elif kind == "balanced":
                for op in balanced_scale_ops(column, partner, 1 / pivot):
                    add(op[1], op[2], op[3])
            if current[column][column] != 1:
                continue
            for row in range(column + 1, size):
                if current[row][column] != 0:
                    add(row, column, -current[row][column])
            rec(current, column + 1, chosen)

    rec([row[:] for row in matrix], 0, [])
    need(best[0] is not None and completed[0] >= 1, "repair family produced no word")
    return len(best[0]), completed[0]


def canonical_reduction(matrix):
    """One branch of the repair family: normalize from the first lower nonzero.

    On this matcher that branch never needs a balanced scale. The counts are
    part of the witness, so a missing helper is a failure rather than a silent
    fallback.
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
    """Reverse and negate the reduction, then append the unique scale."""
    shears = [("add", target, source, -coefficient)
              for _, target, source, coefficient in reversed(reduction)]
    return shears + [("scale", scale_row, SCALE)]


def conjugate_coefficient(coefficient, target, source, scale_row, scale):
    """D E_{target,source}(c) D^{-1} multiplies c by d_target / d_source."""
    diagonal_target = scale if target == scale_row else Fraction(1)
    diagonal_source = scale if source == scale_row else Fraction(1)
    return coefficient * diagonal_target / diagonal_source


def scale_after_prefix(word, prefix_length):
    """Move the final scale to sit after the first prefix_length shears.

    Shears that follow the scale are replaced by their conjugates D E D^{-1}.
    Shears that precede the scale keep their coefficients. The shear count
    does not change.
    """
    need(word[-1][0] == "scale", "conjugation expects a final scale")
    scale_row, scale = word[-1][1], word[-1][2]
    shears = word[:-1]
    prefix = list(shears[:prefix_length])
    suffix = [("add", target, source,
               conjugate_coefficient(coefficient, target, source, scale_row, scale))
              for _, target, source, coefficient in shears[prefix_length:]]
    return prefix + [("scale", scale_row, scale)] + suffix


def scale_to_end(word):
    """Move a middle scale to the end by the inverse conjugation.

    A word with matrix product B D A equals D (D^{-1} B D) A. The shears that
    followed the scale are conjugated by D^{-1}; the shears that preceded it
    stay put. The result is a scale-last word of the same shear count.
    """
    index = next(position for position, op in enumerate(word) if op[0] == "scale")
    need(sum(op[0] == "scale" for op in word) == 1, "scale_to_end expects one scale")
    scale_row, scale = word[index][1], word[index][2]
    before = list(word[:index])
    after = []
    for op in word[index + 1:]:
        need(op[0] == "add", "a shear word contains a non-shear after the scale")
        target, source, coefficient = op[1:]
        diagonal_target = scale if target == scale_row else Fraction(1)
        diagonal_source = scale if source == scale_row else Fraction(1)
        after.append(("add", target, source, coefficient * diagonal_source / diagonal_target))
    return before + after + [("scale", scale_row, scale)]


def balanced_scale_identity():
    samples = (Fraction(2), Fraction(-16), Fraction(1, 2), Fraction(3, 7), Fraction(-1))
    for unit in samples:
        rows = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)]]
        for op in balanced_scale_ops(0, 1, unit):
            target, source, coefficient = op[1:]
            rows[target] = [rows[target][k] + coefficient * rows[source][k] for k in range(2)]
        need(rows[0] == [unit, 0] and rows[1] == [0, 1 / unit],
             "balanced scale identity failed for %s" % unit)
    need(len(balanced_scale_ops(0, 1, Fraction(2))) == 4, "balanced scale is not four shears")


def rank_subadditivity_control():
    """rank(XY - I) <= rank(X - I) + rank(Y - I) on one explicit shear pair.

    The same bound says diag(2, 1/2) needs at least two shears. The balanced
    scale realizes it in four, which meets the bound and does not sharpen it.
    """
    first = elementary_matrix(("add", 0, 1, Fraction(3)))
    second = elementary_matrix(("add", 1, 2, Fraction(-5)))
    product_matrix = matmul(second, first)
    difference = [[product_matrix[row][column] - Fraction(int(row == column))
                   for column in range(N)] for row in range(N)]
    need(1 <= rank(difference) <= 2, "two shears left the rank bound")
    paired = eye()
    paired[0][0] = Fraction(2)
    paired[1][1] = Fraction(1, 2)
    paired_difference = [[paired[row][column] - Fraction(int(row == column))
                          for column in range(N)] for row in range(N)]
    word = list(balanced_scale_ops(0, 1, 2))
    built = product(word)
    need(built[0][0] == 2 and built[1][1] == Fraction(1, 2),
         "balanced scale did not build diag(2, 1/2)")
    need(all(built[row][column] == 0 for row in range(2) for column in range(2) if row != column),
         "balanced scale left an off-diagonal entry")
    need(len(word) == 4 and rank(paired_difference) == 2, "rank control on the diagonal")


def opening_column_obstruction(special):
    """The empty permutation probe rejected this matrix before building a word.

    Columns 0 and 1 each have a single entry, and that entry is 2. A rule that
    pivots only on an already nonzero row, and then demands a second nonzero in
    the same column before it will change 2 into 1, has no move on either
    column. The 29-shear word does the opposite: its first shear writes into
    row 0, whose column-0 entry is 0.
    """
    for column in (0, 1):
        nonzero = [(row, special[row][column]) for row in range(N) if special[row][column] != 0]
        need(nonzero == [((5 if column == 0 else 6), Fraction(2))],
             "opening column %d is no longer a single 2" % column)
    need(special[0][0] == 0, "row 0 is no longer the zero destination of the first shear")


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
    need(product(list(reversed(published))) == matcher, "pinned factors miss S")
    need(matrix_product(list(reversed(published))) == matcher,
         "matrix product of the pinned factors misses S")
    need(signature(published) == SCALE, "pinned signature misses det S")

    balanced_scale_identity()
    rank_subadditivity_control()

    special = cleared_scale(matcher, SCALE_ROW)
    need(determinant(special) == 1, "clearing the scale did not leave determinant 1")
    opening_column_obstruction(special)

    old_reduction, old_counts = predecessor_reduction(special)
    need(old_counts == Counter({"exchange": 15, "balanced": 28, "clear": 4, "back": 6}),
         "predecessor breakdown changed: %s" % dict(old_counts))
    need(len(old_reduction) == 53, "predecessor shear count changed")
    old_word = forward_word(old_reduction, SCALE_ROW)
    need(product(old_word) == matcher, "predecessor word misses S")

    reduction, counts = canonical_reduction(special)
    need(counts == Counter({"normalize": 6, "clear": 10, "back": 13}),
         "canonical breakdown changed: %s" % dict(counts))
    need(counts["balanced"] == 0 and counts["exchange"] == 0,
         "canonical word still uses a balanced scale or a signed exchange")
    word = forward_word(reduction, SCALE_ROW)
    need(len(word) == 30 and sum(op[0] == "add" for op in word) == 29, "canonical length")
    need(product(word) == matcher, "29-shear word misses S")
    need(matrix_product(word) == matcher, "matrix product of the 29-shear word misses S")
    need(word[-1] == ("scale", SCALE_ROW, SCALE), "the unique scale is not the final letter")
    need(signature(word) == SCALE, "29-shear signature misses det S")
    need(Counter(op[0] for op in word) == Counter({"add": 29, "scale": 1}), "letter counts")
    denominators = sorted({op[3].denominator for op in word if op[0] == "add"})
    need(denominators == [1, 2, 4, 8, 16], "unexpected denominators %s" % denominators)
    need(len(word) < len(old_word), "new word is not strictly shorter")

    frozen = json.loads(WORD_PATH.read_text(encoding="utf-8"))
    frozen_ops = [op_from_json(raw) for raw in frozen["letters"]]
    need(frozen_ops == word, "WORD.json differs from the canonical word")
    need(frozen["scale_row"] == SCALE_ROW, "frozen scale row")
    need(parse_coefficient(frozen["scale_coefficient"]) == SCALE, "frozen scale coefficient")
    need(frozen["letter_counts"] == {"swap": 0, "scale": 1, "add": 29}, "frozen counts")

    family_minimum, completed = repair_family_minimum(special)
    need(family_minimum == 29, "repair family minimum changed to %s" % family_minimum)
    need(completed >= 1, "census completed no word")
    # The same minimum on every scale row. Row 2 is the one exception in this
    # family; it is recorded rather than used as the witness.
    family_by_row = {}
    for scale_row in range(N):
        family_by_row[scale_row] = repair_family_minimum(cleared_scale(matcher, scale_row))[0]
    need(family_by_row == {0: 29, 1: 29, 2: 30, 3: 29, 4: 29, 5: 29, 6: 29, 7: 29},
         "per-row family minima changed: %s" % family_by_row)

    for prefix in (0, 10, 29):
        moved = scale_after_prefix(word, prefix)
        need(sum(op[0] == "add" for op in moved) == 29, "moving the scale changed the shear count")
        need(Counter(op[0] for op in moved)["scale"] == 1, "moving the scale duplicated it")
        need(product(moved) == matcher, "scale position %d misses S" % prefix)
        need(signature(moved) == SCALE, "scale position %d changes the determinant" % prefix)
        restored = scale_to_end(moved)
        need(sum(op[0] == "add" for op in restored) == 29, "restoring the scale changed the shear count")
        need(product(restored) == matcher, "restoring the scale at position %d misses S" % prefix)
        need(restored[-1] == ("scale", SCALE_ROW, SCALE), "restored scale is not last")

    for scale_row in range(N):
        cleared = cleared_scale(matcher, scale_row)
        difference = [[cleared[row][column] - Fraction(int(row == column))
                       for column in range(N)] for row in range(N)]
        need(rank(difference) == 8, "rank lower bound changed on row %d" % scale_row)
    shear_only = [op for op in word if op[0] == "add"]
    need(product(shear_only) == special, "the shears do not rebuild D^{-1} S")
    shear_difference = [[special[row][column] - Fraction(int(row == column))
                         for column in range(N)] for row in range(N)]
    need(rank(shear_difference) == 8, "the witness matrix left the rank bound")
    need(len(shear_only) >= rank(shear_difference), "witness is below its own rank bound")

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
    need(signature(shear_only) == 1, "shears alone changed the determinant")

    print(
        "PASS_HELPER462_ONE_SCALE_FEWER_SHEARS"
        " swaps=0 scales=1 scale_row=0 scale=-16 shears=29"
        " predecessor_shears=53 family_minimum=29"
        " normalize=6 clear=10 back=13 balanced=0 exchange=0"
        " shear_denominators=1,2,4,8,16"
        " rank_lower_bound=8 minimum_claimed=0"
        " no_new_kappa=1 selected=781451/250000000"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Elementary rank-drop depth for one-scale zero-swap helper-462 words.

Subadditivity of rank(W - I) gives 8 and is attained by the matrix. The
rank-drop tree is a different invariant. On every scale row its depth is at
most 2, so no word in the inherited alphabet has exactly 8 shears. The lower
bound is therefore 9. No new kappa is claimed.

Standard library only. Controls use an explicit failure function so they stay
active under python -O.
"""

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/bit-completed-backend-api/science/RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
WORD_PATH = Path(__file__).resolve().parent / "WORD.json"
N = 8
SCALE = Fraction(-16)
SOURCE_COMMIT = "98238eeed3faca9f0a5f1d4060db5d5da524a192"

# Exhaustive census fingerprint. Ranks that are omitted are zero.
EXPECTED = {
    0: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 33, 6: 37}, "edges": {8: 33, 7: 37}},
    1: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 33, 6: 37}, "edges": {8: 33, 7: 37}},
    2: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 33, 6: 37}, "edges": {8: 33, 7: 37}},
    3: {"depth": 1, "det": "21/8", "nodes": {8: 1, 7: 38}, "edges": {8: 38}},
    4: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 33, 6: 37}, "edges": {8: 33, 7: 37}},
    5: {"depth": 2, "det": "1/2", "nodes": {8: 1, 7: 36, 6: 4}, "edges": {8: 36, 7: 4}},
    6: {"depth": 1, "det": "21/8", "nodes": {8: 1, 7: 38}, "edges": {8: 38}},
    7: {"depth": 1, "det": "19/4", "nodes": {8: 1, 7: 48}, "edges": {8: 48}},
}

# A tight positive control: eight elementary shears whose partial products
# have rank distance 0, 1, ..., 8 from I. The same two peel rules must
# recover this word from the outside.
TIGHT_WORD = (
    (0, 1, Fraction(-1)),
    (1, 0, Fraction(1, 2)),
    (2, 3, Fraction(1)),
    (3, 2, Fraction(2)),
    (4, 5, Fraction(1)),
    (5, 4, Fraction(3)),
    (6, 7, Fraction(3)),
    (7, 6, Fraction(3)),
)


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def eye(size):
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def rows_of(raw):
    return [[Fraction(entry) for entry in row] for row in raw]


def matmul(left, right):
    width = len(right)
    return [[sum(left[i][k] * right[k][j] for k in range(width))
             for j in range(len(right[0]))] for i in range(len(left))]


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


def rank_of(matrix):
    work = [row[:] for row in matrix]
    height = len(work)
    width = len(work[0])
    rank = 0
    column = 0
    while rank < height and column < width:
        pivot = next((row for row in range(rank, height) if work[row][column] != 0), None)
        if pivot is None:
            column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        for row in range(height):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for index in range(column, width):
                work[row][index] -= factor * work[rank][index]
        rank += 1
        column += 1
    return rank


def difference(matrix):
    return [[matrix[i][j] - (1 if i == j else 0) for j in range(len(matrix))]
            for i in range(len(matrix))]


def apply_shear(matrix, target, source, coefficient):
    out = [row[:] for row in matrix]
    for column in range(len(matrix)):
        out[target][column] += coefficient * out[source][column]
    return out


def apply_scale(matrix, target, coefficient):
    out = [row[:] for row in matrix]
    for column in range(len(matrix)):
        out[target][column] *= coefficient
    return out


def minor(matrix, rows, cols):
    return determinant([[matrix[row][col] for col in cols] for row in rows])


def solve(matrix, rhs):
    """One solution of matrix x = rhs, or None if the system is inconsistent.

    Free variables are set to 0. Callers that use the pairing y^T u rely on
    that pairing being independent of this choice, which the proof records.
    """
    size = len(matrix)
    work = [matrix[row][:] + [rhs[row]] for row in range(size)]
    pivot_of_column = {}
    row = 0
    column = 0
    while row < size and column < size:
        pivot = next((index for index in range(row, size) if work[index][column] != 0), None)
        if pivot is None:
            column += 1
            continue
        work[row], work[pivot] = work[pivot], work[row]
        pivot_value = work[row][column]
        for index in range(size):
            if index == row or work[index][column] == 0:
                continue
            factor = work[index][column] / pivot_value
            for cursor in range(column, size + 1):
                work[index][cursor] -= factor * work[row][cursor]
        pivot_of_column[column] = row
        row += 1
        column += 1
    for index in range(size):
        if all(work[index][cursor] == 0 for cursor in range(size)) and work[index][size] != 0:
            return None
    solution = [Fraction(0) for _ in range(size)]
    for column, index in pivot_of_column.items():
        solution[column] = work[index][size] / work[index][column]
    return solution


def cancelling_coefficient_by_minors(matrix, target, source, rank):
    """Unique c with rank(M - c E_target,source) = rank - 1, or None.

    Every maximal minor is affine in c. A nonconstant minor has one root, and
    any common root of all maximal minors would have to be that root.
    """
    size = len(matrix)
    other_rows = [index for index in range(size) if index != target]
    other_columns = [index for index in range(size) if index != source]
    for row_rest in combinations(other_rows, rank - 1):
        rows = tuple(sorted((target, *row_rest)))
        for column_rest in combinations(other_columns, rank - 1):
            columns = tuple(sorted((source, *column_rest)))
            value_at_zero = minor(matrix, rows, columns)
            saved = matrix[target][source]
            matrix[target][source] = saved - 1
            value_at_one = minor(matrix, rows, columns)
            matrix[target][source] = saved
            if value_at_zero != value_at_one:
                coefficient = value_at_zero / (value_at_zero - value_at_one)
                if coefficient == 0:
                    return None
                matrix[target][source] = saved - coefficient
                dropped = rank_of(matrix)
                matrix[target][source] = saved
                if dropped != rank - 1:
                    return None
                return coefficient
            if value_at_zero != 0:
                return None
    return None


def cancelling_coefficient_by_pairing(matrix, target, source):
    """c = 1 / (y^T e_target) when e_target is in the column space and
    e_source is in the row space. None when either membership fails or the
    pairing is zero.
    """
    size = len(matrix)
    target_vector = [Fraction(int(index == target)) for index in range(size)]
    source_vector = [Fraction(int(index == source)) for index in range(size)]
    if solve(matrix, target_vector) is None:
        return None
    transpose = [[matrix[column][row] for column in range(size)] for row in range(size)]
    left = solve(transpose, source_vector)
    if left is None:
        return None
    pairing = left[target]
    if pairing == 0:
        return None
    return 1 / pairing


def rank_drop_steps(matrix):
    """Legal left rank-drop steps, as (target, source, coefficient).

    The minor test and the pairing test must agree on every edge. Each
    returned step decreases rank(· - I) by exactly one.
    """
    gap = difference(matrix)
    rank = rank_of(gap)
    need(rank >= 1, "a rank-drop step was requested at the identity")
    steps = []
    size = len(matrix)
    for target in range(size):
        for source in range(size):
            if target == source:
                continue
            by_minors = cancelling_coefficient_by_minors(gap, target, source, rank)
            by_pairing = cancelling_coefficient_by_pairing(gap, target, source)
            if by_pairing is not None:
                updated = [row[:] for row in gap]
                updated[target][source] -= by_pairing
                if rank_of(updated) != rank - 1:
                    by_pairing = None
            need(by_minors == by_pairing,
                 "minor and pairing rules disagreed on edge %d <- %d" % (target, source))
            if by_minors is None:
                continue
            steps.append((target, source, by_minors))
    return rank, steps


def left_peel(matrix, target, source, coefficient):
    """Left-multiply by the inverse shear I - c E_target,source."""
    return apply_shear(matrix, target, source, -coefficient)


def census(matrix):
    """Expand the whole rank-drop tree. Rank decreases, so there is no cycle."""
    nodes = {}
    edges = {}
    depth = 0
    reached_identity = False

    def walk(current, rank, chain):
        nonlocal depth, reached_identity
        nodes[rank] = nodes.get(rank, 0) + 1
        if chain > depth:
            depth = chain
        if rank == 0:
            reached_identity = True
            edges[rank] = edges.get(rank, 0)
            return
        found_rank, steps = rank_drop_steps(current)
        need(found_rank == rank, "rank changed between a node and its edge list")
        edges[rank] = edges.get(rank, 0) + len(steps)
        for target, source, coefficient in steps:
            child = left_peel(current, target, source, coefficient)
            need(determinant(child) == 1, "a rank-drop child left SL")
            child_rank = rank_of(difference(child))
            need(child_rank == rank - 1, "a reported step did not drop the rank by 1")
            walk(child, child_rank, chain + 1)

    start = rank_of(difference(matrix))
    walk(matrix, start, 0)
    return {
        "rank": start,
        "depth": depth,
        "nodes": nodes,
        "edges": edges,
        "reached_identity": reached_identity,
    }


def support(counts, keys):
    return {key: counts.get(key, 0) for key in keys}


def scale_cleared(matcher, scale_row):
    matrix = [row[:] for row in matcher]
    for column in range(N):
        matrix[scale_row][column] /= SCALE
    return matrix


def product_of_letters(letters):
    matrix = eye(N)
    for letter in letters:
        kind = letter["op"]
        if kind == "add":
            target = letter["target"]
            source = letter["source"]
            need(target != source, "recorded shear uses one row twice")
            matrix = apply_shear(matrix, target, source, Fraction(letter["coefficient"]))
        elif kind == "scale":
            matrix = apply_scale(matrix, letter["target"], Fraction(letter["coefficient"]))
        else:
            raise SystemExit("FAIL: recorded word has a letter outside the shear/scale alphabet")
    return matrix


def diagonal_entry(scale_row, index):
    if index == scale_row:
        return SCALE
    return Fraction(1)


def conjugate_after_scale(coefficient, target, source, scale_row):
    """Coefficient of D E D^{-1}, used when a shear moves to the left of D."""
    return coefficient * diagonal_entry(scale_row, target) / diagonal_entry(scale_row, source)


def conjugate_before_scale(coefficient, target, source, scale_row):
    """Coefficient of D^{-1} E D, used when a shear moves to the right of D."""
    return coefficient * diagonal_entry(scale_row, source) / diagonal_entry(scale_row, target)


def move_scale(letters, prefix_length, scale_row):
    """Move the final scale to sit after prefix_length shears.

    Shears that end up to the right of the scale are conjugated by D.
    """
    shears = letters[:-1]
    scale = letters[-1]
    need(scale["op"] == "scale" and scale["target"] == scale_row, "the recorded scale moved")
    need(0 <= prefix_length <= len(shears), "scale insertion point is outside the word")
    moved = []
    for index, letter in enumerate(shears):
        coefficient = Fraction(letter["coefficient"])
        if index >= prefix_length:
            coefficient = conjugate_after_scale(
                coefficient, letter["target"], letter["source"], scale_row)
        moved.append({
            "op": "add",
            "target": letter["target"],
            "source": letter["source"],
            "coefficient": str(coefficient),
        })
    moved.insert(prefix_length, dict(scale))
    return moved


def scale_to_end(letters, scale_row):
    """Move the unique scale to the end by conjugating every later shear.

    A word with matrix S_suffix D S_prefix becomes D (D^{-1} S_suffix D) S_prefix.
    """
    index = next(position for position, letter in enumerate(letters) if letter["op"] == "scale")
    prefix = letters[:index]
    suffix = letters[index + 1:]
    scale = letters[index]
    moved = [dict(letter) for letter in prefix]
    for letter in suffix:
        need(letter["op"] == "add", "a letter after the scale is not a shear")
        coefficient = conjugate_before_scale(
            Fraction(letter["coefficient"]), letter["target"], letter["source"], scale_row)
        moved.append({
            "op": "add",
            "target": letter["target"],
            "source": letter["source"],
            "coefficient": str(coefficient),
        })
    moved.append(dict(scale))
    return moved


def balanced_scale(unit):
    """Four shears sending (R, S) to (u R, S/u) on a 2 by 2 identity."""
    return (
        (0, 1, -1 / unit),
        (1, 0, unit - 1),
        (0, 1, Fraction(1)),
        (1, 0, 1 / unit - 1),
    )


def apply_word(word, size):
    matrix = eye(size)
    for target, source, coefficient in word:
        matrix = apply_shear(matrix, target, source, coefficient)
    return matrix


def replay_tight_word():
    matrix = apply_word(TIGHT_WORD, N)
    need(determinant(matrix) == 1, "tight control left SL(8)")
    need(rank_of(difference(matrix)) == N, "tight control does not meet rank distance 8")
    current = matrix
    for target, source, coefficient in reversed(TIGHT_WORD):
        rank, steps = rank_drop_steps(current)
        need((target, source, coefficient) in steps,
             "tight control shear %d <- %d was not a rank-drop step" % (target, source))
        current = left_peel(current, target, source, coefficient)
        need(rank_of(difference(current)) == rank - 1, "tight control peel missed a rank")
    need(current == eye(N), "tight control did not peel back to I")


def two_by_two_gap():
    unit = Fraction(2)
    matrix = apply_word(balanced_scale(unit), 2)
    need(matrix == [[unit, 0], [0, 1 / unit]], "balanced scale missed diag(2, 1/2)")
    gap = difference(matrix)
    need(rank_of(gap) == 2, "diag(2, 1/2) left rank distance 2")
    rank, steps = rank_drop_steps(matrix)
    need(rank == 2 and steps == [], "diag(2, 1/2) acquired a length-2 shear factorization")


def subadditivity_samples():
    first = apply_shear(eye(N), 0, 1, Fraction(3))
    second = apply_shear(eye(N), 2, 3, Fraction(-1, 4))
    need(rank_of(difference(first)) == 1, "one shear left rank distance 1")
    product = matmul(second, first)
    need(rank_of(difference(product)) <= 2, "two shears exceeded rank subadditivity")


def main():
    selected = json.loads(SELECTED.read_text())
    need(selected["kappa"] == "781451/250000000", "selected kappa changed")
    payload = json.loads(RESULT.read_text())
    matcher = rows_of(payload["matcher"])
    need(determinant(matcher) == SCALE, "pinned determinant is not -16")
    factors = rows_of_factors(payload["right_route_factors"])
    need(len(factors) == 24, "published route no longer has 24 factors")
    published = eye(N)
    for factor in factors:
        published = matmul(published, factor)
    need(published == matcher, "published right-route factors miss S")

    recorded = json.loads(WORD_PATH.read_text())
    need(recorded["source_commit"] == SOURCE_COMMIT, "recorded word names a different commit")
    need(recorded["source_pr"] == 7030, "recorded word names a different PR")
    letters = recorded["letters"]
    need(recorded["letter_counts"] == {"swap": 0, "scale": 1, "add": 29}, "recorded counts changed")
    need(len(letters) == 30, "recorded word length changed")
    need(letters[-1] == {"op": "scale", "target": 0, "coefficient": "-16"},
         "recorded scale is not the final -16 on row 0")
    need(product_of_letters(letters) == matcher, "recorded 29-shear word misses S")
    shears_only = product_of_letters(letters[:-1])
    cleared = scale_cleared(matcher, 0)
    need(shears_only == cleared, "recorded shears are not D^{-1} S for row 0")
    for prefix in (0, 10):
        moved = move_scale(letters, prefix, 0)
        need(sum(1 for letter in moved if letter["op"] == "add") == 29,
             "moving the scale changed the shear count")
        need(product_of_letters(moved) == matcher,
             "moving the scale off the end missed S at prefix %d" % prefix)
        restored = scale_to_end(moved, 0)
        need(sum(1 for letter in restored if letter["op"] == "add") == 29,
             "returning the scale to the end changed the shear count")
        need(product_of_letters(restored) == matcher,
             "returning the scale to the end missed S at prefix %d" % prefix)
        need(product_of_letters(restored[:-1]) == cleared,
             "the restored shear block is not D^{-1} S at prefix %d" % prefix)

    mutated = [dict(letter) for letter in letters]
    mutated[-1] = {"op": "scale", "target": 0, "coefficient": "-8"}
    need(product_of_letters(mutated) != matcher, "scale -8 still realized S")
    mutated = [dict(letter) for letter in letters]
    mutated[0] = dict(mutated[0])
    mutated[0]["coefficient"] = str(Fraction(mutated[0]["coefficient"]) + 1)
    need(product_of_letters(mutated) != matcher, "changing the first shear still realized S")
    shortened = letters[1:]
    need(product_of_letters(shortened) != matcher, "dropping the first shear still realized S")

    subadditivity_samples()
    replay_tight_word()
    two_by_two_gap()

    depths = []
    for scale_row in range(N):
        matrix = scale_cleared(matcher, scale_row)
        need(determinant(matrix) == 1, "cleared matrix on row %d left SL" % scale_row)
        report = census(matrix)
        expected = EXPECTED[scale_row]
        need(report["rank"] == N, "rank(D^{-1} S - I) is not 8 on row %d" % scale_row)
        need(str(determinant(difference(matrix))) == expected["det"],
             "det(D^{-1} S - I) changed on row %d" % scale_row)
        need(report["depth"] == expected["depth"],
             "rank-drop depth changed on row %d" % scale_row)
        need(not report["reached_identity"],
             "an 8-shear factorization appeared on row %d" % scale_row)
        need(support(report["nodes"], range(N + 1)) == support(expected["nodes"], range(N + 1)),
             "rank-drop node counts changed on row %d: %s" % (scale_row, report["nodes"]))
        need(support(report["edges"], range(N + 1)) == support(expected["edges"], range(N + 1)),
             "rank-drop edge counts changed on row %d: %s" % (scale_row, report["edges"]))
        need(report["depth"] < report["rank"], "depth did not stay strictly below the rank")
        depths.append(report["depth"])

    need(depths[0] == 2, "the recorded word's matrix does not have depth 2")
    need(max(depths) <= 2, "some scale row still has a long rank-drop chain")
    print(
        "PASS_HELPER462_ONE_SCALE_RANK_DROP"
        " lower_bound=9 subadditive_bound=8 recorded_depth=2"
        " max_depth=%d upper_bound=29 kappa=781451/250000000" % max(depths)
    )


def rows_of_factors(raw_factors):
    return [[[Fraction(entry) for entry in row] for row in factor] for factor in raw_factors]


if __name__ == "__main__":
    main()

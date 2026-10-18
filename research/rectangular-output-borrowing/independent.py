#!/usr/bin/env python3
"""Independent exact integer oracle and complete 2-by-2 minimum-word census.

This module never imports the schedule emitter or its polynomial checker.
Operations are (sign, factor_name, source_row, target_row).  Dense matrices
act on column vectors on the left, using unbounded Python integers.
"""

from collections import Counter, defaultdict
from itertools import permutations
from math import comb, factorial
import json
import random


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def matvec(matrix, vector):
    """A deliberately direct, exact matrix-vector multiplication."""
    if len(matrix) != len(vector) or any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix and vector dimensions differ")
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def product_matrix(factors, matrices):
    """Compose factors in application order, independently by basis columns."""
    factors = list(factors)
    if not factors:
        raise ValueError("an identity product needs an explicit dimension")
    dimension = len(matrices[factors[0]])
    columns = []
    for column in range(dimension):
        vector = [int(row == column) for row in range(dimension)]
        for name in factors:
            vector = matvec(matrices[name], vector)
        columns.append(vector)
    return [[columns[column][row] for column in range(dimension)]
            for row in range(dimension)]


def evaluate(operations, rows, matrices):
    """Return (new_rows, largest_absolute_integer_seen).

    The maximum includes every scalar product, partial dot accumulator, and
    row value, so it also checks intermediate scalar arithmetic widths.
    Inputs are copied and never modified.  There are no floating-point or
    modular operations, and zero/singular matrices are admitted.
    """
    state = [list(row) for row in rows]
    if not state or not state[0] or any(len(row) != len(state[0]) for row in state):
        raise ValueError("rows must have one common positive dimension")
    peak = max(abs(value) for row in state for value in row)
    for sign, factor, source, target in operations:
        if sign not in (-1, 1) or source == target:
            raise ValueError("each operation needs a unit sign and distinct ports")
        if not (0 <= source < len(state) and 0 <= target < len(state)):
            raise ValueError("row index out of bounds")
        matrix = matrices[factor]
        if len(matrix) != len(state[0]) or any(len(row) != len(state[0]) for row in matrix):
            raise ValueError("matrix and row dimensions differ")
        for coordinate, coefficients in enumerate(matrix):
            accumulator = 0
            for coefficient, value in zip(coefficients, state[source]):
                term = coefficient * value
                accumulator += term
                peak = max(peak, abs(term), abs(accumulator))
            state[target][coordinate] += sign * accumulator
            peak = max(peak, abs(state[target][coordinate]))
    return state, peak


def expected(rows, m, k, matrices):
    """Direct rectangular map; extra scratch rows keep their incoming values.

    ``matrices`` contains the complete operators B0..B(m-1), A0..A(k-1).
    This oracle evaluates the formula, without reading or deriving a schedule.
    """
    if m < 1 or k < 2 or len(rows) < m + k:
        raise ValueError("need m >= 1 sources and k >= 2 outputs")
    result = [list(row) for row in rows]
    combined = [0] * len(rows[0])
    for source in range(m):
        for coordinate, value in enumerate(matvec(matrices[f"B{source}"], rows[source])):
            combined[coordinate] += value
    for output in range(k):
        increment = matvec(matrices[f"A{output}"], combined)
        result[m + output] = [a + b for a, b in zip(rows[m + output], increment)]
    return result


def closed_head_travel(operations, row_count, factor_names, length):
    """Independent closed invoice for the documented data-tape layout.

    Data precede coefficient matrices in sorted name order.  Every term visits
    its coefficient then its source entry, every dot product then visits its
    target entry, and every leaf starts and ends at slot zero.  Coefficients
    lie above all data, so every coefficient/data distance has known sign;
    only the final source-to-target jump of each dot product needs abs().
    """
    if length < 1 or row_count < 2:
        raise ValueError("invalid tape dimensions")
    factor_index = {name: index for index, name in enumerate(sorted(factor_names))}
    total = 0
    for _, name, source, target in operations:
        c = row_count * length + factor_index[name] * length * length
        s, t = source * length, target * length
        total += (2 * length**2 * c + length**3 * (length - 1)
                  - length * (2 * length - 1) * s + (2 - length) * t
                  + (length - 1) * (length + 4) // 2
                  + sum(abs(t - s - length + 1 + i) for i in range(length)))
    return total


def _free_evaluate(operations, row_count):
    """Tiny separate free-module oracle used only by the finite census.

    A term key is (original_input_row, tuple_of_left_to_right_factors).
    Every row begins as an independent formal input; zero terms are deleted.
    """
    state = [{(row, ()): 1} for row in range(row_count)]
    for sign, factor, source, target in operations:
        destination = state[target].copy()
        for (original, word), coefficient in state[source].items():
            key = original, (factor,) + word
            destination[key] = destination.get(key, 0) + sign * coefficient
            if destination[key] == 0:
                del destination[key]
        state[target] = destination
    return state


def census_2x2():
    """Count *all* 12-query minima for two distinct sources and two outputs.

    The lower bound forces each B_j to appear once with each sign into each
    output, and each A_i once with each sign from the other output.  Thus all
    12 queries are distinct and there are 12! candidate words.

    Remove the four queries of either B_j from a two-source word.  Because
    sources are immutable and A queries act linearly, the resulting projection
    must be an eight-query single-source solution; the converse also holds if
    both projections are solutions.  The four A queries must retain the same
    order in both projections.  Once a pair of projections is fixed, the
    number of words that project to it is the product of the five within-gap
    binomial shuffle counts.  This gives an exact census without explicitly
    walking 12! words, with neither random sampling nor commuting variables.
    """
    a_queries = ((1, "a0", 2, 1), (-1, "a0", 2, 1),
                 (1, "a1", 1, 2), (-1, "a1", 1, 2))
    b_queries = ((1, "b", 0, 1), (-1, "b", 0, 1),
                 (1, "b", 0, 2), (-1, "b", 0, 2))
    goal = [{(0, ()): 1},
            {(1, ()): 1, (0, ("a0", "b")): 1},
            {(2, ()): 1, (0, ("a1", "b")): 1}]
    groups = defaultdict(Counter)
    all_groups = defaultdict(Counter)
    examined = 0
    for operations in permutations(a_queries + b_queries):
        examined += 1
        a_order, gaps = [], [0]
        for operation in operations:
            if operation[1] == "b":
                gaps[-1] += 1
            else:
                a_order.append(a_queries.index(operation))
                gaps.append(0)
        all_groups[tuple(a_order)][tuple(gaps)] += 1
        if _free_evaluate(operations, 3) == goal:
            groups[tuple(a_order)][tuple(gaps)] += 1
    covered = 0
    for patterns in all_groups.values():
        for first, first_count in patterns.items():
            for second, second_count in patterns.items():
                shuffles = 1
                for left, right in zip(first, second):
                    shuffles *= comb(left + right, left)
                covered += first_count * second_count * shuffles
    _require(covered == factorial(12), "projection shuffles do not cover 12! words")
    total = 0
    contributions = {}
    for a_order, patterns in sorted(groups.items()):
        contribution = 0
        for first, first_count in patterns.items():
            for second, second_count in patterns.items():
                shuffles = 1
                for left, right in zip(first, second):
                    shuffles *= comb(left + right, left)
                contribution += first_count * second_count * shuffles
        contributions[",".join(map(str, a_order))] = contribution
        total += contribution
    singles = sum(sum(group.values()) for group in groups.values())
    _require(examined == factorial(8), "single-source census is incomplete")
    _require(singles == 224, "single-source minimum-word count changed")
    _require(total == 76032, "two-source minimum-word count changed")
    return {
        "one_source_candidates_checked": examined,
        "one_source_minimum_words": singles,
        "two_source_minimum_length": 12,
        "two_source_candidate_words": factorial(12),
        "candidate_words_recovered_by_projection_shuffles": covered,
        "two_source_minimum_words": total,
        "admissible_a_orders": len(groups),
        "gap_patterns": sum(len(group) for group in groups.values()),
        "two_source_words_by_a_order": contributions,
    }


def self_check():
    """Small hand-computable checks of the independent oracle itself."""
    matrices = {
        "B0": [[0, 1], [0, 0]],
        "B1": [[0, 0], [1, 0]],
        "A0": [[1, 2], [0, -1]],
        "A1": [[0, 1], [1, 0]],
    }
    rows = [[2, 3], [-1, 4], [5, -2], [7, 1], [13, -11]]
    _require(expected(rows, 2, 2, matrices) == [
        [2, 3], [-1, 4], [6, -1], [6, 4], [13, -11]], "direct-map hand check")
    _require(product_matrix(["B0", "B1"], matrices) == [[0, 0], [0, 1]], "product-order hand check")
    _require(product_matrix(["B1", "B0"], matrices) == [[1, 0], [0, 0]], "noncommuting hand check")
    operations = [(1, "B0", 0, 2), (-1, "A1", 2, 3)]
    result, peak = evaluate(operations, rows, matrices)
    _require(result == [[2, 3], [-1, 4], [8, -2], [9, -7], [13, -11]], "dense shear hand check")
    _require(peak == 13, "arithmetic peak hand check")
    restored, _ = evaluate([(-sign, factor, source, target)
                           for sign, factor, source, target in reversed(operations)],
                          result, matrices)
    _require(restored == rows, "literal inverse hand check")
    return {"dense_oracle_hand_checks": "passed", "noncommuting_singular_factors": True}


def check(cases, factors, m=3, k=4):
    """Check supplied expanded words against independently composed matrices.

    This consumes only values supplied by the caller; it does not import or
    call the emitter, recurrence, inverse helper, or symbolic checker.
    """
    names = sorted(name for group in factors.values() for name in group)
    common_leaves = max(len(case["word"]) for case in cases.values())
    checks = 0
    widths = []
    for dimension in (1, 2, 3):
        for seed in (54, 154, 254):
            rng = random.Random(seed + 1000 * dimension)
            matrices = {name: [[rng.randrange(-2, 3) for _ in range(dimension)]
                               for _ in range(dimension)] for name in names}
            if seed == 154:
                matrices[names[0]] = [[0] * dimension for _ in range(dimension)]
            if seed == 254:
                matrices[names[0]][0] = [0] * dimension
            complete = {name: product_matrix(group, matrices) for name, group in factors.items()}
            for kind, case in sorted(cases.items()):
                rows = [[rng.randrange(-3, 4) for _ in range(dimension)]
                        for _ in range(case["rows"])]
                actual, peak = evaluate(case["word"], rows, matrices)
                if actual != expected(rows, m, k, complete):
                    raise ValueError(f"independent dense identity failed: {dimension}, {seed}, {kind}")
                inverse = [(-sign, factor, source, target)
                           for sign, factor, source, target in reversed(case["word"])]
                restored, inverse_peak = evaluate(inverse, actual, matrices)
                if restored != rows:
                    raise ValueError(f"independent inverse failed: {dimension}, {seed}, {kind}")
                d = max(1, *(abs(value) for row in rows for value in row))
                h = max(abs(value) for matrix in matrices.values() for row in matrix for value in row)
                width = 2 + (d - 1).bit_length() + common_leaves * (dimension * h).bit_length()
                observed = max(peak, inverse_peak).bit_length() + 1
                if observed > width:
                    raise ValueError("independent scalar arithmetic exceeded stated width")
                widths.append({"dimension": dimension, "seed": seed, "schedule": kind,
                               "observed_signed_bits": observed, "sufficient_signed_bits": width})
                checks += 1
    invoices = {}
    for kind, case in sorted(cases.items()):
        travel = closed_head_travel(case["word"], case["rows"], names, 3)
        if travel != case["invoice_L3"]["head_travel_word_slots"]:
            raise ValueError(f"independent closed tape invoice failed: {kind}")
        invoices[kind] = travel
    return {
        **self_check(),
        "expanded_dense_forward_inverse_cases": checks,
        "dimensions": [1, 2, 3],
        "seeds": [54, 154, 254],
        "deliberate_zero_and_singular_factors": True,
        "scalar_prefix_width_checks": widths,
        "closed_head_travel_L3": invoices,
    }


minimum_census = census_2x2


if __name__ == "__main__":
    print(json.dumps({**self_check(), "minimum_census": census_2x2()}, indent=2, sort_keys=True))

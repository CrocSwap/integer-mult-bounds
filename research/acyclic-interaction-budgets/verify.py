#!/usr/bin/env python3
"""Exact finite corroboration; the universal quantifiers are in PROOF.md."""

import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
from fractions import Fraction as Q


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("acyclic_budgets", PACKAGE / "budgets.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load the adjacent budget implementation")
BUDGETS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUDGETS)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def identity(size):
    return [[Q(row == column) for column in range(size)] for row in range(size)]


def zero(size):
    return [[Q(0) for _ in range(size)] for _ in range(size)]


def plus(left, right, sign=1):
    return [[a + sign * b for a, b in zip(row, other)]
            for row, other in zip(left, right)]


def scale(matrix, value):
    return [[value * entry for entry in row] for row in matrix]


def multiply(left, right):
    size = len(left)
    return [[sum(left[row][inner] * right[inner][column] for inner in range(size))
             for column in range(size)] for row in range(size)]


def act(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def norm(matrix):
    return max(sum(abs(entry) for entry in row) for row in matrix)


def vector_norm(vector):
    return max(abs(entry) for entry in vector)


def inverse(matrix):
    """Independent exact elimination, without a nilpotent inverse formula."""
    size = len(matrix)
    rows = [row.copy() + unit for row, unit in zip(matrix, identity(size))]
    for column in range(size):
        pivots = [row for row in range(column, size) if rows[row][column]]
        require(bool(pivots), "unexpected singular matrix")
        pivot = pivots[0]
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [entry / divisor for entry in rows[column]]
        for row in range(size):
            if row != column:
                factor = rows[row][column]
                rows[row] = [a - factor * b for a, b in zip(rows[row], rows[column])]
    result = [row[size:] for row in rows]
    require(multiply(result, matrix) == identity(size), "left inverse failed")
    require(multiply(matrix, result) == identity(size), "right inverse failed")
    return result


def literal_product(errors):
    size = len(errors[0])
    result = identity(size)
    for error in errors:
        result = multiply(plus(identity(size), error), result)
    return result


def graph_oracle(errors):
    """Adjacency powers give a separate longest-walk oracle for tiny graphs."""
    size = len(errors[0])
    adjacency = [[Q(any(error[row][column] for error in errors))
                  for column in range(size)] for row in range(size)]
    power = identity(size)
    depth = 0
    for degree in range(1, size + 1):
        power = multiply(adjacency, power)
        if norm(power) == 0:
            return depth
        depth = degree
    raise ValueError("cycle in the union support")


def polynomial_checks(counts):
    for length in range(7):
        for depth in range(6):
            values = tuple(Q((2 * index + length) % 5, 3) for index in range(length))
            elementary, homogeneous = BUDGETS.coefficients(values, depth)
            for degree in range(depth + 1):
                expected_e = sum(math.prod(values[i] for i in subset)
                                 for subset in itertools.combinations(range(length), degree))
                expected_h = sum(math.prod(values[i] for i in subset)
                                 for subset in itertools.combinations_with_replacement(
                                     range(length), degree))
                require(elementary[degree] == expected_e, "elementary polynomial mismatch")
                require(homogeneous[degree] == expected_h, "homogeneous polynomial mismatch")
                counts["polynomial_coefficients"] += 2
    elementary, homogeneous = BUDGETS.coefficients([Q(1, 8)] * 32, 15)
    for degree in range(16):
        require(elementary[degree] == math.comb(32, degree) * Q(1, 8) ** degree,
                "capacity elementary coefficient")
        require(homogeneous[degree] == math.comb(31 + degree, degree) * Q(1, 8) ** degree,
                "capacity homogeneous coefficient")
        counts["polynomial_coefficients"] += 2
    BUDGETS.coefficients([Q(1 << 255)] * 32, 15)
    counts["capacity_checks"] += 2


def sequence_checks(errors, depth, counts):
    size = len(errors[0])
    require(BUDGETS.support_depth(errors, size) == graph_oracle(errors),
            "support-depth oracle mismatch")
    require(BUDGETS.support_depth(errors, size) <= depth, "invalid fixture depth")
    counts["support_graphs"] += 1
    norms = []
    noise_norms = []
    result = identity(size)
    initial = [Q((-1) ** index * (index + 1), 3) for index in range(size)]
    trajectory = initial.copy()
    for index, error in enumerate(errors):
        norms.append(norm(error))
        gate = plus(identity(size), error)
        result = multiply(gate, result)
        actual_inverse = inverse(result)
        forward, backward = BUDGETS.envelopes(norms, depth)
        require(norm(result) <= forward, "forward envelope failed")
        require(norm(plus(result, identity(size), -1)) <= forward - 1,
                "forward defect failed")
        require(norm(actual_inverse) <= backward, "inverse envelope failed")
        require(norm(plus(actual_inverse, identity(size), -1)) <= backward - 1,
                "inverse defect failed")
        noise = [Q((-1) ** (index + row), index + 2) for row in range(size)]
        noise_norms.append(vector_norm(noise))
        trajectory = [a + b for a, b in zip(act(gate, trajectory), noise)]
        bound = BUDGETS.trajectory_budget(norms, depth, vector_norm(initial), noise_norms)
        defect = [a - b for a, b in zip(trajectory, initial)]
        require(vector_norm(defect) <= bound, "arithmetic-noise envelope failed")
        counts["prefixes"] += 1
        counts["noise_steps"] += 1


def exhaustive_pairs(counts):
    matrices = []
    for entries in itertools.product((Q(-1, 2), Q(0), Q(1, 2)), repeat=3):
        matrix = zero(3)
        matrix[0][1], matrix[0][2], matrix[1][2] = entries
        matrices.append(matrix)
    for left in matrices:
        for right in matrices:
            sequence_checks([left, right], 2, counts)
            counts["exhaustive_pairs"] += 1


def permuted_words(counts):
    for size in range(2, 7):
        permutation = tuple(reversed(range(size)))
        for length in (1, 3, 7):
            errors = []
            for index in range(length):
                matrix = zero(size)
                for row in range(size):
                    for column in range(row + 1, size):
                        value = Q((index + row + 2 * column) % 5 - 2, 4)
                        matrix[permutation[row]][permutation[column]] = value
                errors.append(matrix)
            sequence_checks(errors, size - 1, counts)
            counts["permuted_words"] += 1


def shift(depth):
    result = zero(depth + 1)
    for index in range(depth):
        result[index][index + 1] = Q(1)
    return result


def witness_checks(depth, values, counts):
    matrix = shift(depth)
    size = depth + 1
    positive = [scale(matrix, value) for value in values]
    negative = [scale(matrix, -value) for value in values]
    forward, backward = BUDGETS.envelopes(values, depth)
    result = literal_product(positive) if positive else identity(size)
    inverse_result = inverse(literal_product(negative)) if negative else identity(size)
    require(norm(result) == forward, "forward sharpness failed")
    require(norm(plus(result, identity(size), -1)) == forward - 1,
            "forward defect sharpness failed")
    require(norm(inverse_result) == backward, "inverse sharpness failed")
    require(norm(plus(inverse_result, identity(size), -1)) == backward - 1,
            "inverse defect sharpness failed")
    initial = [Q(2, 3)] * size
    trajectory = initial.copy()
    noise = [Q(index + 1, 10) for index in range(len(values))]
    for error, value in zip(positive, noise):
        trajectory = [entry + value for entry in act(plus(identity(size), error), trajectory)]
    bound = BUDGETS.trajectory_budget(values, depth, Q(2, 3), noise)
    require(vector_norm([a - b for a, b in zip(trajectory, initial)]) == bound,
            "trajectory sharpness failed")
    counts["attaining_families"] += 1


def all_witnesses(counts):
    for depth in range(6):
        for length in (*range(7), 20):
            values = tuple(Q(index % 4, 5) for index in range(length))
            witness_checks(depth, values, counts)
    witness_checks(15, (Q(1, 8),) * 32, counts)
    for depth, expected in ((1, (Q(3), Q(3))), (2, (Q(49, 10), Q(51, 10)))):
        values = (Q(1, 10),) * 20
        witness_checks(depth, values, counts)
        require(BUDGETS.envelopes(values, depth) == expected, "twenty-step exact values")
        sequence_checks([scale(shift(depth), value) for value in values], depth, counts)
    require(Q(3) < Q(11, 10) ** 20, "strict depth-one product improvement")


def expect_invalid(kind, arguments):
    try:
        if kind == "coefficients":
            BUDGETS.coefficients(*arguments)
        elif kind == "support":
            BUDGETS.support_depth(*arguments)
        elif kind == "trajectory":
            BUDGETS.trajectory_budget(*arguments)
        else:
            raise AssertionError("unknown rejection fixture")
    except ValueError:
        return
    raise AssertionError("invalid input accepted")


def rejection_checks(counts):
    fixtures = [
        ("coefficients", ([1], -1)),
        ("coefficients", ([1], 16)),
        ("coefficients", ([1], True)),
        ("coefficients", ([1] * 33, 2)),
        ("coefficients", ([Q(-1)], 2)),
        ("coefficients", ([0.5], 2)),
        ("coefficients", ([True], 2)),
        ("coefficients", ([1 << 256], 2)),
        ("coefficients", ([Q(1, 1 << 256)], 2)),
        ("coefficients", ((value for value in (1, 2)), 2)),
        ("support", ([], 0)),
        ("support", ([], 17)),
        ("support", ([[[1]]], 1)),
        ("support", ([[[0, 1], [1, 0]]], 2)),
        ("support", ([[[0]]], 2)),
        ("support", ([[[0], [0]]], 2)),
        ("support", ([[[0.0]]], 1)),
        ("trajectory", ([1], 1, 0, [])),
        ("trajectory", ([1], 1, -1, [0])),
        ("trajectory", ([1], 1, 0, [-1])),
    ]
    for kind, arguments in fixtures:
        expect_invalid(kind, arguments)
        counts["input_rejections"] += 1
    require(BUDGETS.support_depth([], 16) == 0, "empty support has depth zero")


def mathematical_controls(counts):
    upper = [[Q(0), Q(1)], [Q(0), Q(0)]]
    lower = [[Q(0), Q(0)], [Q(1), Q(0)]]
    require(multiply(upper, upper) == zero(2) and multiply(lower, lower) == zero(2),
            "individual nilpotence control")
    require(norm(literal_product([upper, lower, upper])) == 5
            > BUDGETS.envelopes([1, 1, 1], 1)[0],
            "common-support necessity control")
    expect_invalid("support", ([upper, lower], 2))
    matrix = shift(2)
    require(norm(literal_product([matrix, matrix])) == 4 > 3,
            "omitted degree-two term control")
    require(norm(inverse(plus(identity(3), scale(matrix, -1)))) == 3
            > BUDGETS.envelopes([1], 2)[0], "inverse is homogeneous, not elementary")
    a, b = zero(3), zero(3)
    a[0][1], b[1][2] = Q(1), Q(1)
    actual = inverse(literal_product([a, b]))
    right = multiply(plus(identity(3), a, -1), plus(identity(3), b, -1))
    wrong = multiply(plus(identity(3), b, -1), plus(identity(3), a, -1))
    require(actual == right and actual != wrong, "inverse chronological order control")
    require(BUDGETS.trajectory_budget([0, 1], 1, 0, [1, 0]) == 2 > 1,
            "noise suffix cannot be omitted")
    frame = plus(identity(2), lower)
    interaction = multiply(multiply(inverse(frame), upper), frame)
    require(interaction[0][0] != 0 and interaction[1][1] != 0,
            "physical and interaction supports differ")
    expect_invalid("support", ([interaction], 2))
    require(multiply(matrix, matrix) != zero(3), "higher-nilpotency class is present")
    counts["mathematical_controls"] += 7


def file_hashes():
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "budgets.py", "verify.py")
    result = {}
    for name in names:
        path = PACKAGE / name
        require(path.is_file() and not path.is_symlink(), "missing or aliased package file")
        require(path.stat().st_size <= 131072, "package file exceeds replay capacity")
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    counts = dict.fromkeys(("polynomial_coefficients", "capacity_checks", "support_graphs",
                            "prefixes", "noise_steps", "exhaustive_pairs", "permuted_words",
                            "attaining_families", "input_rejections", "mathematical_controls"), 0)
    polynomial_checks(counts)
    exhaustive_pairs(counts)
    permuted_words(counts)
    all_witnesses(counts)
    rejection_checks(counts)
    mathematical_controls(counts)
    print(json.dumps({"status": "PASS_ACYCLIC_INTERACTION_BUDGETS", "errors": 0,
                      "claim_type": "scoped written proof with exact finite corroboration",
                      "python": sys.version.split()[0], "counts": counts,
                      "twenty_norms_one_tenth": {
                          "depth_one": [str(x) for x in BUDGETS.envelopes([Q(1, 10)] * 20, 1)],
                          "depth_two": [str(x) for x in BUDGETS.envelopes([Q(1, 10)] * 20, 2)]},
                      "package_sha256": file_hashes()}, sort_keys=True))


if __name__ == "__main__":
    main()

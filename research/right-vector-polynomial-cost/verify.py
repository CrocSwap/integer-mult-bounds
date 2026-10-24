#!/usr/bin/env python3
"""Exact F2[t] matrices corroborating the scoped reduced-word cost proof."""
import hashlib
import itertools
import json
from pathlib import Path

IDENTITY = (1, 0, 0, 1)
DIRECTIONS = (1, 2, 3)
MAX_DEGREE = 4
PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def multiply_polynomial(a, b):
    require(0 <= a < 2**32 and 0 <= b < 2**32, "polynomial capacity")
    result = 0
    for bit in range(b.bit_length()):
        if (b >> bit) & 1:
            result ^= a << bit
    return result


def multiply(a, b):
    return tuple(
        multiply_polynomial(a[2*i], b[j])
        ^ multiply_polynomial(a[2*i+1], b[2+j])
        for i in range(2) for j in range(2)
    )


def transvection(direction, coefficient):
    require(direction in DIRECTIONS, "invalid direction")
    a, b = direction & 1, direction >> 1
    return (
        1 ^ (coefficient if a*b else 0), coefficient if b else 0,
        coefficient if a else 0, 1 ^ (coefficient if a*b else 0)
    )


def degree(matrix):
    return max(value.bit_length() - 1 for value in matrix)


def determinant(matrix):
    a, b, c, d = matrix
    return multiply_polynomial(a, d) ^ multiply_polynomial(b, c)


def evaluate_word(word):
    result = IDENTITY
    for direction, coefficient in word:
        result = multiply(result, transvection(direction, coefficient))
    return result


def free_matrices():
    return tuple(a for a in itertools.product(range(2), repeat=4)
                 if determinant(a) == 1)


def delta(matrix, free):
    values = []
    for endpoint in free:
        product = multiply(matrix, endpoint)
        columns = ((product[0] ^ 1, product[2]),
                   (product[1], product[3] ^ 1))
        nonzero = set(columns) - {(0, 0)}
        values.append(min(2, len(nonzero)))
    return min(values)


def reduced_words():
    # At most four factors, three directions and 15 allowed coefficients.
    states = [((), IDENTITY, 0)]
    frontier = states
    for _length in range(MAX_DEGREE):
        next_frontier = []
        for word, matrix, total in frontier:
            for direction in DIRECTIONS:
                if word and word[-1][0] == direction:
                    continue
                for coefficient in range(2, 2**(MAX_DEGREE+1), 2):
                    new_total = total + coefficient.bit_length() - 1
                    if new_total <= MAX_DEGREE:
                        next_word = word + ((direction, coefficient),)
                        product = multiply(matrix, transvection(direction, coefficient))
                        require(degree(product) == new_total, "degree sum failed")
                        require(determinant(product) == 1, "word not invertible")
                        next_frontier.append((next_word, product, new_total))
        states.extend(next_frontier)
        frontier = next_frontier
    require(len(states) == 256, "normalized-word census")
    return states


def census(states, free):
    seen = {}
    histogram = [0] * 5
    for word, matrix, total in states:
        require(evaluate_word(word) == matrix, "chronological product mismatch")
        for endpoint in free:
            target = multiply(matrix, endpoint)
            require(target not in seen, "normal form collision")
            require(degree(target) == total, "free endpoint changed degree")
            cost = len(word)
            require(delta(target, free) == min(2, cost), "column comparison")
            seen[target] = word, endpoint
            histogram[cost] += 1
    require(histogram == [6, 270, 612, 504, 144], "cost histogram")
    return seen, histogram


def literal_paid_control(free):
    count = 0
    # Enumerate all three nonzero y and all 32^2 possible polynomial left vectors.
    for direction in DIRECTIONS:
        a, b = direction & 1, direction >> 1
        for u0, u1 in itertools.product(range(32), repeat=2):
            matrix = (1 ^ (u0 if a else 0), u0 if b else 0,
                      u1 if a else 0, 1 ^ (u1 if b else 0))
            if determinant(matrix) != 1:
                continue
            coefficient = u0 if b else u1
            require(matrix == transvection(direction, coefficient), "paid reduction")
            constant = transvection(direction, coefficient & 1)
            require(constant in free, "constant factor not free")
            split = transvection(direction, coefficient ^ (coefficient & 1))
            require(multiply(split, constant) == matrix, "constant split")
            for endpoint in free:
                # Binary inverse is found in the complete six-element free group.
                inverses = [s for s in free if multiply(endpoint, s) == IDENTITY]
                require(len(inverses) == 1, "free inverse")
                conjugate = multiply(multiply(endpoint, split), inverses[0])
                require(conjugate in [transvection(y, coefficient & ~1)
                                      for y in DIRECTIONS], "conjugation closure")
            count += 1
    require(count == 96, "literal invertible paid parameter count")
    return count


def target_and_controls(seen):
    word = ((2, 2), (1, 2), (2, 2), (1, 2))
    target = evaluate_word(word)
    require(target == (21, 8, 8, 5), "four-factor target polynomial")
    require(len(seen[target][0]) == 4, "target cost")
    exclusions = sum(1 for candidate, endpoint in seen.values()
                     if len(candidate) <= 3 and degree(evaluate_word(candidate)) == 4)
    require(exclusions == 1008, "degree-four shorter-word exclusions")
    require(multiply(transvection(1, 2), transvection(1, 2)) == IDENTITY,
            "equal-direction cancellation control")
    constant = multiply(transvection(2, 1), transvection(1, 1))
    require(multiply(multiply(constant, constant), constant) == IDENTITY,
            "constant-coefficient relation control")
    require(tuple(p & 1 for p in target) == IDENTITY, "specialization control")
    require(evaluate_word(word[:-1]) != target, "dropped factor control")
    require(evaluate_word(tuple(reversed(word))) != target, "word-order control")
    require(determinant((0, 0, 0, 1)) == 0, "singular-factor control")
    require((target[0] ^ 1, *target[1:]) not in seen, "changed entry control")
    return target, exclusions


def receipt(root, histogram, target, exclusions, paid_count):
    sources = json.loads((root / "SOURCES.json").read_text())
    repository = root.parent.parent
    for row in sources["files"]:
        if row["usage"] == "input":
            payload = (repository / row["path"]).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == row["sha256"], "source hash")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
              for name in PACKAGE_FILES}
    result = {"schema": "right-vector-polynomial-cost/v1", "files_sha256": hashes,
              "targets": sum(histogram), "cost_histogram": histogram,
              "target_polynomial_bits": target, "target_cost": 4,
              "shorter_degree_four_exclusions": exclusions,
              "literal_paid_parameters": paid_count, "negative_controls": 7}
    print(json.dumps(result, sort_keys=True))
    print("PASS_RIGHT_VECTOR_POLYNOMIAL_COST targets=1536 cost4=144 target_cost=4 "
          "shorter_exclusions=1008 controls=7 no_new_kappa")


def main():
    free = free_matrices()
    require(len(free) == 6, "free group cardinality")
    states = reduced_words()
    seen, histogram = census(states, free)
    paid_count = literal_paid_control(free)
    target, exclusions = target_and_controls(seen)
    receipt(Path(__file__).resolve().parent, histogram, target, exclusions, paid_count)


if __name__ == "__main__":
    main()

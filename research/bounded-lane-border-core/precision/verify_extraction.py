#!/usr/bin/env python3
"""Exact standard-library checks for the root-only Walsh recovery identity."""

from fractions import Fraction
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sign(t, grade):
    return -1 if (t & grade).bit_count() % 2 else 1


def character_count(height):
    return 1 << height.bit_length()


def extract(matrix, grades, count):
    return tuple(tuple(sum(sign(t, h) * matrix[i][j] * sign(t, k)
                           for t in range(count)) / count
                       for j, k in enumerate(grades))
                 for i, h in enumerate(grades))


def apply(matrix, vector):
    return tuple(sum(a * x for a, x in zip(row, vector)) for row in matrix)


def run_wrapper(matrix, grades, vector, count):
    accumulator = [Fraction(0) for _ in vector]
    for t in range(count):
        work_input = tuple(sign(t, h) * x for h, x in zip(grades, vector))
        work_output = apply(matrix, work_input)
        for i, (h, value) in enumerate(zip(grades, work_output)):
            accumulator[i] += sign(t, h) * value
    return tuple(value / count for value in accumulator)


def check():
    cases = []
    for height in range(9):
        count = character_count(height)
        grades = tuple(h for h in range(height + 1)
                       for _ in range(1 + h % 3))
        for h in range(height + 1):
            for k in range(height + 1):
                inner = sum(sign(t, h) * sign(t, k) for t in range(count))
                require(inner == (count if h == k else 0),
                        f"character orthogonality failed at {height,h,k}")
        matrix = tuple(tuple(Fraction((7 * i + 3 * j + 1) % 17 - 8,
                                      2 ** ((i + j) % 4))
                             for j in range(len(grades)))
                       for i in range(len(grades)))
        expected = tuple(tuple(matrix[i][j] if h == k else Fraction(0)
                               for j, k in enumerate(grades))
                         for i, h in enumerate(grades))
        actual = extract(matrix, grades, count)
        require(actual == expected,
                f"unequal-block extraction failed at height {height}")
        cases.append({"height": height, "characters": count,
                      "real_dimension": len(grades)})

    # A realification of the exact order-four complex Gaussian. Same-grade
    # blocks are this operator; inter-grade blocks are arbitrary dyadic maps.
    half = Fraction(1, 2)
    gaussian = tuple(tuple(half * x for x in row) for row in
                     ((1, 1, -1, 1), (1, 1, 1, -1),
                      (1, -1, 1, 1), (-1, 1, 1, 1)))
    grades = tuple(h for h in range(4) for _ in range(4))
    matrix = tuple(tuple(gaussian[i % 4][j % 4] if grades[i] == grades[j]
                         else Fraction(((i + 2 * j) % 11) - 5, 4)
                         for j in range(16)) for i in range(16))
    vector = tuple(Fraction(i - 7, 8) for i in range(16))
    expected = tuple(value for start in range(0, 16, 4)
                     for value in apply(gaussian, vector[start:start + 4]))
    require(run_wrapper(matrix, grades, vector, 4) == expected,
            "Gaussian vector recovery failed")

    # Two binary characters cannot distinguish grade zero from grade two.
    # The invalid K=2 average leaves this inter-grade block untouched.
    collision_matrix = ((Fraction(0), Fraction(0), Fraction(1)),
                        (Fraction(0), Fraction(0), Fraction(0)),
                        (Fraction(0), Fraction(0), Fraction(0)))
    collision_grades = (0, 1, 2)
    require(extract(collision_matrix, collision_grades, 2)[0][2] == 1,
            "insufficient-character control did not exhibit its collision")
    require(extract(collision_matrix, collision_grades, 4)[0][2] == 0,
            "valid characters failed to remove the control block")
    return {"status": "pass", "unequal_grade_dimension_cases": cases,
            "gaussian_recovery_dimension": 16,
            "insufficient_character_control": "detected"}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))

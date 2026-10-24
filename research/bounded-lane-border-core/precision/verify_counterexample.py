#!/usr/bin/env python3
"""Exact standard-library checks for the endpoint-height counterexample.

This verifies finite matrix identities.  The asymptotic recurrence is proved in
REVIEW.md; no integer-multiplication bound is claimed.
"""

from fractions import Fraction
import json


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def identity(size):
    return tuple(tuple(int(i == j) for j in range(size))
                 for i in range(size))


def matmul(a, b):
    return tuple(tuple(sum(x * y for x, y in zip(row, col))
                       for col in zip(*b)) for row in a)


def product(*matrices):
    value = matrices[0]
    for matrix in matrices[1:]:
        value = matmul(value, matrix)
    return value


def transpose(matrix):
    return tuple(zip(*matrix))


def power(matrix, exponent):
    result = identity(len(matrix))
    for _ in range(exponent):
        result = matmul(result, matrix)
    return result


def shear(a):
    return ((1, a, 0), (0, 1, 0), (0, 0, 1))


def tensor(a, b):
    return tuple(tuple(a[i][j] * b[k][ell]
                       for j in range(len(a[0]))
                       for ell in range(len(b[0])))
                 for i in range(len(a)) for k in range(len(b)))


P = ((0, 0, 1), (1, 0, 0), (0, 1, 0))
Q = ((1, 0, 0), (0, 0, 1), (0, 1, 0))
PINV = transpose(P)


def square_word(a, a_inverse):
    # Q [A, P A P^-1] Q^-1, with [A,B] = A B A^-1 B^-1.
    b = product(P, a, PINV)
    b_inverse = product(P, a_inverse, PINV)
    return product(Q, a, b, a_inverse, b_inverse, Q)


def inverse_square_word(a, a_inverse):
    b = product(P, a, PINV)
    b_inverse = product(P, a_inverse, PINV)
    return product(Q, b, a, b_inverse, a_inverse, Q)


def check():
    examples = [Fraction(0), Fraction(1), Fraction(2), Fraction(-3),
                Fraction(1, 2), Fraction(-5, 4)]
    for a in examples:
        squared = square_word(shear(a), shear(-a))
        squared_inverse = inverse_square_word(shear(a), shear(-a))
        require(squared == shear(a ** 2), f"square word failed at {a}")
        require(squared_inverse == shear(-(a ** 2)),
                f"inverse square word failed at {a}")
        require(square_word(squared, squared_inverse) == shear(a ** 4),
                f"quartic word failed at {a}")

        # The shear component of T(a)^4 is U(4a). Conjugation by R_+
        # extracts U(a); R_- extracts U(-a), allowing pure G extraction.
        r_plus = ((Fraction(1, 4), 0, 0), (0, 1, 0), (0, 0, 1))
        r_plus_inverse = ((4, 0, 0), (0, 1, 0), (0, 0, 1))
        r_minus = ((Fraction(-1, 4), 0, 0), (0, 1, 0), (0, 0, 1))
        r_minus_inverse = ((-4, 0, 0), (0, 1, 0), (0, 0, 1))
        require(product(r_plus, power(shear(a), 4), r_plus_inverse) == shear(a),
                f"positive extraction failed at {a}")
        require(product(r_minus, power(shear(a), 4), r_minus_inverse) == shear(-a),
                f"negative extraction failed at {a}")

    # Exact realification of G=(1/2)[[1+i,1-i],[1-i,1+i]], in the order
    # (Re z0, Re z1, Im z0, Im z1). This also checks the Gaussian factor
    # omitted from the three-role shear calculation above.
    half = Fraction(1, 2)
    gaussian = tuple(tuple(half * entry for entry in row) for row in
                     ((1, 1, -1, 1), (1, 1, 1, -1),
                      (1, -1, 1, 1), (-1, 1, 1, 1)))
    require(power(gaussian, 4) == identity(4), "Gaussian order-four failed")
    t = tensor(shear(Fraction(2)), gaussian)
    extracted = product(tensor(r_plus, identity(4)), power(t, 4),
                        tensor(r_plus_inverse, identity(4)))
    require(extracted == tensor(shear(Fraction(2)), identity(4)),
            "full Gaussian shear extraction failed")
    pure_gaussian = product(tensor(r_minus, identity(4)), power(t, 4),
                            tensor(r_minus_inverse, identity(4)), t)
    require(pure_gaussian == tensor(identity(3), gaussian),
            "full Gaussian cancellation failed")

    growth = []
    a = 2
    for depth in range(7):
        e = 2 ** depth
        require(a == 2 ** (e ** 2), f"coefficient growth failed at rank {e}")
        require(a.bit_length() == e ** 2 + 1,
                f"numerator bit count failed at rank {e}")
        growth.append({"depth": depth, "rank": e,
                       "off_diagonal_numerator_bits": a.bit_length()})
        a = a ** 4

    return {"status": "pass", "rational_examples": len(examples),
            "full_gaussian_extraction_dimension": 12,
            "quartic_word_child_calls": 16,
            "full_gaussian_diagonal_template_child_calls": 74,
            "growth": growth}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))

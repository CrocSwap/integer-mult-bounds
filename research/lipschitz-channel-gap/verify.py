#!/usr/bin/env python3
"""Check the Lipschitz-order gap with exact four-lane arithmetic."""

from fractions import Fraction
from itertools import product


ZERO = (0, 0, 0, 0)
HALF_SUM = (Fraction(1, 2),) * 4
RESPONSE = (
    ((1, 1, 0, 0), (0, 1, 0, 1)),
    ((1, 0, 1, 0), (0, 1, 1, 0)),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(*vectors):
    return tuple(sum(lane) for lane in zip(*vectors, strict=True))


def multiply(left, right):
    a, b, c, d = left
    matrix = (
        (a, -b, -c, -d),
        (b, a, -d, c),
        (c, d, a, -b),
        (d, -c, b, a),
    )
    return tuple(
        sum(coefficient * lane for coefficient, lane in zip(row, right, strict=True))
        for row in matrix
    )


def left_i(x):
    a, b, c, d = x
    return -b, a, -d, c


def left_j(x):
    a, b, c, d = x
    return -c, d, a, -b


def one_channel(x, y, k_sign):
    iy = left_i(y)
    jy = left_j(y)
    ky = left_i(jy)
    total = add(y, iy, jy, tuple(k_sign * lane for lane in ky))
    z = add(x, tuple(Fraction(lane, 2) for lane in total))
    return add(z, left_i(z)), add(z, left_j(z))


def two_channels(x, y):
    iy = left_i(y)
    jy = left_j(y)
    return add(x, left_i(x), iy, left_i(jy)), add(x, left_j(x), iy, jy)


def check_responses():
    basis = tuple(tuple(int(i == j) for j in range(4)) for i in range(4))
    inputs = tuple((x, ZERO) for x in basis) + tuple((ZERO, y) for y in basis)
    reversed_failures = 0
    for x, y in inputs:
        expected = tuple(
            add(multiply(a, x), multiply(b, y)) for a, b in RESPONSE
        )
        require(one_channel(x, y, 1) == expected, "wrong dyadic response")
        require(two_channels(x, y) == expected, "wrong integral response")
        reversed_failures += one_channel(x, y, -1) != expected
    require(reversed_failures == 4, "reversed ij control did not discriminate")
    return len(inputs), reversed_failures


def check_parity():
    residues = tuple(product(range(2), repeat=4))
    for residue in residues:
        half_product = multiply(residue, HALF_SUM)
        integral = all(lane.denominator == 1 for lane in half_product)
        require(integral == (sum(residue) % 2 == 0), "wrong parity criterion")
    return len(residues)


def divides_on_right(value, divisor):
    a, b, c, d = divisor
    numerator = multiply(value, (a, -b, -c, -d))
    return all(lane % 2 == 0 for lane in numerator)


def check_right_divisors():
    candidates = tuple(
        divisor
        for divisor in product((-1, 0, 1), repeat=4)
        if sum(lane * lane for lane in divisor) == 2
    )
    first, second = (row[0] for row in RESPONSE)
    first_divisors = {d for d in candidates if divides_on_right(first, d)}
    second_divisors = {d for d in candidates if divides_on_right(second, d)}
    common = first_divisors & second_divisors
    require(len(candidates) == 24, "incomplete norm-two domain")
    require(len(first_divisors) == len(second_divisors) == 8, "wrong divisor counts")
    require(not common, "found an integral one-channel factor")
    return len(candidates), len(first_divisors), len(second_divisors), len(common)


def main():
    basis, wrong_order = check_responses()
    parity = check_parity()
    candidates, first, second, common = check_right_divisors()
    print(
        f"PASS_LIPSCHITZ_CHANNEL_GAP basis={basis} parity={parity} "
        f"norm_two={candidates} individual={first},{second} common={common} "
        f"reversed_order_failures={wrong_order}"
    )


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: Apache-2.0
"""Directed integer intervals and a sign proof for the finite packing exchange."""

from fractions import Fraction
from functools import lru_cache

SCALE = 10**60
GRID = 10**25


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceildiv(numerator, denominator):
    return -(-numerator // denominator)


def rational(value):
    value = Fraction(value)
    return (value * SCALE).__floor__(), (value * SCALE).__ceil__()


def multiply(left, right):
    need(min(*left, *right) >= 0, "nonnegative interval multiplication")
    return (
        left[0] * right[0] // SCALE,
        ceildiv(left[1] * right[1], SCALE),
    )


def unit_log(value):
    """Enclose log(value) on [1,2] by 64 positive atanh terms."""
    need(1 <= value <= 2, "unit logarithm range")
    z = rational((value - 1) / (value + 1))
    square = multiply(z, z)
    power, lower, upper = z, 0, 0
    for index in range(64):
        denominator = 2 * index + 1
        lower += power[0] // denominator
        upper += ceildiv(power[1], denominator)
        power = multiply(power, square)
    tail = ceildiv(2 * power[1] * SCALE, 129 * (SCALE - square[1]))
    return 2 * lower, 2 * upper + tail


@lru_cache(maxsize=73)
def logarithm(value):
    value = Fraction(value)
    need(1 <= value <= 73, "logarithm range")
    exponent = 0
    for _ in range(7):
        if value <= 2:
            break
        value /= 2
        exponent += 1
    lower, upper = unit_log(value)
    low_two, high_two = unit_log(Fraction(2))
    return lower + exponent * low_two, upper + exponent * high_two


def exponential(value):
    """24 Taylor terms and a geometric remainder, with directed rounding."""
    need(0 <= value[0] <= value[1] < SCALE, "exponential range")
    term = (SCALE, SCALE)
    lower = upper = SCALE
    for index in range(1, 25):
        product = multiply(term, value)
        term = product[0] // index, ceildiv(product[1], index)
        lower += term[0]
        upper += term[1]
    following = ceildiv(term[1] * value[1], 25 * SCALE)
    tail = ceildiv(following * 26 * SCALE, 26 * SCALE - value[1])
    return lower, upper + tail


def moment_numerator(profile, saving):
    need(0 <= saving <= Fraction(1, 100), "saving range")
    need(1 <= len(profile) <= 72, "profile size")
    lower = upper = 0
    for rank, count in profile.items():
        need(type(rank) is int and 0 < rank < 73, "child rank")
        need(type(count) is int and 0 < count <= 10**7, "child count")
        power = exponential(multiply(rational(saving), logarithm(Fraction(73, rank))))
        lower += count * rank * power[0]
        upper += count * rank * power[1]
    return lower, upper


def root(profile, replicas=74):
    need(replicas == 74, "this certificate has 74 replicas")
    need(sum(r * n for r, n in profile.items()) == 65088 * replicas, "rank mass")
    threshold = 73 * 896 * replicas * SCALE
    low, high = 0, GRID // 100
    need(moment_numerator(profile, Fraction(low, GRID))[1] < threshold, "lower root")
    need(moment_numerator(profile, Fraction(high, GRID))[0] > threshold, "upper root")
    for _ in range(GRID.bit_length()):
        if high - low == 1:
            return Fraction(low, GRID), Fraction(high, GRID)
        middle = (low + high) // 2
        lower, upper = moment_numerator(profile, Fraction(middle, GRID))
        if upper < threshold:
            low = middle
        elif lower > threshold:
            high = middle
        else:
            raise ValueError("interval precision exhausted")
    raise ValueError("bisection bound exhausted")


def short_log(value):
    z = (value - 1) / (value + 1)
    lower = 2 * sum(z ** (2 * j + 1) / (2 * j + 1) for j in range(3))
    return lower, lower + 2 * z**7 / (7 * (1 - z * z))


def sign_certificate():
    """Prove 4 H1 + 4 H3 - 6 H5 + H14 < 0 for 0 < b <= .01."""
    two = short_log(Fraction(2))
    bounds = {}
    for value, exponent, unit in [
        (3, 1, Fraction(3, 2)),
        (5, 2, Fraction(5, 4)),
        (14, 3, Fraction(7, 4)),
    ]:
        low, high = short_log(unit)
        bounds[value] = low + exponent * two[0], high + exponent * two[1]
    need(Fraction(109, 100) < bounds[3][0] < bounds[3][1] < Fraction(11, 10), "log3")
    need(bounds[5][1] < Fraction(161, 100), "log5")
    need(Fraction(263, 100) < bounds[14][0] < bounds[14][1] < Fraction(66, 25), "log14")
    derivative = (
        30 * Fraction(161, 100)
        - 12 * Fraction(109, 100) * Fraction(989, 1000)
        - 14 * Fraction(263, 100) * Fraction(1217, 1250)
    )
    need(derivative == -Fraction(60509, 125000), "negative derivative bound")
    return {"derivative_upper": str(derivative), "saving_interval": "0 < b <= 1/100"}

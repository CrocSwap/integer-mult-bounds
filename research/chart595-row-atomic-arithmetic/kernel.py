# SPDX-License-Identifier: Apache-2.0
"""Evaluate one integer row with a checked arithmetic-word width."""


def check(value, width):
    if type(value) is not int or not -(1 << (width - 1)) <= value < 1 << (width - 1):
        raise ValueError('signed arithmetic width')
    return value


def multiply(value, coefficient, width):
    """Use shifts and additions; preserve the input value."""
    magnitude = check(abs(value), width)
    factor = abs(coefficient)
    total = 0
    position = 0
    while factor:
        shifted = check(magnitude << position, width)
        if factor & 1:
            total = check(total + shifted, width)
        position += 1
        factor >>= 1
    return check(-total if (value < 0) != (coefficient < 0) else total, width)


def divide_exact(value, denominator, width):
    """Use binary long division and reject a nonzero final remainder."""
    magnitude = check(abs(value), width)
    quotient = remainder = 0
    for position in range(width - 2, -1, -1):
        remainder = check((remainder << 1) + ((magnitude >> position) & 1), width)
        quotient = check(quotient << 1, width)
        if remainder >= denominator:
            remainder = check(remainder - denominator, width)
            quotient = check(quotient + 1, width)
    if remainder:
        raise ValueError('nonzero exact-division remainder')
    return check(-quotient if value < 0 else quotient, width)


def row(values, coefficients, denominator, data_width):
    if type(data_width) is not int or data_width < 2:
        raise ValueError('data width must be at least two')
    if type(denominator) is not int or not 1 <= denominator <= 6720:
        raise ValueError('row denominator')
    if len(values) != len(coefficients) or not coefficients:
        raise ValueError('row arity')
    if any(type(c) is not int or c == 0 for c in coefficients):
        raise ValueError('integer row coefficients')
    if sum(map(abs, coefficients)) > 683350:
        raise ValueError('row coefficient mass')
    width = data_width + 20
    check(denominator, width)
    total = 0
    for value, coefficient in zip(values, coefficients, strict=True):
        check(value, data_width)
        total = check(total + multiply(value, coefficient, width), width)
    if denominator == 1:
        return total
    return divide_exact(total, denominator, width)

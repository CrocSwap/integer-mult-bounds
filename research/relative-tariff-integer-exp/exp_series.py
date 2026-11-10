"""Exact rational Taylor interval, evaluated with integer Horner arithmetic."""

from fractions import Fraction


def exp_interval(value: Fraction, degree: int = 24) -> tuple[Fraction, Fraction]:
    """Preserve the finite Taylor sum and the source's geometric tail exactly."""
    if type(value) is not Fraction or not 0 <= value <= Fraction(1, 4):
        raise ValueError("small nonnegative rational exponential domain")
    if type(degree) is not int or not 1 <= degree <= 64:
        raise ValueError("Taylor degree must be an integer in 1..64")
    a, b = value.numerator, value.denominator
    if max(a.bit_length(), b.bit_length()) > 4096:
        raise ValueError("rational components exceed 4096 bits")
    numerator, denominator = 1, 1
    for index in range(degree, 0, -1):
        denominator *= b * index
        numerator = denominator + a * numerator
    lower = Fraction(numerator, denominator)
    tail = Fraction(
        a ** (degree + 1) * (degree + 2),
        denominator * (degree + 1) * (b * (degree + 2) - a),
    )
    if not 1 <= lower <= lower + tail:
        raise ArithmeticError("positive Taylor interval invariant")
    return lower, lower + tail

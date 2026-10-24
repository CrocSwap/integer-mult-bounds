"""Exact half-up mixed-precision equality on bounded affine integer boxes."""
from fractions import Fraction

MAX_DIMENSION = 32
MAX_BITS = 2048
MAX_GAP = 256


def rational(value: int | Fraction) -> Fraction:
    """Validate one exact rational at the public boundary."""
    if type(value) not in (int, Fraction):
        raise ValueError("expected an integer or Fraction, excluding bool")
    result = Fraction(value)
    if max(abs(result.numerator).bit_length(), result.denominator.bit_length()) > MAX_BITS:
        raise ValueError("rational exceeds the bit limit")
    return result


def nearest(value: Fraction) -> int:
    """Round to an integer, with ties towards positive infinity."""
    return (2 * value.numerator + value.denominator) // (2 * value.denominator)


def centered(value: Fraction) -> Fraction:
    return value - nearest(value)


def equal_roundings(value: Fraction, gap: int) -> bool:
    scale = 1 << gap
    return scale * nearest(value) == nearest(scale * value)


def validate(offset, coefficients, widths, gap):
    if type(gap) is not int or not 1 <= gap <= MAX_GAP:
        raise ValueError("gap must be an integer in 1..256")
    if type(coefficients) is not tuple or type(widths) is not tuple:
        raise ValueError("coefficients and widths must be tuples")
    if len(coefficients) != len(widths) or len(widths) > MAX_DIMENSION:
        raise ValueError("dimension mismatch or more than 32 coordinates")
    for width in widths:
        if type(width) is not int or width < 0 or width.bit_length() > MAX_BITS:
            raise ValueError("invalid integer box width")
    return rational(offset), tuple(rational(a) for a in coefficients)


def first_exit(residue, deltas, widths, radius, upper):
    """Jump along a monotone box path to its first unsafe point."""
    point = [0] * len(widths)
    current = residue
    for i, (delta, width) in enumerate(zip(deltas, widths, strict=True)):
        if (delta > 0) != upper or delta == 0:
            continue
        endpoint = current + width * delta
        within = endpoint < radius if upper else endpoint >= -radius
        if within:
            point[i] = width
            current = endpoint
            continue
        if upper:
            ratio = (radius - current) / delta
            count = -((-ratio.numerator) // ratio.denominator)
        else:
            ratio = (current + radius) / (-delta)
            count = ratio.numerator // ratio.denominator + 1
        if not 1 <= count <= width:
            raise ArithmeticError("first-exit count is outside its box")
        point[i] = count
        return tuple(point)
    raise ArithmeticError("a failing extremum must have a first exit")


def analyze(offset, coefficients, widths, gap):
    """Return (safe, counterexample or None, minimum lift, maximum lift).

    Coarse-grid units are used. The box is 0 <= z_i <= widths[i].
    A false result contains an actual integer box point with unequal roundings.
    """
    offset, coefficients = validate(offset, coefficients, widths, gap)
    radius = Fraction(1, 2 << gap)
    residue = centered(offset)
    deltas = tuple(centered(a) if width else Fraction(0)
                   for a, width in zip(coefficients, widths, strict=True))
    lower = residue + sum(min(Fraction(0), a * b)
                          for a, b in zip(deltas, widths, strict=True))
    upper = residue + sum(max(Fraction(0), a * b)
                          for a, b in zip(deltas, widths, strict=True))
    if lower >= -radius and upper < radius:
        return True, None, lower, upper
    if not -radius <= residue < radius:
        witness = (0,) * len(widths)
    else:
        witness = first_exit(residue, deltas, widths, radius, upper >= radius)
    actual = offset + sum(a * z for a, z in zip(coefficients, witness, strict=True))
    if equal_roundings(actual, gap):
        raise ArithmeticError("constructed point does not witness failure")
    return False, witness, lower, upper

"""Select pairwise coprime square CRT axes without a primality test."""

from math import gcd, isqrt


def controller_shape(n):
    """Return p, log2 T, the axis count and the smaller width.

    A zero count selects the finite elementary branch.
    n is the number of bits in the longer operand.
    """
    if n < 2:
        return 0, 0, 0, 0
    b = (n - 1).bit_length()
    p = 6 * b
    target_min = (4 * n + b - 1) // b
    length = (target_min - 1).bit_length()
    count = number_of_axes(p, length)
    return p, length, count, length // count if count else 0


def number_of_axes(p, length):
    unit_width = (1 << 16) * (p + 1).bit_length() ** 3
    capacity = length // unit_width
    if not capacity:
        return 0
    return 1 << (capacity.bit_length() - 1)


def widths(log_extent, count):
    """Put the larger contiguous fields first, starting at axis zero."""
    short, excess = divmod(log_extent, count)
    return [short + (index < excess) for index in range(count)]


def production_widths(log_extent, count):
    """Select different dyadic widths while keeping the exact address length."""
    result = widths(log_extent, count)
    half = count // 2
    amplitude = (log_extent // count) // 8
    for i in range(half):
        transfer = amplitude - (i % (amplitude + 1))
        result[i] += transfer
        result[i + half] -= transfer
    return result


def square_interval(width, count, index):
    # Alternate two disjoint bands of relative deficits.
    target = 1 << width
    denom = (4 if index % 2 == 0 else 16) * count
    low_square = ((denom - 1) * target + denom - 1) // denom
    high_square = ((2 * denom - 1) * target) // (2 * denom)
    return max(3, 1 + isqrt(low_square - 1)), isqrt(high_square)


def select_squares(axis_widths):
    """Construct the first eligible square in each original axis order."""
    prefix = 2
    sides = []
    for axis, width in enumerate(axis_widths):
        low, high = square_interval(width, len(axis_widths), axis)
        for x in range(low | 1, high + 1, 2):
            if gcd(prefix, x) == 1:
                sides.append(x * x)
                prefix *= x
                break
        else:
            return None
    return sides

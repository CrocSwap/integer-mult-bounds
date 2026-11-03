"""Literal application of the cited PR4077 tariffs, without carry optimization."""

from itertools import product


def inherited_overhead(exponents, width, radix_width):
    """Additional non-radix actions in the shared method, from PR4077 §3–4."""
    overhead = 0
    for exponent in exponents:
        if exponent == 0:
            continue
        length = exponent.bit_length()
        zeros = width - length
        population = exponent.bit_count()
        construction = (2 * width + 3, width + 1 + 2 * zeros,
                        2 * width + 4 + 2 * zeros)
        decrements = (7 * exponent - 2 * population + 1,
                      2 * exponent - population + 2 * length + 1,
                      6 * exponent - 2 * population + 2 * length + 2)
        consumed_close = (7, 2, 8)
        unconsumed_close = (2 * length + 5, length + 1, 2 * length + 6)
        index_copy = (3 * width + 3, 0, 2 * width + 4)
        rundown = sum(construction) + sum(decrements) + sum(consumed_close)
        probe = sum(construction) + sum(unconsumed_close)
        overhead += (radix_width - 1) * rundown + probe + radix_width * sum(index_copy)
    return overhead


def exhaustive_maxima(width, radix_width):
    """Enumerate each ordered triple once in the fixed corroboration domain."""
    if type(width) is not int or not 1 <= width <= 5:
        raise ValueError("oracle width outside 1..5")
    if radix_width not in (1, 2, 3, 7):
        raise ValueError("oracle radix width outside the fixed fixture")
    limit = 1 << width
    maxima = [-1] * (3 * (limit - 1) + 1)
    visited = 0
    for exponents in product(range(limit), repeat=3):
        total = sum(exponents)
        value = inherited_overhead(exponents, width, radix_width)
        maxima[total] = max(maxima[total], value)
        visited += 1
    if visited != limit**3 or min(maxima) < 0:
        raise ValueError("incomplete triple inventory")
    return maxima, visited

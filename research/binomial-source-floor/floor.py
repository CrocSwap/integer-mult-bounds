"""Sharp source floors from inventory summaries. Apache-2.0."""

from math import comb


def need(condition, message):
    if not condition:
        raise ValueError(message)


def height(low, cap):
    """Bounded reference domain; the written theorem has no height cap."""
    need(type(low) is int and 2 <= low <= 16, "floor outside 2..16")
    need(type(cap) is int and 1 <= cap < low**7, "cap outside heights 0..6")
    result = 0
    for candidate in range(1, 7):
        if low**candidate <= cap:
            result = candidate
    return result


def source_floor(low, maximum, targets, paid, maximal, cap):
    """Return the exact minimum source count over the declared summaries."""
    degree = height(low, cap)
    need(type(maximum) is int and low < maximum <= 32, "maximum outside domain")
    need(type(targets) is int and 2 <= targets <= 8, "target count outside 2..8")
    need(type(paid) is int and targets <= paid <= 8, "require W <= Q <= 8")
    need(type(maximal) is int and 1 <= maximal < targets, "require 0 < t < W")
    correction = 0
    for depth in range(degree):
        remaining = degree - depth
        missing = sum(
            comb(remaining, high) * maximal**high
            * (targets - maximal)**(remaining - high)
            for high in range(remaining + 1)
            if low**(remaining - high) * maximum**high > cap
        )
        correction += paid**depth * missing
    return targets**(degree + 1) + (paid - targets) * correction

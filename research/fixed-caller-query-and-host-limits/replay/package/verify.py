"""Rational power enclosure retained from PR #7098 by Rohan Arun."""

SCALE = 10**30

def enclosure(rank, saving):
    exponent = 1 - saving
    target = rank**exponent.numerator * SCALE**exponent.denominator
    lower, upper = 0, (rank + 1) * SCALE
    while upper - lower > 1:
        mid = (lower + upper) // 2
        if mid**exponent.denominator <= target:
            lower = mid
        else:
            upper = mid
    return lower, upper

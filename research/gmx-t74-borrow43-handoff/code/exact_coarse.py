"""Exact integer evaluation of the retained degree-24 exponential enclosure.

Same polynomial, geometric tail and final rounding as the pinned rational engine.
Prepared under dataisfire with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
if not __debug__:
    raise RuntimeError('Assertions must be enabled')


def _polynomial(x):
    """Return A,D with A/D = sum(x**j/j!, j=0..24), without Fraction steps."""
    p, q = x.numerator, x.denominator
    total = coefficient = q_power = 1
    for j in range(23, -1, -1):
        q_power *= q
        coefficient *= j + 1
        total = total * p + coefficient * q_power
    return total, coefficient * q_power


def exponential(lower, upper, dyad=1 << 224):
    """Return exactly the original outward-rounded interval, not a tighter proxy."""
    if not isinstance(lower, (int, F)) or not isinstance(upper, (int, F)):
        raise TypeError('Exact rational endpoints required')
    lower, upper = F(lower), F(upper)
    assert 0 <= lower <= upper < F(1, 10)
    assert type(dyad) is int and dyad > 0
    a, d = _polynomial(lower)
    low = (a * dyad) // d
    a, d = _polynomial(upper)
    p, q = upper.numerator, upper.denominator
    # S24 + (u**25/25!) / (1-u/26), written over one integer denominator.
    remainder_denominator = 26 * q - p
    numerator = 25 * a * remainder_denominator + 26 * p**25
    denominator = 25 * d * remainder_denominator
    high = -((-numerator * dyad) // denominator)
    return F(low, dyad), F(high, dyad)


def moment(engine, profile, dimension, live, endpoint, bad=False):
    """Opt-in adapter; retains the original logs, weights, surcharge and rounding."""
    low = high = F(0)
    for rank, count in profile.items():
        assert 0 < rank < dimension and count > 0
        l, u = engine.logarithm(F(dimension, rank))
        e, f = exponential(endpoint*l, endpoint*u, engine.DYAD)
        weight = F(rank*count, dimension*live)
        low += weight*e
        high += weight*f
    if bad:
        l, u = engine.logarithm(F(dimension))
        e, f = exponential(endpoint*l, endpoint*u, engine.DYAD)
        weight = F(32*dimension*sum(profile.values()), 10**16*live)
        low += weight*e
        high += weight*f
    return engine.floor(low), engine.ceil(high)

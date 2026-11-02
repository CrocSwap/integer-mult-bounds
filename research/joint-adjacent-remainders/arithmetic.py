"""Two shared quotient-correction comparisons for moduli p+1 and p+2.

Produced by Nick Petalas. Apache-2.0.
The comparison bill concerns the trusted digit core, not boundary validation.
"""

MAX_RADIX_BITS = 4096


def prepare(p):
    """Prepare a bounded implementation of the all-p mathematical construction."""
    if type(p) is not int or p < 2 or p.bit_length() > MAX_RADIX_BITS:
        raise ValueError("radix must be an integer >=2 with at most 4096 bits")
    q1 = p + 1
    q2 = p + 2
    return p, q1, q2, q2 + q2, p * q2


def digit_core(context, a, r):
    """Require 0<=a<=p+1, 0<=r<p and a context returned by prepare(p).

    Return both remainders, the constant correction pair and the two predicate
    outcomes. This trusted core performs no division, remainder or lookup.
    """
    _p, q1, q2, twice_q2, _limit = context
    d = r - a
    e = d - a
    first = d < 0
    if first:
        second = e < -q2
        if second:
            return d + q1, e + twice_q2, (1, 2), (first, second)
        return d + q1, e + q2, (1, 1), (first, second)
    second = e < 0
    if second:
        return d, e + q2, (0, 1), (first, second)
    return d, e, (0, 0), (first, second)


def reduce_pair(context, x):
    """Validate the input prefix, split its digits, then call the trusted core."""
    p, _q1, _q2, _twice_q2, limit = context
    if type(x) is not int or not 0 <= x < limit:
        raise ValueError("input must be an integer in [0,p*(p+2))")
    a, r = divmod(x, p)
    return digit_core(context, a, r)


def separate_core(context, a, r):
    """An attaining independent-tree baseline in the stated comparison model."""
    _p, q1, q2, twice_q2, _limit = context
    d = r - a
    e = d - a
    first = d < 0
    left = d + q1 if first else d
    negative = e < 0
    if not negative:
        return left, e, (int(first), 0), (first, negative)
    deep = e < -q2
    if deep:
        return left, e + twice_q2, (int(first), 2), (first, negative, deep)
    return left, e + q2, (int(first), 1), (first, negative, deep)

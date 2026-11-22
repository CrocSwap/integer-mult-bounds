"""Serial bit operations for the fixed installer's reduced rational arithmetic."""

from itertools import zip_longest


def canonical(word):
    return word.lstrip("0") or "0"


def compare(a, b):
    """Scan two canonical magnitudes from their high ends."""
    first = 0
    for x, y in zip_longest(a, b):
        if x is None:
            return -1
        if y is None:
            return 1
        if not first:
            first = (x > y) - (x < y)
    return first


def combine(a, b, subtract=False):
    """Add two magnitudes, or subtract b from a when a >= b."""
    output = []
    carry = 0
    for x, y in zip_longest(reversed(a), reversed(b), fillvalue="0"):
        digit = (x == "1") + carry + (-1 if subtract else 1) * (y == "1")
        carry, bit = divmod(digit, 2)
        output.append("01"[bit])
    if carry == 1:
        output.append("1")
    if carry < 0:
        raise ArithmeticError("negative magnitude")
    return "".join(reversed(output))


def times(a, b):
    """Use one shift and at most one addition per digit of b."""
    r = "0"
    for digit in b:
        r = r + "0"
        if digit == "1":
            r = combine(r, a)
        r = canonical(r)
    return r


def quotient_remainder(a, b):
    """Return the exact quotient and remainder of two canonical magnitudes."""
    if b == "0":
        raise ZeroDivisionError
    tail = iter(a)
    for _ in b:
        if next(tail, None) is None:
            return "0", a
    zero_tail = "".join("0" for _ in tail)
    divisor = b + zero_tail
    quotient = []
    for _ in "1" + zero_tail:
        # The two words retain the dividend width throughout this loop.
        take = a >= divisor
        quotient.append("1" if take else "0")
        if take:
            a = combine(a, divisor, subtract=True)
        divisor = "0" + divisor[:-1]
    return canonical("".join(quotient)), canonical(a)


def signed(sign, mag):
    return (1 if mag == "0" else sign, mag)


def sum_signed(x, y):
    sx, a = x
    sy, b = y
    if sx == sy:
        return signed(sx, canonical(combine(a, b)))
    if compare(a, b) < 0:
        sx, a, b = sy, b, a
    return signed(sx, canonical(combine(a, b, subtract=True)))


def neg(x):
    return signed(-x[0], x[1])


def product_signed(x, y):
    return signed(x[0] * y[0], times(x[1], y[1]))


def bezout(a, b):
    """Return g,u,v with g >= 0 and u*a + v*b = g for signed integers."""
    sa, a = a
    sb, b = b
    unit, zero = (1, "1"), (1, "0")
    rows = ((unit, zero), (zero, unit))
    if compare(a, b) < 0:
        a, b = b, a
        rows = rows[::-1]
    while b != "0":
        q, r = quotient_remainder(a, b)
        old, current = rows
        after = tuple(sum_signed(u, neg(product_signed(v, (1, q))))
                      for u, v in zip(old, current))
        rows = current, after
        a, b = b, r
    x, y = rows[0]
    return a, signed(sa * x[0], x[1]), signed(sb * y[0], y[1])


def exact_quotient(a, b):
    q, r = quotient_remainder(a, b)
    if r != "0":
        raise ArithmeticError("inexact division")
    return q


def reduced(num, den):
    if den[1] == "0":
        raise ZeroDivisionError
    g = bezout(num, den)[0]
    return signed(num[0] * den[0], exact_quotient(num[1], g)), exact_quotient(den[1], g)


def rational(op, x, y):
    """Evaluate a field operation on pairs of signed numerator and positive denominator."""
    a, b = x
    c, d = y
    if op == "/":
        return reduced(product_signed(a, (1, d)), product_signed((1, b), c))
    denominator = product_signed((1, b), (1, d))
    if op == "*":
        return reduced(product_signed(a, c), denominator)
    if op not in ("+", "-"):
        raise ValueError(op)
    left = product_signed(a, (1, d))
    right = product_signed(c, (1, b))
    return reduced(sum_signed(left, right if op == "+" else neg(right)), denominator)

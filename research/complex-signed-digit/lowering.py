"""Paid signed-digit coefficient circuits. Apache-2.0; OpenAI Codex assistance."""

from fractions import Fraction


def numerator_digits(n):
    """Most significant first non-adjacent digits of a positive integer."""
    if type(n) is not int or n <= 0:
        raise ValueError("positive integer numerator required")
    digits = []
    while n:
        digit = 2 - n % 4 if n % 2 else 0
        digits.append(digit)
        n = (n - digit) // 2
    return digits[::-1]


def circuit(q, signed=True):
    """Lower t += q*s, with distinct t,s,w and arbitrary initial private w.

    Each tuple is one real primitive. Both real components execute this word.
    The original clear/leading-add initialization is retained for attribution.
    """
    q = Fraction(q)
    if not q or q.denominator & (q.denominator - 1):
        raise ValueError("nonzero dyadic coefficient required")
    n = abs(q.numerator)
    binary = [int(bit) for bit in bin(n)[2:]]
    digits = numerator_digits(n) if signed else binary
    if len(digits) + sum(d != 0 for d in digits) >= len(binary) + sum(binary):
        digits = binary
    ops = [("clear", "w")]
    for i, digit in enumerate(digits):
        if i:
            ops.append(("double", "w"))
        if digit:
            ops.append(("add" if digit == 1 else "sub", "w", "s"))
    ops.extend([("half", "w")] * (q.denominator.bit_length() - 1))
    ops.extend([("add" if q > 0 else "sub", "t", "w"), ("clear", "w")])
    return ops

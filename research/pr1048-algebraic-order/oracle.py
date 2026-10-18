"""Separate polynomial-GCD / rational-bisection regression oracle.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
This module does not import compare.py or use its factored-difference rule.
It is a finite implementation check, not a proof of the general theorem.
"""
from fractions import Fraction


def polynomial(counts, roles):
    coefficients = [Fraction(-8 * roles), Fraction(0), Fraction(0), Fraction(0)]
    for rank, count in zip((1, 2, 4), counts):
        exponent = (8 // rank).bit_length() - 1
        coefficients[exponent] += rank * count
    return trim(coefficients)


def trim(p):
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def evaluate(p, x):
    total = Fraction(0)
    for coefficient in reversed(p):
        total = total * x + coefficient
    return total


def gcd(a, b):
    a, b = trim(a), trim(b)
    while b:
        remainder = a[:]
        while remainder and len(remainder) >= len(b):
            shift = len(remainder) - len(b)
            quotient = remainder[-1] / b[-1]
            for i, coefficient in enumerate(b):
                remainder[i + shift] -= quotient * coefficient
            remainder = trim(remainder)
        a, b = b, remainder
    return [coefficient / a[-1] for coefficient in a] if a else []


def isolate(p, steps=64):
    lower, upper = Fraction(1), Fraction(2)
    if not evaluate(p, lower) < 0 < evaluate(p, upper):
        raise ValueError("oracle requires a root strictly between 1 and 2")
    for _ in range(steps):
        mid = (lower + upper) / 2
        value = evaluate(p, mid)
        if value == 0:
            return mid, mid
        if value < 0:
            lower = mid
        else:
            upper = mid
    return lower, upper


def root_order(a, b, interval_a=None, interval_b=None):
    if a == b:
        return 0
    la, ua = interval_a if interval_a is not None else isolate(a)
    lb, ub = interval_b if interval_b is not None else isolate(b)
    if ua < lb:
        return -1
    if ub < la:
        return 1
    common = gcd(a, b)
    if len(common) == 2:
        root = -common[0] / common[1]
        if 1 < root < 2 and evaluate(a, root) == evaluate(b, root) == 0:
            return 0
    # A finite cap fails visibly; an overlapping bracket is never a tie.
    for steps in (128, 256, 512):
        la, ua = isolate(a, steps)
        lb, ub = isolate(b, steps)
        if ua < lb:
            return -1
        if ub < la:
            return 1
    raise ValueError("unresolved root comparison after 512 bisections")

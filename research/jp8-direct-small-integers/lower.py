"""Direct small-integer target accumulation; Apache-2.0.

Michał Ciemięga (@zewelor), with substantial OpenAI Codex assistance.
PR696 supplies the baseline and the arbitrary-dirty, cleared-work contract.
"""
from fractions import Fraction


def lower(op, baseline):
    """Keep the original macro boundary, frame and private-work clear."""
    original = baseline(op)  # Retain predecessor validation, including aliases.
    if op[0] != "add":
        return original
    q = Fraction(op[3], op[4])
    if abs(q) not in (2, 3):
        return original
    target, source = tuple(op[1]), tuple(op[2])
    update = ("add" if q > 0 else "subtract", target, source)
    return [update] * abs(q.numerator) + [("clear", ("W", 0))]

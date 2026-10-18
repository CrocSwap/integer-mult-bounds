"""Prefix-bounded signed Horner circuits. Apache-2.0.

Chris Pagolu, with substantial OpenAI Codex assistance.
The copied/unit baseline is Sagar Thakrar's pinned PR696 implementation.
The primitive interface follows icekylinx's PR425/433/531 lineage.
"""
from fractions import Fraction
from functools import lru_cache

from vendor.pr696_lower import lower as binary_lower


@lru_cache(maxsize=None)
def bounded_digits(n, bound):
    """Shortest signed-binary Horner word for n, with coefficient <= bound.

    A word begins at 1; each digit doubles then optionally adds/subtracts 1.
    The doubled intermediate, not just the completed digit, must fit bound.
    This is a restricted word class, not general addition-chain optimality.
    Returns the digits after the leading 1. Digit costs are 1 + abs(digit).
    """
    if not isinstance(n, int) or not isinstance(bound, int) or not 1 <= n <= bound:
        raise ValueError("expected integers 1 <= n <= bound")
    if n == 1:
        return ()
    if n % 2 == 0:
        return bounded_digits(n // 2, bound) + (0,)
    choices = [bounded_digits((n - 1) // 2, bound) + (1,)]
    if n + 1 <= bound:
        choices.append(bounded_digits((n + 1) // 2, bound) + (-1,))
    # Prefer fewer subtractions on equal cost, then deterministic lexicography.
    return min(choices, key=lambda ds: (sum(1 + abs(d) for d in ds), ds.count(-1), ds))


def lower(op, work=("W", 0)):
    """Lower one macro; additions accept dirty work and leave it zero.

    Source access, coefficient synthesis, halving, accumulation and clearing
    are all explicit. Every primitive runs at the input macro's own frame.
    """
    reference = binary_lower(op, work)  # Also validates the inherited domain.
    if op[0] != "add":
        return reference
    q = Fraction(op[3], op[4])
    if abs(q) == 1:
        return reference
    target, source = tuple(op[1]), tuple(op[2])
    n = abs(q.numerator)
    result = [("copy", work, source)]
    for digit in bounded_digits(n, n):
        result.append(("double", work))
        if digit:
            result.append(("add" if digit > 0 else "subtract", work, source))
    result += [("halve", work)] * (q.denominator.bit_length() - 1)
    result += [("add" if q > 0 else "subtract", target, work), ("clear", work)]
    if len(result) > len(reference):
        raise ValueError("bounded word is worse than its binary candidate")
    return result

"""Exact multiplicities for two independent tensor-capacity losses.

Produced by Nick Petalas. Apache-2.0.
The caller must establish the disjoint-prime hypothesis in PROOF.md.
"""

from dataclasses import dataclass
from fractions import Fraction

MAX_RANK = 4096
MAX_LENGTH = 4096


@dataclass(frozen=True, slots=True)
class Schedule:
    crossing: int
    counts: tuple[int, ...]
    density: Fraction


def validate(r: int, c: int, s: int, d: int, n: int) -> None:
    """Validate the bounded numeric interface, including strict defects."""
    if any(type(x) is not int for x in (r, c, s, d, n)):
        raise TypeError("ranks, capacities and length must be integers")
    if not (1 <= c < r <= MAX_RANK and 1 <= d < s <= MAX_RANK):
        raise ValueError("require 1 <= capacity < rank <= 4096 for both types")
    if not 1 <= n <= MAX_LENGTH:
        raise ValueError("require 1 <= length <= 4096")


def optimize(r: int, c: int, s: int, d: int, n: int) -> Schedule:
    """Return every optimal first-type count and the exact unit density.

    This optimizes min((c/r)**a, (d/s)**(n-a)). It does not certify that
    physical cuts exist, or that supplied profiles have disjoint defects.
    """
    validate(r, c, s, d, n)
    low, high = 0, n
    for _ in range(n.bit_length() + 1):
        if high - low == 1:
            break
        middle = (low + high) // 2
        if r**middle * d ** (n - middle) <= c**middle * s ** (n - middle):
            low = middle
        else:
            high = middle
    if high - low != 1:
        raise RuntimeError("crossing search exhausted its proven bound")
    left = Fraction(d, s) ** (n - low)
    right = Fraction(c, r) ** high
    best = max(left, right)
    counts = tuple(a for a, value in ((low, left), (high, right)) if value == best)
    return Schedule(low, counts, best)

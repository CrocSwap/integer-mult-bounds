"""Exact root ordering for equal-mass proper dyadic width-eight profiles.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
No supplier, logarithm, exponential, or predecessor implementation is imported.
"""
from dataclasses import dataclass
from fractions import Fraction as Q


def sign(value):
    return (value > 0) - (value < 0)


@dataclass(frozen=True)
class Profile:
    counts: tuple
    roles: int

    def __post_init__(self):
        if type(self.counts) is not tuple or len(self.counts) != 3:
            raise ValueError("counts must be a tuple for ranks (1,2,4)")
        if any(type(n) is not int or n < 0 for n in self.counts):
            raise ValueError("counts must be nonnegative integers")
        if type(self.roles) is not int or self.roles <= 0:
            raise ValueError("roles must be a positive integer")
        if not self.mass < 8 * self.roles or not sum(self.counts) > self.roles:
            raise ValueError("requires a unique root strictly inside 0<a<1")

    @property
    def mass(self):
        n1, n2, n4 = self.counts
        return n1 + 2 * n2 + 4 * n4

    def residual(self, t):
        """8W times (moment minus one), in t=2**a, evaluated exactly."""
        t = Q(t)
        n1, n2, n4 = self.counts
        return ((n1 * t + 2 * n2) * t + 4 * n4) * t - 8 * self.roles


def difference(a, b):
    if a.roles != b.roles or a.mass != b.mass:
        raise ValueError("profiles must have the same roles and rank mass")
    return a.counts[0] - b.counts[0], a.counts[2] - b.counts[2]


def crossing(a, b):
    """The unique crossing in 1<t<2, or None (identical curves included)."""
    u, v = difference(a, b)
    if u:
        c = Q(4 * v, u)
        if 1 < c < 2:
            return c
    return None


def root_order(a, b):
    """Return sign(root_a - root_b); larger a is the better moment root.

    Difference: P_a(t)-P_b(t) = t(t-1)(u*t-4*v).
    At a's root, sign(root_a-root_b) = -sign(u*t_a-4*v).
    For 1<c=4*v/u<2, monotonicity gives sign(t_a-c)=-sign(P_a(c)).
    """
    u, v = difference(a, b)
    if u == 0:
        return sign(v)
    c = Q(4 * v, u)
    if c <= 1:
        return -sign(u)
    if c >= 2:
        return sign(u)
    return sign(u) * sign(a.residual(c))

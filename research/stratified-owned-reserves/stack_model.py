"""Exact reference accounting; this is not an executed supplier dispatcher.

Prepared for CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


@dataclass(frozen=True)
class Stage:
    name: str
    contraction: Fraction
    local: tuple[Fraction, ...]
    lower: tuple[tuple[str, Fraction], ...] = ()


def potentials(stages: Sequence[Stage]) -> dict[str, tuple[Fraction, ...]]:
    """Least coordinatewise certificate for the stated stratified relaxation."""
    if not stages:
        raise ValueError("empty stage list")
    tapes = len(stages[0].local)
    if not tapes:
        raise ValueError("no tape coordinates")
    answer = {}
    for stage in stages:
        rho = Fraction(stage.contraction)
        local = tuple(Fraction(c) for c in stage.local)
        lower = tuple((name, Fraction(a)) for name, a in stage.lower)
        if stage.name in answer or not 0 <= rho < 1:
            raise ValueError("duplicate stage or noncontracting same-stage edge")
        if len(local) != tapes or any(c < 0 for c in local):
            raise ValueError("invalid local tape envelope")
        if any(name not in answer or a <= 0 for name, a in lower):
            raise ValueError("a lower edge must descend to a preceding stage")
        answer[stage.name] = tuple(
            max([c / (1 - rho)] +
                [c + a * answer[name][t]
                 for name, a in lower])
            for t, c in enumerate(local)
        )
    return answer


def selected_relaxation(q1: int, q2: int,
                        local: Sequence[Sequence[int | Fraction]] | None = None
                        ) -> tuple[Stage, ...]:
    """The six source application stages, with conservative factors only.

    q values here are geometric parameters, not admission certificates.
    B0 abbreviates a separate complete relative-space contract.
    """
    if q1 < 3 or q2 < 3:
        raise ValueError("q must be at least three")
    rows = local if local is not None else [(1,)] * 6
    if len(rows) != 6:
        raise ValueError("six local envelopes required")
    a = [tuple(Fraction(x) for x in row) for row in rows]
    p1, p2 = Fraction(2 * q1 * q1), Fraction(2 * q2 * q2)
    return (
        Stage("B0", Fraction(0), a[0]),
        Stage("K1", Fraction(1, 2), a[1], (("B0", Fraction(4)),)),
        Stage("O1", Fraction(0), a[2], (("K1", p1), ("B0", p1))),
        Stage("K2", Fraction(1, 2), a[3], (("O1", Fraction(4)),)),
        Stage("O2", Fraction(0), a[4], (("K2", p2), ("O1", p2))),
        Stage("C", Fraction(1, 2), a[5], (("O2", Fraction(1)),)),
    )


def ceil_div(a: int, b: int) -> int:
    if a < 0 or b <= 0:
        raise ValueError("ceil_div domain")
    return (a + b - 1) // b


def ceil_log(n: int, base: int) -> int:
    if n < 1 or base < 2:
        raise ValueError("ceil_log domain")
    power, depth = 1, 0
    while power < n:
        power *= base
        depth += 1
    return depth


def atom_width(e: int, numerator: int = 1, denominator: int = 250) -> int:
    """Smallest positive w satisfying w**denominator >= e**numerator."""
    if e < 1 or not 0 < numerator < denominator:
        raise ValueError("atom-width domain")
    target = e ** numerator
    lo, hi = 1, e
    while lo < hi:
        mid = (lo + hi) // 2
        if mid ** denominator < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def stock_exponents(e: int, n: int, numerator: int = 1,
                    denominator: int = 250) -> tuple[int, int, int]:
    """w, exponent of L, exponent of q in W(w)**D; old stock is separate."""
    w = atom_width(e, numerator, denominator)
    d = 2 + ceil_log(max(1, ceil_div(e, w)), n)
    return w, d, n * n * (w - 1) * d


def reserve_envelope(e_max: int, n: int, numerator: int = 1,
                     denominator: int = 250) -> tuple[int, int, int]:
    w = atom_width(e_max, numerator, denominator)
    d = 2 + ceil_log(max(1, e_max), n)
    return w, d, n * n * (w - 1) * d


def mixed_rank(coordinates: Sequence[int], radices: Sequence[int]) -> int:
    if len(coordinates) != len(radices) or any(r < 1 for r in radices):
        raise ValueError("bad mixed-radix shape")
    out = 0
    for digit, radix in zip(coordinates, radices, strict=True):
        if not 0 <= digit < radix:
            raise ValueError("digit outside its own reservation")
        out = out * radix + digit
    return out


def mixed_unrank(value: int, radices: Sequence[int]) -> tuple[int, ...]:
    if value < 0 or any(r < 1 for r in radices):
        raise ValueError("bad mixed-radix rank")
    result = []
    for radix in reversed(radices):
        value, digit = divmod(value, radix)
        result.append(digit)
    if value:
        raise ValueError("rank outside complete reservation")
    return tuple(reversed(result))

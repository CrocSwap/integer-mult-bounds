"""Exact checks for the uniform-fee target-refinement theorem.

Part A enumerates every integer partition of every target rank R <= R_MAX and
compares the true optimum with the closed form for exact rational concave
tariffs and fees.  Part B certifies the halving thresholds for the power
tariff r**t at the selected exponent with correctly rounded decimal arithmetic.
Standard library only.
"""

from __future__ import annotations

import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Callable, Iterator

R_MAX = 22
SELECTED_KAPPA = Fraction(781451, 250000000)
FEE_RANKS = (1, 2, 4, 8)
EXPECTED_THRESHOLDS = {1: 470, 2: 940, 4: 1880, 8: 3760}
DIGITS = 60
MARGIN = Decimal("1e-40")

Tariff = Callable[[int], Fraction]


def partitions(n: int, largest: int) -> Iterator[tuple[int, ...]]:
    """Yield the partitions of n with parts at most `largest`, nonincreasing."""
    if n == 0:
        yield ()
        return
    for first in range(min(n, largest), 0, -1):
        for rest in partitions(n - first, first):
            yield (first,) + rest


def balanced(phi: Tariff, rank: int, pieces: int) -> Fraction:
    q, r = divmod(rank, pieces)
    return r * phi(q + 1) + (pieces - r) * phi(q)


def harmonic(n: int) -> Fraction:
    return sum((Fraction(1, j) for j in range(1, n + 1)), Fraction(0))


def tariffs() -> dict[str, Tariff]:
    """Exact increasing concave tariffs with phi(0) = 0 on 0..R_MAX."""
    width = R_MAX
    menu: dict[str, Tariff] = {
        "linear": lambda n: Fraction(n),
        "harmonic": harmonic,
        "quadratic": lambda n: Fraction(n * (2 * width - n), width),
    }
    for cap in (1, 2, 3, 5, 8):
        menu[f"cap{cap}"] = lambda n, cap=cap: Fraction(min(n, cap))
    return menu


def is_concave_increasing(phi: Tariff) -> bool:
    values = [phi(n) for n in range(R_MAX + 1)]
    steps = [b - a for a, b in zip(values, values[1:])]
    return (
        values[0] == 0
        and all(s >= 0 for s in steps)
        and all(a >= b for a, b in zip(steps, steps[1:]))
    )


def predicted_optimum(phi: Tariff, rank: int, fee: Fraction) -> tuple[Fraction, int]:
    """Closed form: first k whose next balanced increment is at most the fee."""
    k = 1
    while k < rank and balanced(phi, rank, k + 1) - balanced(phi, rank, k) > fee:
        k += 1
    return balanced(phi, rank, k) - (k - 1) * fee, k


def check_exact() -> int:
    fees = sorted({Fraction(a, b) for a in range(0, 13) for b in (1, 2, 3, 7)})
    checks = 0
    for name, phi in tariffs().items():
        if not is_concave_increasing(phi):
            raise AssertionError(f"tariff {name} is not concave increasing")
        for rank in range(1, R_MAX + 1):
            best_by_k: dict[int, Fraction] = {}
            for part in partitions(rank, rank):
                credit = sum((phi(x) for x in part), Fraction(0))
                k = len(part)
                if credit > best_by_k.get(k, Fraction(-1)):
                    best_by_k[k] = credit
            ks = sorted(best_by_k)
            for k in ks:
                if best_by_k[k] != balanced(phi, rank, k):
                    raise AssertionError(f"balanced not optimal: {name} R={rank} k={k}")
                checks += 1
            for k in ks[1:-1]:
                if best_by_k[k - 1] + best_by_k[k + 1] > 2 * best_by_k[k]:
                    raise AssertionError(f"not concave: {name} R={rank} k={k}")
                checks += 1
            for fee in fees:
                truth = max(best_by_k[k] - (k - 1) * fee for k in ks)
                value, k_star = predicted_optimum(phi, rank, fee)
                if value != truth or best_by_k[k_star] - (k_star - 1) * fee != truth:
                    raise AssertionError(f"optimum mismatch: {name} R={rank} fee={fee}")
                halving_pays = rank >= 2 and balanced(phi, rank, 2) - phi(rank) > fee
                if halving_pays != (truth > phi(rank)):
                    raise AssertionError(f"halving test fails: {name} R={rank} fee={fee}")
                checks += 1
    return checks


def failure_controls() -> int:
    """The theorem's hypotheses matter: a convex tariff breaks the halving test."""
    convex: Tariff = lambda n: Fraction(n * n)
    if is_concave_increasing(convex):
        raise AssertionError("convex control misclassified")
    # Halving never pays under a convex tariff, yet the theorem's balanced
    # rule is not optimal for fixed k: (R-1, 1) beats the balanced pair.
    rank = 6
    if balanced(convex, rank, 2) >= convex(5) + convex(1):
        raise AssertionError("convex control did not separate balanced split")
    # Increasing but non-concave tariff (found by a small exhaustive search):
    # halving does not pay at fee 0, yet the balanced three-way split does.
    table = (0, 0, 1, 1, 1, 1, 2)
    bumpy: Tariff = lambda n: Fraction(table[n])
    fee = Fraction(0)
    halving = max(bumpy(a) + bumpy(rank - a) for a in range(1, rank)) - bumpy(rank)
    three = 3 * bumpy(2) - 2 * fee - bumpy(rank)
    steps = [b - a for a, b in zip(table, table[1:])]
    concave = all(a >= b for a, b in zip(steps, steps[1:]))
    if concave or min(steps) < 0 or halving > fee or three <= 0:
        raise AssertionError("non-concave control did not separate the halving test")
    return 2


def power(n: int, t: Decimal) -> Decimal:
    return Decimal(0) if n == 0 else (t * Decimal(n).ln()).exp()


def halving_gain(rank: int, t: Decimal) -> Decimal:
    low = rank // 2
    return power(low, t) + power(rank - low, t) - power(rank, t)


def check_thresholds() -> dict[int, int]:
    found: dict[int, int] = {}
    with localcontext() as ctx:
        ctx.prec = DIGITS
        t = Decimal(SELECTED_KAPPA.denominator - SELECTED_KAPPA.numerator) / Decimal(
            SELECTED_KAPPA.denominator
        )
        limit = 2 * max(EXPECTED_THRESHOLDS.values())
        gains = [Decimal(0), Decimal(0)] + [halving_gain(r, t) for r in range(2, limit + 1)]
        for q in FEE_RANKS:
            fee = power(q, t)
            for rank in range(2, limit + 1):
                gap = gains[rank] - fee
                if abs(gap) < MARGIN:
                    raise AssertionError(f"uncertified sign at R={rank} q={q}")
                if gap > 0 and q not in found:
                    found[q] = rank
            if q not in found:
                raise AssertionError(f"no threshold for q={q}")
            first = found[q]
            if any(gains[r] - fee > 0 for r in range(2, first)):
                raise AssertionError("threshold not least")
            if any(gains[r] - fee <= 0 for r in range(first, limit + 1)):
                raise AssertionError(f"profit not monotone above threshold q={q}")
    if found != EXPECTED_THRESHOLDS:
        raise AssertionError(f"thresholds {found} != {EXPECTED_THRESHOLDS}")
    return found


def main() -> int:
    exact = check_exact()
    controls = failure_controls()
    found = check_thresholds()
    summary = " ".join(f"q{q}:R>={r}" for q, r in sorted(found.items()))
    print(
        f"PASS_UNIFORM_FEE_TARGET_REFINEMENT exact_checks={exact} "
        f"controls={controls} thresholds={summary}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

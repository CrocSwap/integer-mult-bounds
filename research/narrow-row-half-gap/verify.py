#!/usr/bin/env python3
"""Explicit half-gap budget for #4100's narrow reference row.

The checker uses only the standard library. It pins the one-sentence claim,
proves the ideal certificate 1-S >= 1/(8p^2) by exact comparisons, and checks
that alias removal and band truncation preserve that certificate while a
rounding defect of 1/(16p^2) leaves a row gap of 1/(16p^2).
"""

from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FINE = ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md"
GAUSSIAN = ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"
LOGA = ROOT / "research/capped-phase-fusion/LOG-A-PHASE-SCHUR-AUDIT.md"
COVERAGE = ROOT / "docs/research/pr4100-audit-coverage-map.md"
COLUMN = ROOT / "research/gaussian-gauge-column/README.md"

HALF_SENTENCE = (
    "Omitting the exponentially small nonzero diagonal aliases and setting the\n"
    "diagonal exactly to one preserves a polynomial gap. Exponentially accurate\n"
    "band truncation and coefficient rounding preserve half of it."
)
GAUSSIAN_CLAIM = (
    "round at sufficiently high fixed precision so the reference H has diagonal1,\n"
    "row gap delta>=1/(16p^2) and row norm<2."
)


def series(y, n):
    """Partial sum of exp(y) through degree n, as an exact rational."""
    total = Fraction(0)
    term = Fraction(1)
    for k in range(n + 1):
        total += term
        term *= y / (k + 1)
    return total


def exp2_upper():
    """exp(2) < sum_{k=0}^{8} 2^k/k! + 2^9/9! * 10/8 < 8."""
    total = series(Fraction(2), 8)
    # Next term is 2^9/9!, and later terms shrink by at most 2/10.
    remainder = Fraction(2) ** 9 / series_factorial(9) * Fraction(10, 8)
    return total + remainder


def series_factorial(n):
    value = 1
    for k in range(2, n + 1):
        value *= k
    return value


def ideal_certificate():
    """1 - exp(-2a theta) - 5 exp(-2a) >= 1/(8p^2) at the parameter minimum."""
    # exp(2) < 8, so ln(8) > 2 and ln(16p) > 2 for every integer p >= 1.
    if not exp2_upper() < 8:
        raise AssertionError(exp2_upper())
    # exp(1) > 8/3, so 1 - exp(-1) > 5/8.
    if not series(Fraction(1), 6) > Fraction(8, 3):
        raise AssertionError(series(Fraction(1), 6))
    # exp(7/2) > 2, used for the inductive step p -> p+1.
    if not series(Fraction(7, 2), 2) > 2:
        raise AssertionError(series(Fraction(7, 2), 2))
    # exp(9/2) > 48, so the worst-case x is at most 1 at p = 3.
    if not series(Fraction(9, 2), 5) > 48:
        raise AssertionError(series(Fraction(9, 2), 5))

    # p = 1, 2: worst-case x >= 1, so 1-exp(-x) > 5/8.
    for p in (1, 2):
        tail = Fraction(5, (16 * p) ** 8)
        if not Fraction(5, 8) - tail >= Fraction(1, 8 * p * p):
            raise AssertionError((p, Fraction(5, 8) - tail))

    # Every p >= 1: 2/p^2 - 5/(16p)^8 >= 1/(8p^2), the x <= 1 branch.
    # 15 * 2^32 >= 40 is the cleared denominator at p = 1, and p^6 only helps.
    if not 15 * (1 << 32) >= 40:
        raise AssertionError("uniform polynomial comparison")


def gap_lower(off, diagonal=1):
    return diagonal - off


def operations_preserve(p):
    """Worst case and a strict improvement, for one integer p."""
    gamma = Fraction(1, 8 * p * p)
    budget = Fraction(1, 16 * p * p)
    # Certified row: Off + |d - 1| <= 1 - gamma, d >= 0.
    # Tight case d = 1, Off = 1 - gamma, nothing truncated.
    off = 1 - gamma
    final_off = off + budget
    if gap_lower(final_off) < budget:
        raise AssertionError((p, gap_lower(final_off)))
    if gap_lower(final_off) != gamma - budget:
        raise AssertionError("tight rounding should spend exactly the budget")
    # Row norm is 1 + off-sum < 2.
    if not 1 + final_off < 2:
        raise AssertionError((p, 1 + final_off))
    # Positive alias mass and a deleted tail both increase the gap.
    alias = Fraction(1, 100 * p * p)
    removed = Fraction(1, 100 * p * p)
    improved = off - alias - removed + budget
    if not gap_lower(improved) > budget:
        raise AssertionError((p, gap_lower(improved)))
    # Spending the whole certificate leaves gap 0. One extra unit makes it negative.
    if gap_lower(off + gamma) != 0:
        raise AssertionError("full certificate is sharp")
    if not gap_lower(off + gamma + Fraction(1, p * p)) < 0:
        raise AssertionError("control past the certificate should fail")


def per_entry_budget():
    """At most 2p entries, each moved by at most 2^{-5p}, meet the row budget.

    At p=1 the two sides are equal. For p>=1, (1+1/p)^3 <= 8 <= 32, so
    32(p+1)^3 <= 2^5 * 32 p^3. The inequality therefore persists for every
    larger integer once it holds at p=1.
    """
    if 32 * 1 ** 3 != 2 ** 5:
        raise AssertionError("C=5 should meet p=1 with equality")
    if (1 + 1) ** 3 > 32:
        raise AssertionError("inductive factor")
    if 32 * 1 ** 3 <= 2 ** (4 * 1):
        raise AssertionError("C=4 must fail at p=1")
    # The rejected per-entry copy of the old 1/(16p) margin.
    for p in range(2, 21):
        band = 2 * p - 1
        if not Fraction(band, 16 * p) > Fraction(1, 8 * p * p):
            raise AssertionError(("coarse row charge", p))


def polynomial_threshold(c, degree):
    """Smallest p such that p^degree / 2^{c p} <= 1/(16 p^2) from there on."""
    power = degree + 2
    for p in range(1, 10000):
        holds = 16 * p ** power <= 2 ** (c * p)
        increases = (1 << c) * p ** power >= (p + 1) ** power
        if holds and increases:
            return p
    raise AssertionError((c, degree))


def polynomial_thresholds():
    expected = {0: 11, 1: 16, 2: 22, 3: 29, 4: 35, 5: 42, 6: 49, 7: 57, 8: 64}
    for degree, want in expected.items():
        got = polynomial_threshold(1, degree)
        if got != want:
            raise AssertionError((degree, got, want))
    if polynomial_threshold(5, 3) != 1:
        raise AssertionError("Cp bits with C=5 and degree 3 should hold at p=1")


def principal_and_neumann():
    """A principal subrow keeps the gap. A singular control has gap 0."""
    full = [Fraction(1), Fraction(1, 5), Fraction(1, 5), Fraction(1, 5)]
    # Drop the last off-diagonal entry.
    sub_off = sum(full[1:3])
    full_off = sum(full[1:])
    if not gap_lower(sub_off) > gap_lower(full_off):
        raise AssertionError("principal deletion should widen the gap")
    # [[1,1],[1,1]] has off-sum 1 and determinant 0.
    if gap_lower(Fraction(1)) != 0:
        raise AssertionError("gap 0 control")
    if 1 * 1 - 1 * 1 != 0:
        raise AssertionError("singular control")


def pin_sources():
    fine = FINE.read_text(encoding="utf-8")
    gaussian = GAUSSIAN.read_text(encoding="utf-8")
    loga = LOGA.read_text(encoding="utf-8")
    coverage = COVERAGE.read_text(encoding="utf-8")
    column = COLUMN.read_text(encoding="utf-8")
    if HALF_SENTENCE not in fine:
        raise SystemExit("FINE-PRIME half-gap sentence not found")
    if "1/(16p^2)" in HALF_SENTENCE:
        raise SystemExit("the one sentence must stay unquantified")
    if GAUSSIAN_CLAIM not in gaussian:
        raise SystemExit("GAUSSIAN.md conclusion not found")
    if "`5exp(-2a)<=5/(16p)^8<1/(8p)`." not in loga:
        raise SystemExit("LOG-A natural-log comparison not found")
    if "alias removal, band truncation and rounding keep half the gap" not in coverage:
        raise SystemExit("coverage-map obligation not found")
    if "A row-sum bound does not replace this argument." not in column:
        raise SystemExit("column package does not record the row separation")


def main():
    pin_sources()
    ideal_certificate()
    for p in range(1, 201):
        operations_preserve(p)
    per_entry_budget()
    polynomial_thresholds()
    principal_and_neumann()
    print("PASS_NARROW_ROW_HALF_GAP")


if __name__ == "__main__":
    main()

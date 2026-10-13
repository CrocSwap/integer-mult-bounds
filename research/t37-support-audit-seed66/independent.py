#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Contributor: Eva Ayala, with substantial OpenAI Codex assistance.
"""Independent fixed-point enclosure of the T37 supporting inequality.

Only Python's standard library is used.  No repository verifier or moment
engine is imported.  The input literals are the fixed-family data stated in
research/complex-t37-owners/ALL-T-PROOF.md, not a claim of physical feasibility.

For 0 < z <= 1/500, write a = log(48/r), b = log(48).  The elementary bounds
exp(z*a)-1 >= z*a and exp(z*b)-1 <= z*b*exp(z*b) reduce the positive-credit
comparison to r*a > (v/925)*b*exp(b/500).  Every enclosure below is rational.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from math import gcd


WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
HELPERS_PER_CALL = (80, 32, 54, 122, 216)
CALLS = 9
BINS = ((8, 672, 2), (16, 448, 4), (32, 448, 8), (48, 448, -13))
SCALE = 10**40
LOG_TERMS = 1024
EXP_SQUARINGS = 20


def require(condition: bool, message: str) -> None:
    """Keep all failure detection active under python -O."""
    if not condition:
        raise ValueError(message)


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def log_interval(value: Fraction) -> tuple[Fraction, Fraction]:
    """Bound log(value) using a direct, downward-rounded atanh recurrence.

    If q=(value-1)/(value+1), log(value)=2*sum q^(2j+1)/(2j+1).
    The integer recurrence p <- floor(p*q^2), initially floor(SCALE*q),
    undershoots each scaled exact power by less than E=1/(1-q^2).
    Each rounded summand loses at most E/(2j+1)+1 <= E+1.
    The uncomputed tail is at most
    2*q^(2N+1)/((2N+1)*(1-q^2)).  The terminal integer power plus E bounds
    its numerator, so the entire computation uses short integers/rationals.
    """
    require(value >= 1, "log enclosure requires value >= 1")
    if value == 1:
        return Fraction(0), Fraction(0)
    q = (value - 1) / (value + 1)
    q2 = q * q
    error = 1 / (1 - q2)
    power = (SCALE * q.numerator) // q.denominator
    total = 0
    for index in range(LOG_TERMS):
        total += power // (2 * index + 1)
        power = (power * q2.numerator) // q2.denominator
    lower = Fraction(2 * total, SCALE)
    rounding = Fraction(2 * LOG_TERMS, SCALE) * (error + 1)
    tail = (Fraction(2, SCALE) * (power + error)
            / ((2 * LOG_TERMS + 1) * (1 - q2)))
    return lower, lower + rounding + tail


def exp_upper(value: Fraction) -> Fraction:
    """Bound exp(value) by a geometric bound and outward-rounded squaring.

    exp(t) <= 1/(1-t) for 0<=t<1, since 1/k!<=1 termwise in the convergent
    positive series.  Apply this to t=value/2^20 and square twenty times.
    All upper endpoints are rounded upward to the fixed-point grid.
    """
    require(value >= 0, "exponential enclosure requires value >= 0")
    small = value / (1 << EXP_SQUARINGS)
    require(small < 1, "geometric exponential bound outside domain")
    bound = ceil_fraction(Fraction(SCALE) / (1 - small))
    for _ in range(EXP_SQUARINGS):
        bound = (bound * bound + SCALE - 1) // SCALE
    return Fraction(bound, SCALE)


def residual_scores() -> dict[int, int]:
    """Unbounded exact-fill DP; supplier multiplicities are relaxed here."""
    fill: list[int | None] = [None] * 49
    fill[0] = 0
    for total in range(1, 49):
        candidates = [fill[total - width] + price
                      for width, price in zip(WIDTHS, PRICES)
                      if total >= width and fill[total - width] is not None]
        if candidates:
            fill[total] = max(candidates)
    scores: dict[int, int] = {}
    for capacity, _, bonus in BINS:
        for used in range(capacity + 1):
            if fill[used] is None:
                continue
            rank = capacity - used
            score = bonus + fill[used]
            if rank not in scores or score > scores[rank]:
                scores[rank] = score
    return scores


def audit() -> dict:
    log2_lower, log2_upper = log_interval(Fraction(2))
    require(Fraction(2, 3) < log2_lower <= log2_upper < 1,
            "known log2 enclosure failed")
    dyadic_exp = exp_upper(Fraction(1, 128))
    require(Fraction(129, 128) < dyadic_exp < Fraction(128, 127),
            "known dyadic exponential enclosure failed")
    scores = residual_scores()
    require(len(scores) == 45, "attainable residual-rank count changed")
    require(scores[0] == 0 and scores[1] == 19 and scores[48] == -13,
            "distinguished signed scores changed")
    stock_mass = sum(capacity * count for capacity, count, _ in BINS)
    helper_mass = CALLS * sum(width * count for width, count
                             in zip(WIDTHS, HELPERS_PER_CALL))
    mass = stock_mass - helper_mass
    signed = (sum(count * bonus for _, count, bonus in BINS)
              + CALLS * sum(count * price for count, price
                            in zip(HELPERS_PER_CALL, PRICES)))
    credit = 48 * signed + 13 * mass
    require((mass, signed, credit) == (14382, -3892, 150),
            "fixed-family inventory equations changed")
    log48_lower, log48_upper = log_interval(Fraction(48))
    require(0 < log48_lower <= log48_upper < 4,
            "log48 enclosure outside its expected rigorous range")
    exponential_upper = exp_upper(log48_upper / 500)
    positive_product_upper = log48_upper * exponential_upper
    table = []
    margins: dict[int, Fraction] = {}
    for rank, score in sorted(scores.items()):
        value = 48 * score + 13 * rank
        row = {"rank": rank, "u": score, "v": value}
        if 0 < rank < 48 and rank != 1:
            log_lower, log_upper = log_interval(Fraction(48, rank))
            require(log_lower > 0, f"positive log failed at rank {rank}")
            if value > 0:
                margin = (rank * log_lower
                          - Fraction(value, 925) * positive_product_upper)
            else:
                # The negative multiplier reverses the enclosure direction.
                # The actual integral term (exp(z*b)-1)/z is at least b,
                # hence at least log48_lower, for every positive z.
                margin = (rank * log_lower
                          - Fraction(value, 925) * log48_lower)
            require(margin > 3,
                    f"uniform supporting comparison failed at rank {rank}")
            margins[rank] = margin
            row.update({"log_ratio_lower": fraction_text(log_lower),
                        "log_ratio_upper": fraction_text(log_upper),
                        "uniform_margin_lower": fraction_text(margin)})
        table.append(row)
    require(len(margins) == 42, "strict-rank coverage changed")
    require(48 * scores[1] + 13 == 925, "rank-one credit changed")
    normalized_one = Fraction(credit, 925)
    normalized_48 = (Fraction(mass) - normalized_one) / 48
    require(normalized_one == Fraction(6, 37)
            and normalized_48 == Fraction(11086, 37),
            "normalized equality profile changed")
    require(gcd(normalized_one.numerator, normalized_one.denominator) == 1
            and normalized_one.denominator == 37,
            "equality replica divisibility changed")
    require(6 + 48 * 11086 == mass * 37
            and 19 * 6 - 13 * 11086 == signed * 37,
            "integral equality representative failed inventory equations")
    minimum_rank = min(margins, key=margins.get)
    return {
        "status": "PASS",
        "method": "direct fixed-point atanh and geometric repeated squaring",
        "parameters": {"scale": SCALE, "log_terms": LOG_TERMS,
                       "exp_squarings": EXP_SQUARINGS},
        "z_domain": "0 < z <= 1/500",
        "attainable_ranks": len(scores), "strict_ranks_checked": len(margins),
        "rank_mass": mass, "signed_price": signed, "required_credit": credit,
        "log48_lower": fraction_text(log48_lower),
        "log48_upper": fraction_text(log48_upper),
        "exp_log48_over500_upper": fraction_text(exponential_upper),
        "minimum_margin_rank": minimum_rank,
        "minimum_uniform_margin_lower": fraction_text(margins[minimum_rank]),
        "normalized_equality_profile": {
            "1": fraction_text(normalized_one),
            "48": fraction_text(normalized_48)},
        "equality_replica_divisor": 37,
        "equality_replica_divisor_scope": "Positive integer T and integer "
            "residual counts. Relaxed real counts permit every T > 0.",
        "table": table,
        "scope": "Necessary fixed-family relaxation; no physical realization, "
                 "root enclosure, outer transfer, or new kappa claim.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print exact receipt")
    args = parser.parse_args()
    result = audit()
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("PASS: 45 attainable ranks; 42 strict uniform comparisons; "
              "all normalized margins > 3; integer-count equality requires "
              "37 | T.")


if __name__ == "__main__":
    main()

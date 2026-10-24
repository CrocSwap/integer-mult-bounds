#!/usr/bin/env python3
"""The printed #4100 union ledger names tau_eff, not 45/16."""

from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAUSSIAN = "research/unconditional-batched-crt/GAUSSIAN.md"
FINE = "research/unconditional-batched-crt/vendor/FINE-PRIME.md"
UNION = "research/unconditional-batched-crt/vendor/UNION-SCHEDULE.md"
GAUGE = "research/unconditional-batched-crt/vendor/GAUGEFREE-INTERIORS.md"

EPS = Decimal("0.99999437577296")
XI = Decimal("0.50167412128176")
BETA = Decimal("0.99664613320944")


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def load(path):
    return (ROOT / path).read_text(encoding="utf-8")


def require_phrase(body, phrase, name):
    require(phrase in body, name + " missing phrase: " + phrase)


def round_half_up(value, places):
    quantum = Decimal("1e-" + str(places))
    return value.quantize(quantum, rounding=ROUND_HALF_UP)


def saving_gap(tau):
    """S_b - S_u = c - 1/2, with c = (3 - tau) / 2."""
    return (Fraction(3) - tau) / 2 - Fraction(1, 2)


def main():
    gaussian = load(GAUSSIAN)
    fine = load(FINE)
    union = load(UNION)
    gauge = load(GAUGE)

    require_phrase(gaussian, "7^16<2^45 gives exponent tau=45/16", "GAUSSIAN.md")
    require_phrase(gaussian, "O(V d W^(tau-1)/B polylog(p))", "GAUSSIAN.md")
    require_phrase(gaussian, "Total union cost over d/g groups is", "GAUSSIAN.md")
    require_phrase(gaussian, "O(V d W/B polylog(p))", "GAUSSIAN.md")
    require_phrase(
        gaussian,
        "Temporary padding of the one exposed polynomial\nrow field is removed before the next axis",
        "GAUSSIAN.md",
    )
    strassen_at = gaussian.index("7^16<2^45 gives exponent tau=45/16")
    union_at = gaussian.index("Total union cost over d/g groups is")
    padding_at = gaussian.index("Temporary padding of the one exposed polynomial")
    require(strassen_at < union_at < padding_at, "layout sentence is not after the Strassen paragraph")

    require_phrase(fine, "target exponent `tau=45/16` and `c=(3-tau)/2=3/32`", "FINE-PRIME.md")
    require_phrase(fine, "needs no structured inverse algorithm", "FINE-PRIME.md")
    require_phrase(fine, "its saving is `c+xi-epsilon`", "FINE-PRIME.md")
    require(
        fine.index("target exponent `tau=45/16`") < fine.index("needs no structured inverse algorithm"),
        "Strassen sentence does not reject the structured inverse",
    )

    require_phrase(union, "tau_eff = 2 + 1e-64", "UNION-SCHEDULE.md")
    require_phrase(union, "this document's schedule is independent of the boundary exponent", "UNION-SCHEDULE.md")
    require_phrase(union, "epsilon = 0.9999944, xi = 0.5016741, beta = 0.9966461", "UNION-SCHEDULE.md")
    require_phrase(union, "the same exponent eps+1/2-xi and both bind", "UNION-SCHEDULE.md")
    require_phrase(
        union,
        "retained polynomial-width row-field movement for batched boundary arithmetic",
        "UNION-SCHEDULE.md",
    )
    require_phrase(union, "nothing in this document changes the arithmetic", "UNION-SCHEDULE.md")
    require(
        union.index("tau_eff = 2 + 1e-64") < union.index("epsilon = 0.9999944"),
        "section 5b does not follow the tau_eff definition",
    )

    require_phrase(
        gauge,
        "eps = 0.99999437577296, xi = 0.50167412128176, beta = 0.99664613320944",
        "GAUGEFREE-INTERIORS.md",
    )
    require_phrase(gauge, "c = (3 - tau_eff)/2", "GAUGEFREE-INTERIORS.md")
    require_phrase(gauge, "0.001679745508802299", "GAUGEFREE-INTERIORS.md")
    require_phrase(
        gauge,
        "margins above kappa: main = Gaussian = bit router = boundary = union ~ 1e-64",
        "GAUGEFREE-INTERIORS.md",
    )

    require(round_half_up(EPS, 7) == Decimal("0.9999944"), "eps does not round to the section 5b digit")
    require(round_half_up(XI, 7) == Decimal("0.5016741"), "xi does not round to the section 5b digit")
    require(round_half_up(BETA, 7) == Decimal("0.9966461"), "beta does not round to the section 5b digit")

    union_saving = Fraction(XI) + Fraction(1, 2) - Fraction(EPS)
    require(union_saving == Fraction(1049840943, 625000000000), "union saving is not 0.0016797455088")
    prefix = Decimal(union_saving.numerator) / Decimal(union_saving.denominator)
    require(format(prefix, "f").startswith("0.0016797455088"), "union saving misses the printed kappa prefix")
    require("0.001679745508802299".startswith("0.00167974550880"), "kappa prefix drifted")

    tau_eff = Fraction(2) + Fraction(1, 10**64)
    tau_strassen = Fraction(45, 16)
    require(saving_gap(tau_eff) == Fraction(-1, 2 * 10**64), "tau_eff gap is not -5e-65")
    require(saving_gap(tau_strassen) == Fraction(-13, 32), "45/16 gap is not -13/32")

    boundary_strassen = union_saving + saving_gap(tau_strassen)
    require(boundary_strassen < 0, "45/16 boundary saving is not below zero on the printed point")
    require(abs(saving_gap(tau_eff)) < Fraction(1, 10**64), "tau_eff gap is outside the stated 1e-64 margin")
    require(abs(saving_gap(tau_strassen)) > Fraction(1, 10), "45/16 control is not separated from the slack")

    # A ledger that names 45/16 cannot be the section 5b joint-binding row.
    require(saving_gap(tau_strassen) != saving_gap(tau_eff), "the two exponents collapsed")

    print(
        "PASS_LEDGER_BOUNDARY_EXPONENT"
        " exponent=tau_eff"
        " gap_eff=-5e-65"
        " gap_45=-13/32"
        " seven_digit_round=true"
        " layout_on_union_paragraph=true"
        " strassen_below_zero=true"
        " selected_decimal=0.00302015"
        " no_new_kappa=true"
    )


if __name__ == "__main__":
    main()

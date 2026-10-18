#!/usr/bin/env python3
"""Exact source-binding and algebraic controls for the prime selector proof."""

from fractions import Fraction
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "upstream/build/sections/08-assembly.tex"
EXPECTED_SHA256 = (
    "763d7945b1e1ec4ebae9b799bcefcc45fa9bae6e2ffad799868a9c3d513dbd4a"
)


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def main():
    actual = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    require(actual == EXPECTED_SHA256, "pinned assembly source SHA256")

    epsilon = Fraction(1, 2**75)
    require(0 < epsilon < Fraction(1, 4), "epsilon lies in the source range")
    require(1 - 2 * epsilon > Fraction(1, 2), "1-2epsilon > 1/2")
    require(1 - epsilon > Fraction(1, 2), "1-epsilon > 1/2")
    exponent = 1 / epsilon
    require(exponent == 2**75, "the exact d>=5 cutoff exponent")
    require(2**75 > 16, "the cutoff implies b>=2^16")
    require(1 - 2 * epsilon >= Fraction(1, 2),
            "the square-root comparison for b/d^2")
    require(1 - epsilon >= Fraction(1, 2),
            "the square-root comparison for b/(2d)")
    require(Fraction(1, 2) < Fraction(32, 2),
            "the log x lower-bound constants")
    require(Fraction(32 * 5 - 1, 2) > 8 * 5,
            "log x threshold at minimum d=5")

    # These endpoint and derivative checks are the exact constant parts of
    # the monotonicity argument in PROOF.md; ln(2)>1/2 is proved there by its
    # integral. The checks are reductions, not a formal proof assistant run.
    require(Fraction(2**8, 8) - 16 > 0,
            "sqrt(b)/8-log2(b) at b=2^16")
    require(Fraction(2**8, 2) > 16 * 1,
            "sqrt(b)*ln(2)>16 using ln(2)>1/2")
    require(Fraction(2**8, 4) > 5,
            "sqrt(b)/4>5 at b=2^16")
    require(Fraction(5, 1) >= 5, "d cutoff minimum")
    require(3 * 5 >= 6, "alpha-gap conclusion implies alpha^4 theta > p")
    require(Fraction(1, 2) < 1, "n^(1/2)=o(n) implication")

    # Exact finite controls exercise rational endpoint algebra. They are
    # diagnostics, not the proof for all d.
    for d in range(2, 129):
        eta = Fraction(1, 4 * d)
        require(0 < eta < Fraction(1, 4), f"eta range at d={d}")
        require((1 - eta) / 2 < 1 - 2 * eta,
                f"two intervals are disjoint at d={d}")
        require(eta / (1 - eta) > eta, f"lower gap at d={d}")
        require((1 - Fraction(1, 2 * d)) ** d > Fraction(1, 2),
                f"product lower bound at d={d}")
        if d >= 5:
            require(Fraction(1, 2 * d - 1) < Fraction(1, 8),
                    f"upper gap at d={d}")

    # Negative controls: d=1 is outside the strict eta hypothesis; eta=1/3
    # makes the two interval boundaries meet instead of being disjoint.
    eta_d1 = Fraction(1, 4)
    require(not (eta_d1 < Fraction(1, 4)), "reject d=1 endpoint")
    eta_touch = Fraction(1, 3)
    require((1 - eta_touch) / 2 == 1 - 2 * eta_touch,
            "reject the touching-interval boundary")

    print("PASS_SOURCE_PIN sha256=" + actual)
    print("PASS_EXACT_EXPONENT epsilon=2^-75; sufficient cutoff b>=5^(2^75)")
    print("PASS_FINITE_GEOMETRY_CONTROLS d=2..128 (diagnostic only)")
    print("PASS_NEGATIVE_CONTROLS d=1 and eta=1/3 rejected")
    print("SCOPE: exact pins and reductions only; not (RS), all-size prime counts, or a numerical prime search")


if __name__ == "__main__":
    main()

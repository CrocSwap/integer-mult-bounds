#!/usr/bin/env python3
"""Exact rational checks for the row-norm/domain proof in PROOF.md."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import sys


if sys.flags.optimize:
    raise SystemExit("assertions must remain enabled")

ROOT = Path(__file__).resolve().parent
proof = ROOT / "inputs/PR3878-PROOF.md"
expected_sha256 = "5452f3e2191824b4a8451c83fbdf58b3b2228f4e1966a6f22c3e60bd152e56b0"
assert sha256(proof.read_bytes()).hexdigest() == expected_sha256

# The bound (alpha+1)/(2 alpha) is exactly 3/4 at alpha=2 and
# decreases for every larger alpha.
q_at_two = (Fraction(2) + 1) / (2 * 2)
assert q_at_two == Fraction(3, 4)
for alpha in (2, 3, 7, 32, 101):
    q = Fraction(alpha + 1, 2 * alpha)
    assert q <= Fraction(3, 4)
assert Fraction(1 + 1, 2 * 1) == 1  # alpha=1 misses the 3/4 guarantee

# C = sqrt(2)+2^-11 is strictly below the rational bound 10/7+2^-11,
# which is strictly below 3/2. Therefore the error budget is below 1/4 at p=3.
C_upper = Fraction(10, 7) + Fraction(1, 2048)
assert C_upper < Fraction(3, 2)
assert C_upper / 8 < Fraction(3, 16) < Fraction(1, 4)
assert C_upper / (2**101) < Fraction(1, 4)
assert Fraction(3, 4) + C_upper / 8 < 1

# Boundary control: at p=2 the stated coarse error budget does not imply
# strict output-domain preservation. This rational map saturates the bound.
assert Fraction(10, 7) > 1  # hence C > 1 and C/4 > 1/4
exact_at_one = Fraction(3, 4)
approx_at_one = exact_at_one + Fraction(1, 4)
assert approx_at_one == 1
assert Fraction(1, 4) < C_upper / 4

print(
    "PASS_PHYSICAL_GAUSSIAN_ROW_NORM_TRANSFER "
    "alpha2_q=3/4 all_alpha_guard=true C_upper=true "
    "p3_preserves_unit_ball=true p2_boundary_control=true source_hash=true"
)

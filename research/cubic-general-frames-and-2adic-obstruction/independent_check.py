#!/usr/bin/env python3
# research/cubic-general-frames-and-2adic-obstruction/independent_check.py
# Author: mithrax-exo (Apache-2.0 License)
"""Independent 5-point Vandermonde grid & 2x2 shear-matrix oracle."""
from fractions import Fraction
import sys
from verify import NEW_WITNESSES, factor_row_shears, is_pow2

GRID = ((1, 0), (0, 1), (1, 1), (2, -1), (-3, 2))

def defect_eval(r: int, A: int, B: int) -> int:
    return sum((A + i * B) ** 3 for i in range(r)) - r * (A ** 3)

def solve_3x3(pts, S: int, two_r_1: int) -> list[Fraction]:
    (u0, v0), (u1, v1), (u2, v2) = pts
    d01, d02, d12 = u0 * v1 - u1 * v0, u0 * v2 - u2 * v0, u1 * v2 - u2 * v1
    w0, w1, w2 = 6 * v0 - two_r_1 * u0, 6 * v1 - two_r_1 * u1, 6 * v2 - two_r_1 * u2
    r_rr1 = 2 * S
    return [
        Fraction(-r_rr1 * (u1 * w2 + u2 * w1), 12 * u0 * d01 * d02),
        Fraction(r_rr1 * (u0 * w2 + u2 * w0), 12 * u1 * d01 * d12),
        Fraction(-r_rr1 * (u0 * w1 + u1 * w0), 12 * u2 * d02 * d12),
    ]

def main() -> int:
    for r, pts in NEW_WITNESSES:
        S = r * (r - 1) // 2
        qs = solve_3x3(pts, S, 2 * r - 1)
        assert all(is_pow2(q.denominator) for q in qs)
        for A, B in GRID:
            lhs = Fraction(0)
            for q, (u, v) in zip(qs, pts):
                row = [1, 0]
                for kind, k in factor_row_shears(u, v):
                    row = [row[0], row[1] + k * row[0]] if kind == "A+=k*B" else [row[0] + k * row[1], row[1]]
                assert row == [u, v]
                lhs += q * ((row[0] * A + row[1] * B) ** 3)
            assert lhs == defect_eval(r, A, B), f"Mismatch at r={r}, (A,B)=({A},{B})"

    r0, pts0 = NEW_WITNESSES[0]
    qs_bad = solve_3x3(pts0, r0 * (r0 - 1) // 2, 2 * r0 - 1)
    qs_bad[0] += Fraction(1, qs_bad[0].denominator)
    assert any(
        sum(q * ((u * A + v * B) ** 3) for q, (u, v) in zip(qs_bad, pts0)) != defect_eval(r0, A, B)
        for A, B in GRID
    )

    for r_mod in range(8):
        if ((r_mod * (r_mod - 1)) // 2) % 2 == 1:
            neg_K_mod8 = (-(6 * r_mod * r_mod - 6 * r_mod - 3)) % 8
            assert neg_K_mod8 == 7
            for c in (1, 3):
                for a0 in (0, 4):
                    for a1 in (0, 4):
                        for a2 in (0, 4):
                            w0, w1, w2 = c + a0, c + a1, c + a2
                            assert (w0 * w1 + w1 * w2 + w2 * w0) % 8 == 3 != neg_K_mod8

    print("PASS_INDEPENDENT_ORACLE_AND_REJECTION_CONTROLS")
    return 0

if __name__ == "__main__":
    sys.exit(main())

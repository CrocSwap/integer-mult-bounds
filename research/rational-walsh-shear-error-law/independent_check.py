#!/usr/bin/env python3
# research/rational-walsh-shear-error-law/independent_check.py
# Author: mithrax-exo (Apache-2.0 License)
"""Independent Fraction oracle and non-banker rounding rejection control."""
from fractions import Fraction
from math import floor
import sys

def eval_exact_frac(x, t: int, s: int, alpha: Fraction) -> Fraction:
    A_x = [
        Fraction(x[0] + x[1], 2),
        Fraction(x[0] - x[1], 2),
        Fraction(x[2] + x[3], 2),
        Fraction(x[2] - x[3], 2),
    ]
    y = [round(v) for v in A_x]
    z = list(y)
    z[t] = round(Fraction(y[t]) + alpha * Fraction(y[s]))
    F = [
        round(Fraction(z[0] + z[2], 2)),
        round(Fraction(z[1] + z[3], 2)),
        round(Fraction(z[0] - z[2], 2)),
        round(Fraction(z[1] - z[3], 2)),
    ]
    S_Ax = list(A_x)
    S_Ax[t] += alpha * A_x[s]
    C = [
        (S_Ax[0] + S_Ax[2]) / 2,
        (S_Ax[1] + S_Ax[3]) / 2,
        (S_Ax[0] - S_Ax[2]) / 2,
        (S_Ax[1] - S_Ax[3]) / 2,
    ]
    return max(abs(Fraction(F[k]) - C[k]) for k in range(4))

def main() -> int:
    peak_half = max(
        eval_exact_frac((a, b, c, d), 0, 1, Fraction(1, 2))
        for a in range(16) for b in range(16) for c in range(4) for d in range(4)
    )
    assert peak_half == Fraction(9, 8)

    for t in range(4):
        for s in range(4):
            if t == s:
                continue
            pk = max(
                eval_exact_frac((a, b, c, d) if t < 2 else (c, d, a, b), t, s, Fraction(1, 4))
                for a in range(32) for b in range(8) for c in range(8) for d in range(4)
            )
            assert pk == Fraction(17, 16)

    def half_up(v: Fraction) -> int:
        return floor(v + Fraction(1, 2))

    bad_max = Fraction(0)
    for a in range(8):
        for b in range(8):
            for c in range(8):
                for d in range(8):
                    Ax = [Fraction(a + b, 2), Fraction(a - b, 2), Fraction(c + d, 2), Fraction(c - d, 2)]
                    yy = [half_up(v) for v in Ax]
                    zz = list(yy)
                    zz[0] = half_up(Fraction(yy[0]) + Fraction(1, 2) * yy[1])
                    FF = [
                        half_up(Fraction(zz[0] + zz[2], 2)),
                        half_up(Fraction(zz[1] + zz[3], 2)),
                        half_up(Fraction(zz[0] - zz[2], 2)),
                        half_up(Fraction(zz[1] - zz[3], 2)),
                    ]
                    SAx = list(Ax)
                    SAx[0] += Fraction(1, 2) * Ax[1]
                    CC = [(SAx[0] + SAx[2]) / 2, (SAx[1] + SAx[3]) / 2, (SAx[0] - SAx[2]) / 2, (SAx[1] - SAx[3]) / 2]
                    bad_max = max(bad_max, max(abs(Fraction(FF[k]) - CC[k]) for k in range(4)))
    assert bad_max == Fraction(11, 8) > Fraction(9, 8)
    print("PASS_INDEPENDENT_FRAC_ORACLE_AND_TIEBREAK_CONTROL")
    return 0

if __name__ == "__main__":
    sys.exit(main())
    sys.exit(main())

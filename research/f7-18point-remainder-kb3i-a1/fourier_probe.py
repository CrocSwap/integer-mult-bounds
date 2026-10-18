"""Fourier / identity numbers for the both-odd surviving splits (11,7)/(9,9)
of the 18-point question (route KB3i-b), read from the byte-vendored PR 2961
engine cover18.py.  No new arithmetic; this prints the recorded identity
conditions so the even-half / rho-square frontier is explicit."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
sys.stdout.reconfigure(encoding="utf-8")

import cover18 as c18  # noqa: E402


def show(s, t):
    n = 7
    print("=== split (%d,%d)  n=7 (E=F2^6, |A|+|B|=%d) ===" % (s, t, s + t))
    eo = s * t - (1 << (n - 1))
    print("  odd_excess E_o = s*t - 2^(n-1) = %d" % eo)
    print("  even_half_max (self-sum bound) = %d" % c18.even_half_max(n, s, t))
    # rho square attainable values and the min
    if eo <= 24:
        vals = c18.rho_square_values(eo)
        print("  attainable sum rho^2 (partition square sums of E_o=%d): %s" % (eo, vals))
        print("  min sum rho^2 = %d, max = %d" % (vals[0], vals[-1]))
    else:
        print("  E_o=%d out of rho budget (>24): not attempted" % eo)
    if "--full" in sys.argv:
        for nzb in (False, True):
            rec = c18.fourier_profile_feasibility(n, s, t, nonzero_both=nzb)
            print("  fourier_profile_feasibility(nonzero_both=%s): feasible=%s"
                  % (nzb, rec["feasible"]))
            print("    reason: %s" % rec["reason"])
            print("    feasible_S (rho square sums): %s" % rec.get("feasible_S"))
    # squeeze numbers
    sq = c18.squeeze_numbers(n, s, t)
    print("  squeeze_numbers: opposite_parity=%s contradiction=%s reason=%s"
          % (sq["opposite_parity"], sq["contradiction"], sq["reason"]))
    for side in sq["sides"]:
        print("    side %s card=%d parseval_remainder=%s max_char=%s max_allowed=%s deficit=%s"
              % (side["side"], side["cardinality"], side["parseval_remainder"],
                 side["max_char"], side["max_allowed"], side["deficit"]))


if __name__ == "__main__":
    show(11, 7)
    show(9, 9)
    # controls: the decided/deciding classes for reference
    print()
    show(12, 6)
    show(10, 8)

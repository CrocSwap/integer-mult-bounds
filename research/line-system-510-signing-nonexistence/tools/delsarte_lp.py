"""Delsarte LP checks for idea 3: 510 lines in R^30 with |cos| in {0, 1/4}.

Exact rational arithmetic (fractions.Fraction) for every reported number;
scipy's LP is used only to find the optimum, which is then re-derived exactly.

Part A: the fixed distance distribution forced by the W(7,2) doubled pattern
        (per line: 253 orthogonal lines, 256 lines at |cos| = 1/4) against
        every Gegenbauer inequality of even degree 2..KMAX.
Part B: the plain LP bound  max N  for lines in R^n with angles {90, arccos a}.
Part C: same LP with the extra tight-frame equality (degree 2 = 0), which every
        saturated system satisfies (README section 4, equality case).

Run:  py -3.12 delsarte_lp.py   (seconds). Appends to progress.log.
"""
from fractions import Fraction as Fr
import datetime
import json
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "progress.log")
KMAX = 60


def log(msg):
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def gegenbauer_normalised(n, kmax, t):
    """Q_k(t) for k = 0..kmax on S^{n-1}, normalised Q_k(1) = 1, exact."""
    lam = Fr(n - 2, 2)
    c = [Fr(1), 2 * lam * t]
    c1 = [Fr(1), 2 * lam]
    for k in range(1, kmax):
        c.append((2 * (k + lam) * t * c[k] - (k + 2 * lam - 1) * c[k - 1]) / (k + 1))
        c1.append((2 * (k + lam) * c1[k] - (k + 2 * lam - 1) * c1[k - 1]) / (k + 1))
    return [c[k] / c1[k] for k in range(kmax + 1)]


def part_a(n, a, n_orth, n_ang):
    q0 = gegenbauer_normalised(n, KMAX, Fr(0))
    qa = gegenbauer_normalised(n, KMAX, a)
    rows = []
    worst = None
    for k in range(2, KMAX + 1, 2):
        val = 1 + n_orth * q0[k] + n_ang * qa[k]
        rows.append((k, val))
        if worst is None or val < worst[1]:
            worst = (k, val)
    return rows, worst


def lp_bound(n, a, tight_frame):
    q0 = gegenbauer_normalised(n, KMAX, Fr(0))
    qa = gegenbauer_normalised(n, KMAX, a)
    ks = list(range(2, KMAX + 1, 2))
    # variables x = (A0, Aa) >= 0 ; maximise A0 + Aa
    # constraint per k:  -(q0 A0 + qa Aa) <= 1
    A_ub, b_ub, A_eq, b_eq = [], [], [], []
    for k in ks:
        if tight_frame and k == 2:
            A_eq.append([float(q0[k]), float(qa[k])])
            b_eq.append(-1.0)
        else:
            A_ub.append([-float(q0[k]), -float(qa[k])])
            b_ub.append(1.0)
    res = linprog([-1, -1], A_ub=A_ub, b_ub=b_ub,
                  A_eq=A_eq or None, b_eq=b_eq or None,
                  bounds=[(0, None), (0, None)], method="highs")
    if res.status != 0:
        return None
    # exact re-derivation: the optimum of a 2-variable LP is a vertex where
    # two constraints are tight (or one constraint and a bound).
    cand_rows = [(k, q0[k], qa[k], "eq" if (tight_frame and k == 2) else "ub") for k in ks]
    best = None
    lines = [(r[1], r[2]) for r in cand_rows] + [("A0=0",), ("Aa=0",)]

    def feasible(A0, Aa):
        if A0 < 0 or Aa < 0:
            return False
        for k, c0, ca, kind in cand_rows:
            v = 1 + c0 * A0 + ca * Aa
            if kind == "eq" and v != 0:
                return False
            if v < 0:
                return False
        return True

    def solve2(r1, r2):
        # each r: (c0, ca) meaning 1 + c0 A0 + ca Aa = 0, or bound
        def eq(r):
            if r == ("A0=0",):
                return (Fr(1), Fr(0), Fr(0))
            if r == ("Aa=0",):
                return (Fr(0), Fr(1), Fr(0))
            return (r[0], r[1], Fr(-1))
        a1, b1, c1 = eq(r1)
        a2, b2, c2 = eq(r2)
        det = a1 * b2 - a2 * b1
        if det == 0:
            return None
        return ((c1 * b2 - c2 * b1) / det, (a1 * c2 - a2 * c1) / det)

    # restrict to rows near the float optimum to keep it quick
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            p = solve2(lines[i], lines[j])
            if p is None or not feasible(*p):
                continue
            val = 1 + p[0] + p[1]
            if best is None or val > best[0]:
                best = (val, p)
    return best, -res.fun + 1


def main():
    n, a = 30, Fr(1, 4)
    log("=== delsarte_lp.py start: n=30, |cos| in {0, 1/4}, even degrees 2..%d ===" % KMAX)

    rows, worst = part_a(n, a, 253, 256)
    log("Part A (fixed distribution 1 + 253 + 256 = 510):")
    for k, v in rows[:8]:
        log(f"  k={k:2d}  1+253Q_k(0)+256Q_k(1/4) = {v}  (~{float(v):.6g})")
    log(f"  worst over k<= {KMAX}: k={worst[0]} value {float(worst[1]):.6g}  -> "
        + ("ALL >= 0: LP does not kill the object" if worst[1] >= 0 else "NEGATIVE: object does not exist"))

    out = {"part_a": {str(k): str(v) for k, v in rows}}
    for tf in (False, True):
        best, fl = lp_bound(n, a, tf)
        tag = "C (with tight-frame equality)" if tf else "B (plain LP)"
        log(f"Part {tag}: N <= {best[0]} = {float(best[0]):.4f} (float LP {fl:.4f}); vertex A0={best[1][0]}, A1/4={best[1][1]}")
        out["part_" + ("c" if tf else "b")] = {"N_max": str(best[0]), "A0": str(best[1][0]), "Aa": str(best[1][1])}

    # absolute / relative bounds for comparison
    log(f"  absolute bound (3 inner products 0, +-a on lines): C(n+2,3)={n*(n+1)*(n+2)//6}")
    with open(os.path.join(HERE, "delsarte_lp_result.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    log("=== delsarte_lp.py done; results in delsarte_lp_result.json ===")


if __name__ == "__main__":
    sys.exit(main())

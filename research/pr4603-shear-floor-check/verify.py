#!/usr/bin/env python3
"""Independent check of three statements in PR #4603 (Matarener, head caab2b42): p16 query-only shears.

#4603 argues that the 15 query-only shears of the p16 controllers cannot be removed by lazy central frames or cheap
gather words. Independently of its code (nothing imported), this verifier checks:
  1. the exact identity S_x(-Q) S_y(Q^-1) = signed_swap * diag(Q^-1, Q) * S_x(Q), with S_x(a) = [[1,a],[0,1]],
     S_y(b) = [[1,0],[b,1]], signed_swap = [[0,-1],[1,0]], over Laurent monomials in Q (exact symbolic arithmetic
     on {exponent: coefficient} polynomials);
  2. the premise of its window bound on main's pinned complex controller: each of the 15 QUERY_SHEAR events on pair j
     is preceded, since the last LOCAL event on pair j, only by ADD and IDLE events (no SIGNED_SWAP or other LOCAL);
     the 15 windows [that LOCAL, the shear] are pairwise disjoint; so any scheme paying >= 1 per window pays >= 15,
     which the controller attains with exactly 15 shears;
  3. merging the 112 rank-one shear jobs of one query into 14 rank-eight jobs saves under one unit of paid moment at
     the current root t = 1 - 0.0030202 (112 - 14 * 8^t < 1), as stated.
The fusion-rank statement (part 1 of #4603) and the distinct-query-line census are not re-checked.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from decimal import Decimal as D, getcontext
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
getcontext().prec = 40


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def padd(a, b):
    out = Counter(a)
    for k, v in b.items():
        out[k] += v
    return {k: v for k, v in out.items() if v}


def pmul(a, b):
    out = Counter()
    for i, x in a.items():
        for j, y in b.items():
            out[i + j] += x * y
    return {k: v for k, v in out.items() if v}


def mmul(x, y):
    return [[padd(pmul(x[i][0], y[0][j]), pmul(x[i][1], y[1][j])) for j in range(2)] for i in range(2)]


ONE, ZERO = {0: 1}, {}


def mono(e, c=1):
    return {e: c}


def identity_check():
    sx = lambda a: [[ONE, a], [ZERO, ONE]]
    sy = lambda b: [[ONE, ZERO], [b, ONE]]
    lhs = mmul(sx(mono(1, -1)), sy(mono(-1)))
    swap = [[ZERO, mono(0, -1)], [ONE, ZERO]]
    diag = [[mono(-1), ZERO], [ZERO, mono(1)]]
    rhs = mmul(mmul(swap, diag), sx(mono(1)))
    need(lhs == rhs, "S_x(-Q) S_y(Q^-1) = signed_swap diag(Q^-1,Q) S_x(Q)")
    need(lhs == [[ZERO, mono(1, -1)], [mono(-1), ONE]], "explicit product")
    need(mmul(sx(mono(1)), sy(mono(-1))) != rhs, "control: wrong sign is detected")


def window_check():
    row = json.loads((ROOT / "research/joint-helper-lattice/CONTROLLER.json").read_text(encoding="utf-8"))
    events = row["physical_events"]
    windows = []
    for i, e in enumerate(events):
        if e[0] != "QUERY_SHEAR":
            continue
        pair = e[2]
        k = i - 1
        while not (events[k][0] == "LOCAL" and events[k][2] == pair):
            need(events[k][0] in ("ADD", "IDLE"), "only ADD/IDLE between the pair's full call and its shear")
            k -= 1
        windows.append((k, i))
    need(len(windows) == 15, "15 query-only shears")
    need(all(a[1] < b[0] for a, b in zip(windows, windows[1:])), "windows pairwise disjoint")
    # control: inserting a SIGNED_SWAP into the first window breaks the premise
    k, i = windows[0]
    broken = events[:k + 1] + [["SIGNED_SWAP", 0, 1]] + events[k + 1:]
    j = i
    ok = True
    while not (broken[j][0] == "LOCAL" and broken[j][2] == broken[i + 1][2]):
        ok &= broken[j][0] in ("ADD", "IDLE", "QUERY_SHEAR")
        j -= 1
    need(not ok, "control: an inserted SIGNED_SWAP is detected")
    return windows


def merge_check():
    t = 1 - D("0.0030202")
    saving = 112 - 14 * (D(8).ln() * t).exp()
    need(0 < saving < 1, "112 rank-one -> 14 rank-eight saves under one unit")
    return saving


def main():
    identity_check()
    windows = window_check()
    saving = merge_check()
    print(json.dumps({"status": "PASS_PR4603_PARTIAL_CHECK", "identity": True, "windows": windows,
                      "window_lower_bound": 15, "controller_shears": 15, "merge_saving": str(saving)[:10],
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())

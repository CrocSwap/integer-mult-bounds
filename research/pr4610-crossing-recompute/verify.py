#!/usr/bin/env python3
"""Independent 50-digit recomputation of PR #4610's raw crossing (intqwq, head 4b4c75bc).

#4610 claims that its changed paid list Pnew = 2201 H1 + 412 H2 + 506 H3 + 135 H4 + 36 H5 + 8 H8 (helpers unchanged:
28 H4 + 7 H7 + 47 H8 + 326 H9), inserted into the retained p16 controller, moves the raw crossing of the complete
target and paid moments into (0.0030215551, 0.0030215552), and selects kappa = 0.00302152.
This verifier rebuilds both histograms from main's pinned research/joint-helper-lattice/CONTROLLER.json:
    LOCAL event: targets += helpers, paid += local list;  QUERY_SHEAR: paid[1] += 112;
    IDLE with s retained stages: paid[8 s] += 224;  each diagonal term: targets[1 + 8 * sum(term[1:])] += 112,
and solves sum_T n r^(1-c) = sum_P n r^(1-c) by bisection in 50-digit Decimal arithmetic (a different engine from
#4610's Fraction intervals; nothing imported from #4610). The old list Pold must reproduce PR4535's root
0.0030201659770... as a control; paid-call counts and the rank-mass surplus are also checked.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from decimal import Decimal as D, getcontext
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
CONTROLLER = ROOT / "research/joint-helper-lattice/CONTROLLER.json"
HELPERS = {4: 28, 7: 7, 8: 47, 9: 326}
P_NEW = {1: 2201, 2: 412, 3: 506, 4: 135, 5: 36, 8: 8}
P_OLD = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}
getcontext().prec = 50


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def histograms(row, local, idle=True):
    targets, paid = Counter(), Counter()
    kinds = Counter(e[0] for e in row["physical_events"])
    need(kinds["LOCAL"] == 18 and kinds["QUERY_SHEAR"] == 15 and kinds["IDLE"] == 15, "18 calls, 15 shears, 15 idles")
    for e in row["physical_events"]:
        if e[0] == "LOCAL":
            targets.update(HELPERS)
            paid.update(local)
        elif e[0] == "QUERY_SHEAR":
            paid[1] += 112
        elif e[0] == "IDLE" and idle:
            paid[8 * len(e[2])] += 224
    for term in row["diagonal"]:
        targets[1 + 8 * sum(term[1:])] += 112
    return targets, paid


def margin(targets, paid, c):
    s = 1 - c
    moment = lambda h: sum(D(n) * (D(r).ln() * s).exp() for r, n in h.items())
    return moment(targets) - moment(paid)


def root(targets, paid, lo=D("0.0025"), hi=D("0.0035")):
    need(margin(targets, paid, lo) > 0 > margin(targets, paid, hi), "sign change bracket")
    for _ in range(70):
        mid = (lo + hi) / 2
        if margin(targets, paid, mid) > 0:
            lo = mid
        else:
            hi = mid
    return lo, hi


def main():
    row = json.loads(CONTROLLER.read_text(encoding="utf-8"))
    need((row["kind"], row["pairs"], row["prefix_pairs"]) == ("complex", 16, 7), "p16 complex controller")
    tn, pn = histograms(row, P_NEW)
    to, po = histograms(row, P_OLD)
    new_lo, new_hi = root(tn, pn)
    old_lo, old_hi = root(to, po)
    need(D("0.0030215551") < new_lo and new_hi < D("0.0030215552"), "#4610 raw crossing bracket")
    need(D("0.00302016597") < old_lo and old_hi < D("0.0030201659771"), "control: PR4535 root reproduced")
    need(sum(pn.values()) == 64404 and sum(po.values()) == 64620, "paid calls 64,404 / 64,620")
    mass = lambda h: sum(r * n for r, n in h.items())
    need(mass(tn) - mass(pn) == mass(to) - mass(po) == 752, "rank-mass surplus 752")
    kappa = (new_lo * 10 ** 8).to_integral_value(rounding="ROUND_FLOOR") - 3
    need(kappa == 302152, "kappa = floor(root * 1e8) - 3 = 0.00302152")
    t_bad, p_bad = histograms(row, P_NEW, idle=False)
    need(root(t_bad, p_bad, hi=D("0.5"))[0] > new_hi, "failure control: dropping idle charges inflates the root")
    print(json.dumps({"status": "PASS_PR4610_CROSSING_RECOMPUTED", "new_root": str(new_lo)[:22],
                      "old_root_control": str(old_lo)[:22], "gain": str(new_lo - old_lo)[:12],
                      "paid_calls": [64620, 64404], "rank_mass_surplus": 752, "kappa_e8": 302152,
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())

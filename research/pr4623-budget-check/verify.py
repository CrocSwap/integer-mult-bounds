#!/usr/bin/env python3
"""Independent check of PR #4623's (dillona, head fd5d3be1) BUDGET.md mass bookkeeping and tangent bounds.

Checks, with nothing imported from #4623: (1) from main's pinned joint-helper-lattice/CONTROLLER.json, the complex p16
main target mass 177,408 minus the idle paid mass 141,568 equals the determinant formula M_p = 2v[p + b(p+2)] = 35,840
(v = 112, b = 8, p = 16); (2) in 40-digit Decimal, the tangent bounds A(t) = h - v + 2v(1+b)^t and
B_J(t) = 2h + v + 4vbt(1+b)^(t-1), h = local helper minus local paid moment, match #4623's printed values at
C = .006 (complex, PR4470 lists) and C = .007 (BIT, 439 H8 helpers vs the PR589 local list) and are negative.
(3) the separator premise of the monotone extension (signed equal-rank terms of h, Jensen base, thin query).
Not checked: decoder and precision sections.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from decimal import Decimal as D, getcontext
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
getcontext().prec = 40


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def moment(h, t):
    return sum(D(n) * (D(r).ln() * t).exp() for r, n in h.items())


def bounds(helpers, paid, v, b, c):
    t = 1 - D(c)
    h = moment(helpers, t) - moment(paid, t)
    a = h - v + 2 * v * (D(1 + b).ln() * t).exp()
    bj = 2 * h + v + 4 * v * b * t * (D(1 + b).ln() * (t - 1)).exp()
    return a, bj


def main():
    row = json.loads((ROOT / "research/joint-helper-lattice/CONTROLLER.json").read_text(encoding="utf-8"))
    main_mass = sum((1 + 8 * sum(term[1:])) * 112 for term in row["diagonal"])
    idle = sum(8 * len(e[2]) * 224 for e in row["physical_events"] if e[0] == "IDLE")
    need(main_mass == 177408 and idle == 141568 and main_mass - idle == 2 * 112 * (16 + 8 * 18) == 35840, "masses")
    ca, cb = bounds({4: 28, 7: 7, 8: 47, 9: 326}, {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}, 112, 8, ".006")
    ba, bb = bounds({8: 439}, {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}, 111, 7, ".007")
    for got, printed in ((ca, "-2.6366097977"), (cb, "-132.6282065737"), (ba, "-3.5731057048"), (bb, "-133.1717283852")):
        need(abs(got - D(printed)) < D("1e-9") and got < 0, "tangent bound matches #4623 and is negative")
    # monotone extension: equal-rank signed terms of h sit on the correct side of the separator, as do the Jensen main
    # base 1 + b + 2b/p (> separator) and the rank-one thin queries (< separator); then J_p(t)/sep^t increases in t
    for helpers, paid, b, sep in (({4: 28, 7: 7, 8: 47, 9: 326}, {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}, 8, 6),
                                  ({8: 439}, {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}, 7, D("7.5"))):
        signed = {r: helpers.get(r, 0) - paid.get(r, 0) for r in set(helpers) | set(paid)}
        need(all((n > 0) == (r > sep) for r, n in signed.items() if n), "signed terms separated")
        need(1 + b > sep and 1 < sep, "Jensen base above and thin query below the separator")
    print(json.dumps({"status": "PASS_PR4623_BUDGET_CHECK", "monotone_separator": True, "main_mass": main_mass, "idle_mass": idle,
                      "M_p": main_mass - idle, "complex_A_BJ": [str(ca)[:14], str(cb)[:16]],
                      "BIT_A_BJ": [str(ba)[:14], str(bb)[:16]], "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())

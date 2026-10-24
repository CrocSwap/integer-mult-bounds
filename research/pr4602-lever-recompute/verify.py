#!/usr/bin/env python3
"""Independent 40-digit recomputation of PR #4602's lever re-pricing (Matarener, head 0dadb877).

#4602 recomputes the #1240 one-at-a-time ideal lever budgets on the current complete invoices (#4470 complex, retained
query-thinned BIT) by solving sum_T n r^(1-C) = sum_P n r^(1-C). This verifier recomputes a subset independently:
nothing is imported from #4602; the complex invoice is rebuilt from main's pinned joint-helper-lattice/CONTROLLER.json
with PR4470's local paid list (8 H8 per call = owned centre) and helper list, the BIT invoice is read from main's
pinned query-thinned-controllers/RESULT.json (targets, paid, whole_idle, thin_queries), and every root is a 40-digit
Decimal bisection (a different engine from #4602's outward-rounded log/exp series). Checked against #4602's reported
values (to the digits it reports):
  complex: baseline 0.0030202; shares idle 59%, local 40%, shears 0.7%, centre 0.5%; centre free 0.00765;
           centre shared 0.00533; query shears free 0.0099; two unpaid coordinates per idle family 0.0282;
           free idle stages > 1/6;
  BIT:     baseline 0.0034642; shares idle 56%, shears 0.8%; shears free 0.0113; two unpaid idle coordinates 0.0319.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from decimal import Decimal as D, getcontext
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HELPERS = {4: 28, 7: 7, 8: 47, 9: 326}
P4470 = {1: 2237, 2: 388, 3: 494, 4: 147, 5: 36, 8: 8}
getcontext().prec = 40


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def complex_parts():
    row = json.loads((ROOT / "research/joint-helper-lattice/CONTROLLER.json").read_text(encoding="utf-8"))
    targets, parts = Counter(), {k: Counter() for k in ("local", "centre", "shears", "idle")}
    for e in row["physical_events"]:
        if e[0] == "LOCAL":
            targets.update(HELPERS)
            for r, n in P4470.items():
                parts["centre" if r == 8 else "local"][r] += n
        elif e[0] == "QUERY_SHEAR":
            parts["shears"][1] += 112
        elif e[0] == "IDLE":
            parts["idle"][8 * len(e[2])] += 224
    for term in row["diagonal"]:
        targets[1 + 8 * sum(term[1:])] += 112
    return targets, parts


def bit_parts():
    d = json.loads((ROOT / "research/query-thinned-controllers/RESULT.json").read_text(encoding="utf-8"))["bit_invoice"]
    ints = lambda h: Counter({int(k): int(v) for k, v in h.items()})
    targets, paid, idle = ints(d["targets"]), ints(d["paid"]), ints(d["whole_idle"])
    shears = Counter({1: int(d["thin_queries"])})
    local = paid.copy()
    local.subtract(idle)
    local.subtract(shears)
    need(min(local.values()) >= 0 and int(d["thin_queries"]) == 15 * 111, "BIT parts")
    return targets, {"local": +local, "centre": Counter(), "shears": shears, "idle": idle}


def moment(h, s):
    return sum(D(n) * (D(r).ln() * s).exp() for r, n in h.items() if n)


def root(targets, paid, hi=D("0.5")):
    lo = D("0.00001")
    need(moment(targets, 1 - lo) > moment(paid, 1 - lo) and moment(targets, 1 - hi) < moment(paid, 1 - hi), "bracket")
    for _ in range(90):
        mid = (lo + hi) / 2
        if moment(targets, 1 - mid) > moment(paid, 1 - mid):
            lo = mid
        else:
            hi = mid
    return lo


def total(parts, **change):
    out = Counter()
    for k, p in parts.items():
        out.update(change.get(k, p))
    return out


def near(x, reported):
    digits = len(reported.split(".")[1])
    return abs(x - D(reported)) <= D(1).scaleb(-digits) / 2


def main():
    res = {}
    for name, (targets, parts) in (("complex", complex_parts()), ("BIT", bit_parts())):
        base = root(targets, total(parts))
        mass = moment(total(parts), 1 - base)
        shares = {k: moment(v, 1 - base) / mass for k, v in parts.items()}
        two_unpaid = Counter({r - 2: n for r, n in parts["idle"].items()})
        out = {"baseline": base, "shares": {k: round(float(v), 4) for k, v in shares.items()},
               "shears_free": root(targets, total(parts, shears=Counter())),
               "two_unpaid_idle": root(targets, total(parts, idle=two_unpaid)),
               "idle_free": root(targets, total(parts, idle=Counter()), hi=D("0.9"))}
        if name == "complex":
            out["centre_free"] = root(targets, total(parts, centre=Counter()))
            half = Counter({r: D(n) / 2 for r, n in parts["centre"].items()})
            out["centre_shared"] = root(targets, total(parts, centre=half))
        res[name] = out
    c, b = res["complex"], res["BIT"]
    need(near(c["baseline"], "0.0030202") and near(b["baseline"], "0.0034642"), "baselines")
    need(round(c["shares"]["idle"], 2) == 0.59 and round(c["shares"]["local"], 2) == 0.40, "complex idle 59%, local 40%")
    need(round(c["shares"]["shears"], 3) == 0.007 and round(c["shares"]["centre"], 3) == 0.005, "shears 0.7%, centre 0.5%")
    need(round(b["shares"]["idle"], 2) == 0.56 and round(b["shares"]["shears"], 3) == 0.008, "BIT idle 56%, shears 0.8%")
    need(near(c["centre_free"], "0.00765") and near(c["centre_shared"], "0.00533"), "centre levers")
    need(near(c["shears_free"], "0.0099") and near(b["shears_free"], "0.0113"), "shear levers")
    need(near(c["two_unpaid_idle"], "0.0282") and near(b["two_unpaid_idle"], "0.0319"), "two unpaid idle coordinates")
    need(c["idle_free"] > D(1) / 6 and b["idle_free"] > D(1) / 6, "free idle stages exceed 1/6")
    # semantic control: #4610's changed local list moves the complex baseline off #4602's reported value
    targets, parts = complex_parts()
    changed = Counter({1: 18 * 2201, 2: 18 * 412, 3: 18 * 506, 4: 18 * 135, 5: 18 * 36})
    need(not near(root(targets, total(parts, local=changed)), "0.0030202"), "control: a changed profile is detected")
    print(json.dumps({"status": "PASS_PR4602_LEVER_RECOMPUTE",
                      "complex": {k: (str(v)[:12] if isinstance(v, D) else v) for k, v in c.items()},
                      "BIT": {k: (str(v)[:12] if isinstance(v, D) else v) for k, v in b.items()},
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())

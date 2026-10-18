"""Minimality + mechanism check for the mu2-variation finding.

(a) complete F2^2 (gsize 4) and F2^1 (gsize 2): is there ANY split where mu2
    varies?  (If none, (4,4) at F2^3 is the minimal variation split.)
(b) F2^3 (4,4): extract the two mu2 clusters and show the mechanism - a side is
    a coset of a 2-dim subspace (affine plane, |A+A|=4) vs a generic 4-set
    (|A+A|=7).  Exact ints.
"""

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
import parity_census as pc  # noqa: E402


def is_structured(mask, gsize):
    """True if a 4-set is structured (a coset of a 2-dim subspace, so |A+A|=4)
    rather than generic (|A+A|=7)."""
    return mask.bit_count() == 4 and pc.selfsum(mask).bit_count() == 4


def complete_census(gsize):
    subs = list(range(1 << gsize))
    out = {}
    for am in subs:
        for bm in subs:
            ok, _ = pc.covers_pair(am, bm, gsize)
            if not ok:
                continue
            k = (am.bit_count(), bm.bit_count())
            sa = pc.selfsum(am).bit_count()
            sb = pc.selfsum(bm).bit_count()
            mu2 = (pc.selfsum(am) & pc.selfsum(bm)).bit_count()
            out.setdefault(k, {"mu2": set(), "sum": set(), "n": 0})
            out[k]["mu2"].add(mu2)
            out[k]["sum"].add(sa + sb)
            out[k]["n"] += 1
    return out


def vary_splits(gsize):
    res = complete_census(gsize)
    varying = {k: v for k, v in res.items() if len(v["mu2"]) > 1}
    return res, varying


def mechanism_44():
    gsize = 8
    rows = []
    for ac in combinations(range(8), 4):
        am = pc.mask_of(ac)
        for bc in combinations(range(8), 4):
            bm = pc.mask_of(bc)
            ok, _ = pc.covers_pair(am, bm, gsize)
            if not ok:
                continue
            sa = pc.selfsum(am).bit_count()
            sb = pc.selfsum(bm).bit_count()
            mu2 = (pc.selfsum(am) & pc.selfsum(bm)).bit_count()
            rows.append((is_structured(am, 8), is_structured(bm, 8), sa, sb, mu2, ac, bc))
    # group by (structuredA, structuredB)
    from collections import Counter
    grp = Counter((r[0], r[1], r[4]) for r in rows)  # (structA,structB,mu2)->count
    return rows, grp


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for gsize, name in [(2, "F2^1"), (4, "F2^2"), (8, "F2^3")]:
        cres, varying = vary_splits(gsize)
        res[name] = {
            "splits_with_covers": len(cres),
            "varying_splits": {("%d,%d" % k): {"mu2_set": sorted(v["mu2"]),
                                               "sum_set": sorted(v["sum"]),
                                               "n": v["n"]}
                               for k, v in sorted(varying.items())},
        }
        print("=== %s (gsize %d) complete: %d splits with covers; %d vary in mu2 ==="
              % (name, gsize, len(cres), len(varying)))
        for k in sorted(cres):
            r = cres[k]
            print("  split (%d,%d) n=%d mu2=%s sum=%s %s"
                  % (k[0], k[1], r["n"], sorted(r["mu2"]), sorted(r["sum"]),
                     "<-- VARIES" if len(r["mu2"]) > 1 else ""))
    print()
    rows, grp = mechanism_44()
    res["F2^3_(4,4)_mechanism"] = {
        "(structA,structB,mu2)->count": {"%s,%s,%d" % k: v for k, v in sorted(grp.items())}
    }
    print("=== F2^3 (4,4) mechanism: (structA?, structB?, mu2) -> count ===")
    for k in sorted(grp):
        print("  structA=%s structB=%s mu2=%d : %d covers" % (k[0], k[1], k[2], grp[k]))
    # show one example of each
    seen = set()
    print("--- example cover per (structA,structB,mu2) ---")
    for r in rows:
        key = (r[0], r[1], r[4])
        if key in seen:
            continue
        seen.add(key)
        print("  A=%s B=%s sa=%d sb=%d mu2=%d structA=%s structB=%s"
              % (list(r[5]), list(r[6]), r[2], r[3], r[4], r[0], r[1]))
    (HERE / "MU2-MECH.json").write_text(
        json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("MU2_MINIMALITY_DONE", flush=True)


if __name__ == "__main__":
    main()

"""KB3k: press the mu2-constant even-half condition.

For a reduced covering pair (A, B) of G = F2^m (A+B = G and (A+A) u (B+B) = G)
define mu2 = |(A+A) n (B+B)|.  Exact identity (proved in README):

    mu2 = |A+A| + |B+B| - 2^m

(since |(A+A) u (B+B)| = 2^m for a cover and inclusion-exclusion).  So mu2 is
constant per split (a, b) iff the selfsum-size SUM |A+A| + |B+B| is constant per
split.  This module searches for the minimal (smallest m, smallest split) cover
split at which mu2 (equivalently the sum) VARIES, by COMPLETE enumeration where
feasible and clearly-labelled random sampling where not.  Exact int arithmetic,
no floats.

Modes
  m3       complete F2^3, every split
  m4       complete F2^4 for a list of feasible splits
  m5       random sampling in F2^5 (and a targeted exact small-split pass)
  identity exhaustive sanity: mu2 == sa+sb-2^m on every enumerated cover
"""

import json
import random
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))

import parity_census as pc  # noqa: E402  (vendored byte-exact KB3j engine)


def profile_of(am, bm, gsize):
    allg = (1 << gsize) - 1
    sa = pc.selfsum(am)
    sb = pc.selfsum(bm)
    union = sa | sb
    inter = sa & sb
    return {
        "a": am.bit_count(),
        "b": bm.bit_count(),
        "sa": sa.bit_count(),
        "sb": sb.bit_count(),
        "mu2": inter.bit_count(),
        "self_union": union.bit_count(),
        "deficit": (allg.bit_count() - union.bit_count()),
    }


def covers(am, bm, gsize):
    ok, _ = pc.covers_pair(am, bm, gsize)
    return ok


def split_summary(rows):
    """rows: list of profile dicts at one split.  Return mu2 / sum ranges."""
    sums = {r["sa"] + r["sb"] for r in rows}
    mu2s = {r["mu2"] for r in rows}
    sas = sorted({r["sa"] for r in rows})
    sbs = sorted({r["sb"] for r in rows})
    return {
        "covers": len(rows),
        "sa_set": sas,
        "sb_set": sbs,
        "sum_set": sorted(sums),
        "mu2_set": sorted(mu2s),
        "sum_constant": len(sums) == 1,
        "mu2_constant": len(mu2s) == 1,
    }


def check_identity(rows, gsize):
    """Identity: mu2 = sa + sb - |G| and self_union = |G| for every cover
    (|G| = gsize = number of group elements = 2^m)."""
    bad = 0
    for r in rows:
        if r["mu2"] != r["sa"] + r["sb"] - gsize:
            bad += 1
        if r["self_union"] != gsize:
            bad += 1000  # self_union must be full for a cover
    return bad


def run_m3():
    gsize = 8
    subs = list(range(1 << gsize))
    by_split = {}
    for am in subs:
        for bm in subs:
            if covers(am, bm, gsize):
                k = (am.bit_count(), bm.bit_count())
                by_split.setdefault(k, []).append(profile_of(am, bm, gsize))
    out = {"gsize": gsize, "splits": {}}
    bad = 0
    for k in sorted(by_split):
        s = split_summary(by_split[k])
        bad += check_identity(by_split[k], gsize)
        out["splits"]["%d,%d" % k] = s
    out["identity_violations"] = bad
    out["any_mu2_variation"] = any(
        not s["mu2_constant"] for s in out["splits"].values()
    )
    return out


def run_m4(split_list):
    gsize = 16
    out = {"gsize": gsize, "splits": {}}
    for (a, b) in split_list:
        rows = []
        for ac in combinations(range(gsize), a):
            am = pc.mask_of(ac)
            for bc in combinations(range(gsize), b):
                bm = pc.mask_of(bc)
                if covers(am, bm, gsize):
                    rows.append(profile_of(am, bm, gsize))
        s = split_summary(rows)
        s["identity_violations"] = check_identity(rows, gsize)
        out["splits"]["%d,%d" % (a, b)] = s
    out["any_mu2_variation"] = any(
        not s["mu2_constant"] for s in out["splits"].values()
    )
    return out


def run_m5(sample_split_list, trials=200000, seed=20261016, gsize=32):
    """Random sampling: generate random A,B of given sizes, keep covers, and
    see whether mu2 varies at a fixed split.  Sampling only FINDS variation
    (a found variation is exact proof of non-constancy); it cannot prove
    constancy."""
    rng = random.Random(seed)
    out = {"gsize": gsize, "mode": "random-sampling", "trials_per_split": trials, "splits": {}}
    for (a, b) in sample_split_list:
        mu2s = {}
        sums = {}
        covers_seen = 0
        for _ in range(trials):
            ac = rng.sample(range(gsize), a)
            bc = rng.sample(range(gsize), b)
            am = pc.mask_of(ac)
            bm = pc.mask_of(bc)
            if covers(am, bm, gsize):
                covers_seen += 1
                p = profile_of(am, bm, gsize)
                mu2s[p["mu2"]] = mu2s.get(p["mu2"], 0) + 1
                sums[p["sa"] + p["sb"]] = sums.get(p["sa"] + p["sb"], 0) + 1
        out["splits"]["%d,%d" % (a, b)] = {
            "covers_sampled": covers_seen,
            "mu2_hist": dict(sorted(mu2s.items())),
            "sum_hist": dict(sorted(sums.items())),
            "mu2_constant_observed": len(mu2s) <= 1,
        }
    out["any_mu2_variation_observed"] = any(
        not s["mu2_constant_observed"] for s in out["splits"].values()
    )
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "m3"
    if mode == "m3":
        res = run_m3()
    elif mode == "m4":
        splits = [(1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (3, 3), (4, 4), (2, 2), (1, 5)]
        res = run_m4(splits)
    elif mode == "m5":
        splits = [(2, 8), (4, 6), (5, 5), (3, 7), (4, 8)]
        res = run_m5(splits)
    elif mode == "m5odd":
        splits = [(5, 5), (7, 7), (5, 7), (3, 7)]
        res = run_m5(splits, trials=400000, seed=777, gsize=32)
    elif mode == "m6":
        # the exact 18-point target splits, both-odd, at reduced F2^6 (gsize 64)
        splits = [(11, 7), (9, 9)]
        res = run_m5(splits, trials=400000, seed=1616, gsize=64)
    elif mode == "identity":
        res = {"m3": check_identity_m3()}
    else:
        raise SystemExit("usage: mu2_search.py m3|m4|m5|m5odd|m6|identity")
    print(json.dumps(res, indent=2, sort_keys=True))
    tag = {"m3": "MU2_M3", "m4": "MU2_M4", "m5": "MU2_M5", "m5odd": "MU2_M5ODD",
           "m6": "MU2_M6", "identity": "MU2_ID"}[mode]
    (HERE / ("MU2-%s.json" % mode.upper())).write_text(
        json.dumps(res, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(tag + "_DONE", flush=True)


def check_identity_m3():
    gsize = 8
    subs = list(range(1 << gsize))
    bad = 0
    n = 0
    for am in subs:
        for bm in subs:
            if covers(am, bm, gsize):
                n += 1
                p = profile_of(am, bm, gsize)
                if p["mu2"] != p["sa"] + p["sb"] - gsize:
                    bad += 1
    return {"covers": n, "violations": bad}


if __name__ == "__main__":
    main()

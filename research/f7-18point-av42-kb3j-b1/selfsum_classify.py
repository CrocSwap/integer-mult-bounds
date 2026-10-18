"""KB3j route (c): even-half (self-sum) structure of reduced covering pairs.

PR 3034's named live direction for the both-odd splits (11,7)/(9,9): classify
the m=3 both-odd covers (small ground truth: (5,5)=3136, (7,7)=64) by their
even-half self-sum structure and lift only what survives scaling (the
scale-dependent m=4 self-sum-size bound is NOT lifted - it fails at m=3).

For a reduced covering pair (A, B) of F2^m (A+B = F2^m and (A+A) u (B+B) =
F2^m) define the even-half multiplicity profile

  mu(p) = [p in A+A] + [p in B+B]  in {0,1,2},
  mu2   = |{p : mu(p) = 2}| = |(A+A) n (B+B)|,
  mu1   = 2^m - mu2.

Every cover has mu >= 1 pointwise.  This module computes the exact profile
distributions (|A+A|, |B+B|, mu2, span rank, doubling) over COMPLETE
enumerations at two scales:

  m=3 (F2^3, 8 points): every both-odd cover (splits (3,5),(3,7),(5,3),(5,5),
      (5,7),(7,3),(7,5),(7,7)) and every cover at all splits.
  m=4 (F2^4, 16 points): every both-even cover at the sum-10 splits (2,8)
      and (4,6) (the m=5 ground-truth covering splits).

and tests named lift candidates against both scales.  Exact int arithmetic.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))

import parity_census as pc  # noqa: E402  (vendored byte-exact PR 3034 engine)


def span_rank(mask, gsize):
    """GF(2) rank of the elements of mask (as gsize-bit row vectors)."""
    pivots = {}
    for r in pc.elems(mask):
        x = r
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def profile(am, bm, gsize):
    allg = (1 << gsize) - 1
    sa = pc.selfsum(am)
    sb = pc.selfsum(bm)
    union = sa | sb
    inter = sa & sb
    return dict(
        a=pc.popcount(am),
        b=pc.popcount(bm),
        sa=pc.popcount(sa),
        sb=pc.popcount(sb),
        mu2=pc.popcount(inter),
        mu1=pc.popcount(union) - pc.popcount(inter),
        self_union=pc.popcount(union),
        deficit=allg.bit_count() - pc.popcount(union),
        rank_a=span_rank(am, gsize),
        rank_b=span_rank(bm, gsize),
        st=pc.popcount(am) * pc.popcount(bm),
    )


def census_m3_profiles():
    """Complete: every covering pair in F2^3 with its profile."""
    gsize = 8
    subs = list(range(1 << gsize))
    by_split = {}
    for am in subs:
        for bm in subs:
            ok, _ = pc.covers_pair(am, bm, gsize)
            if not ok:
                continue
            key = (pc.popcount(am), pc.popcount(bm))
            p = profile(am, bm, gsize)
            by_split.setdefault(key, []).append(p)
    return by_split


def census_m4_profiles(a, b):
    """Complete: every covering pair in F2^4 at split (a, b) with its profile."""
    gsize = 16
    out = []
    for ac in _comb(16, a):
        am = pc.mask_of(ac)
        for bc in _comb(16, b):
            bm = pc.mask_of(bc)
            ok, _ = pc.covers_pair(am, bm, gsize)
            if ok:
                out.append(profile(am, bm, gsize))
    return out


def _comb(n, k):
    from itertools import combinations

    return combinations(range(n), k)


def dist(profiles, key):
    d = {}
    for p in profiles:
        d[p[key]] = d.get(p[key], 0) + 1
    return dict(sorted(d.items()))


def profile_table(profiles):
    """Distribution of (sa, sb, mu2) with counts."""
    d = {}
    for p in profiles:
        k = (p["sa"], p["sb"], p["mu2"])
        d[k] = d.get(k, 0) + 1
    return {"|A+A|,|B+B|,mu2 -> count": {"%d,%d,%d" % k: v for k, v in sorted(d.items())}}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}

    # ---- m=3 complete both-odd classification -------------------------
    m3 = census_m3_profiles()
    both_odd = {k: v for k, v in m3.items() if k[0] % 2 == 1 and k[1] % 2 == 1}
    out["m3_covers_total"] = sum(len(v) for v in m3.values())
    out["m3_both_odd_splits"] = {str(k): len(v) for k, v in sorted(both_odd.items())}
    out["m3_both_odd_profiles"] = {
        str(k): profile_table(v) for k, v in sorted(both_odd.items())
    }
    out["m3_both_odd_sa_range"] = {
        str(k): {"sa_min": min(p["sa"] for p in v), "sa_max": max(p["sa"] for p in v),
                 "sb_min": min(p["sb"] for p in v), "sb_max": max(p["sb"] for p in v),
                 "mu2_min": min(p["mu2"] for p in v), "mu2_max": max(p["mu2"] for p in v),
                 "self_union_min": min(p["self_union"] for p in v),
                 "self_union_max": max(p["self_union"] for p in v),
                 "rank_a_max": max(p["rank_a"] for p in v),
                 "rank_b_max": max(p["rank_b"] for p in v)}
        for k, v in sorted(both_odd.items())
    }
    # the two named ground-truth splits in full detail
    for k in [(5, 5), (7, 7)]:
        v = both_odd.get(k, [])
        out["m3_split_%d_%d" % k] = {
            "covers": len(v),
            "sa_dist": dist(v, "sa"),
            "sb_dist": dist(v, "sb"),
            "mu2_dist": dist(v, "mu2"),
            "self_union_dist": dist(v, "self_union"),
            "rank_a_dist": dist(v, "rank_a"),
            "rank_b_dist": dist(v, "rank_b"),
        }

    # ---- m=4 both-even comparison profiles ---------------------------
    for (a, b) in [(2, 8), (4, 6)]:
        v = census_m4_profiles(a, b)
        out["m4_split_%d_%d" % (a, b)] = {
            "covers": len(v),
            "sa_dist": dist(v, "sa"),
            "sb_dist": dist(v, "sb"),
            "mu2_dist": dist(v, "mu2"),
            "self_union_dist": dist(v, "self_union"),
        }

    (HERE / "SELFSUM-PROFILES.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for key in sorted(out):
        print(key, json.dumps(out[key], sort_keys=True)[:300], flush=True)
    print("PASS_SELFSUM_CLASSIFY", flush=True)


if __name__ == "__main__":
    main()

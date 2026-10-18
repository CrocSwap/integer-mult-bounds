"""Bounded both-odd cover search: does mu2 vary among BOTH-ODD covers at the
target regime (the (11,7)/(9,9) analogue)?

Random (11,7)/(9,9) covers at F2^6 are too rare to sample, so this uses a
hill-climbing mutation to force the cover conditions (cross A+B = G and
(A+A) u (B+B) = G), then records (sa, sb, mu2) for each cover found and reports
whether mu2 VARIES at a fixed both-odd split.  A found variation is exact proof
of non-constancy for that split; no variation found is not a proof of constancy.
Exact ints.  Bounded trials per split.
"""

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
import parity_census as pc  # noqa: E402


def deficit(am, bm, gsize):
    allg = (1 << gsize) - 1
    cross = pc.sumset(am, bm)
    selfs = pc.selfsum(am) | pc.selfsum(bm)
    return (allg ^ cross).bit_count() + (allg ^ selfs).bit_count()


def profile(am, bm, gsize):
    sa = pc.selfsum(am)
    sb = pc.selfsum(bm)
    inter = sa & sb
    return (sa.bit_count(), sb.bit_count(), inter.bit_count())


def climb(a_list, b_list, gsize, rng, max_steps=4000):
    am = pc.mask_of(a_list)
    bm = pc.mask_of(b_list)
    d = deficit(am, bm, gsize)
    for _ in range(max_steps):
        if d == 0:
            return a_list, b_list, True
        # try swapping one element in A or B
        improved = False
        for which in (0, 1):
            cur = a_list if which == 0 else b_list
            other = b_list if which == 0 else a_list
            in_set = set(cur)
            out_set = [x for x in range(gsize) if x not in in_set]
            rng.shuffle(out_set)
            for old in list(cur):
                for new in out_set[:8]:
                    trial = [new if x == old else x for x in cur]
                    if which == 0:
                        nd = deficit(pc.mask_of(trial), pc.mask_of(other), gsize)
                    else:
                        nd = deficit(pc.mask_of(other), pc.mask_of(trial), gsize)
                    if nd < d:
                        if which == 0:
                            a_list = trial
                        else:
                            b_list = trial
                        d = nd
                        improved = True
                        break
                if improved:
                    break
            if improved:
                break
        if not improved:
            return a_list, b_list, d == 0
    return a_list, b_list, d == 0


def search_split(a, b, gsize, restarts=200, seed=0):
    rng = random.Random(seed)
    found = {}
    successes = 0
    for r in range(restarts):
        a_list = rng.sample(range(gsize), a)
        b_list = rng.sample(range(gsize), b)
        a_list, b_list, ok = climb(a_list, b_list, gsize, rng)
        if ok:
            successes += 1
            p = profile(pc.mask_of(a_list), pc.mask_of(b_list), gsize)
            found[p] = found.get(p, 0) + 1
    return {
        "covers_found": successes,
        "profiles_(sa,sb,mu2)_counts": {"%d,%d,%d" % k: v for k, v in sorted(found.items())},
        "mu2_set": sorted({k[2] for k in found}),
        "mu2_constant_observed": len({k[2] for k in found}) <= 1,
    }


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    # both-odd analogue of (11,7)/(9,9) at F2^5 (gsize 32) and F2^6 (gsize 64)
    cases = [
        ("F2^5 (7,7)", 7, 7, 32, 400, 12345),
        ("F2^6 (9,9)", 9, 9, 64, 300, 991),
        ("F2^6 (11,7)", 11, 7, 64, 300, 771),
    ]
    for name, a, b, gsize, restarts, seed in cases:
        out[name] = search_split(a, b, gsize, restarts=restarts, seed=seed)
        out[name]["gsize"] = gsize
    for k in out:
        print(k, out[k], flush=True)
    any_var = any(not v["mu2_constant_observed"] for v in out.values())
    print("ANY_BOTH_ODD_MU2_VARIATION =", any_var, flush=True)
    (HERE / "MU2-ODD.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("MU2_ODD_SEARCH_DONE", flush=True)


if __name__ == "__main__":
    main()

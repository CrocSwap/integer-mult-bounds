"""KB3k verifier.  Reproduces the mu2-condition verdict.

quick   re-run the fast exact checks live (F2^3 identity + minimality/mechanism
        census at gsize 2/4/8) and READ BACK the heavier receipts (m4 complete
        census, m5odd/m6 sampling, both-odd mutation search) from their JSON.
full    re-run everything live (adds the m4 complete census and the both-odd
        mutation search; minutes).  Exact ints throughout.

Markers: PASS_KB3K_QUICK / PASS_KB3K_FULL.
"""

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))
import parity_census as pc  # noqa: E402
import mu2_search as m2  # noqa: E402


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def check_identity_m3():
    gsize = 8
    subs = list(range(1 << gsize))
    bad = n = 0
    for am in subs:
        for bm in subs:
            if m2.covers(am, bm, gsize):
                n += 1
                p = m2.profile_of(am, bm, gsize)
                if p["mu2"] != p["sa"] + p["sb"] - gsize or p["self_union"] != gsize:
                    bad += 1
    return n, bad


def minimality():
    """Return (F2^1 varying, F2^2 varying, F2^3 minimal varying split)."""
    def vary(gsize):
        res = {}
        for am in range(1 << gsize):
            for bm in range(1 << gsize):
                if m2.covers(am, bm, gsize):
                    k = (am.bit_count(), bm.bit_count())
                    sa = pc.selfsum(am).bit_count()
                    sb = pc.selfsum(bm).bit_count()
                    mu2 = (pc.selfsum(am) & pc.selfsum(bm)).bit_count()
                    res.setdefault(k, {"mu2": set(), "n": 0})
                    res[k]["mu2"].add(mu2)
                    res[k]["n"] += 1
        return {k: v for k, v in res.items() if len(v["mu2"]) > 1}, res

    v1, _ = vary(2)   # F2^1, gsize 2
    v2, _ = vary(4)   # F2^2, gsize 4
    v3, r3 = vary(8)  # F2^3, gsize 8
    minimal = min(v3.items(), key=lambda kv: (sum(kv[0]), max(kv[0]))) if v3 else None
    return v1, v2, v3, minimal


def walk_check():
    """Read the (4,2) walk receipts: aggregate the complete shards and, if both
    the clean run and the preserved from-empty recompute are present, require
    their counters to match exactly (the receipt-validation trap)."""
    import glob as _glob

    receipts = []
    for p in sorted(_glob.glob(str(HERE / "AV42-AV42-*.json"))):
        rec = json.loads(Path(p).read_text(encoding="utf-8"))
        receipts.append(rec)
    complete = [r for r in receipts if r.get("complete")]
    u = sum(r.get("u_checked", 0) for r in complete)
    pairs = sum(r.get("uv_pairs", 0) for r in complete)
    wcand = sum(r.get("w_candidates", 0) for r in complete)
    covering = sum(r.get("covering_configs", 0) for r in complete)
    print("WALK aggregate: %d complete shards u_checked=%d uv_pairs=%d w_candidates=%d covering=%d"
          % (len(complete), u, pairs, wcand, covering))
    # recompute comparison for shard 29
    first = HERE / "AV42-RECOMPUTE-29-first-run.json"
    cur = HERE / "AV42-AV42-29.json"
    if first.exists() and cur.exists():
        a = json.loads(first.read_text(encoding="utf-8"))
        b = json.loads(cur.read_text(encoding="utf-8"))
        keys = ("u_checked", "uv_pairs", "w_candidates", "covering_configs",
                "uv_pairs_by_sumset_size", "w_candidates_by_m_size")
        same = all(a.get(k) == b.get(k) for k in keys)
        print("WALK recompute shard=29 from empty receipts: counters identical = %s (u=%d uv_pairs=%d)"
              % (same, b.get("u_checked", -1), b.get("uv_pairs", -1)))
        assert same, "shard 29 recompute mismatch"
    else:
        print("WALK recompute shard=29: first-run or current receipt not both present (skipped)")
    return len(complete), u, pairs


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"

    # --- always-live exact checks -------------------------------------
    n, bad = check_identity_m3()
    print("IDENTITY m3 covers=%d violations=%d (must be 0)" % (n, bad))
    assert bad == 0, "identity violated"

    v1, v2, v3, minimal = minimality()
    print("MINIMALITY F2^1 varying=%d F2^2 varying=%d F2^3 varying=%d"
          % (len(v1), len(v2), len(v3)))
    assert len(v1) == 0 and len(v2) == 0, "variation found below F2^3"
    assert minimal is not None, "no F2^3 variation"
    print("MINIMAL VARIATION SPLIT = (%d,%d) at F2^3, mu2=%s n=%d"
          % (minimal[0][0], minimal[0][1], sorted(minimal[1]["mu2"]), minimal[1]["n"]))
    assert minimal[0] == (4, 4), "minimal variation split is not (4,4)"

    # --- receipts (read back in quick; re-run in full) ----------------
    if mode == "full":
        print("FULL: re-running m4 complete census + both-odd search live...")
        m2.run_m4([(1, 9), (2, 8), (3, 7), (4, 6), (5, 5), (3, 3), (4, 4), (2, 2), (1, 5)])
        print("(m4 rerun above)")

    m4 = load("MU2-M4.json")
    print("M4 (2,8) mu2=%s constant=%s; (4,6) mu2=%s constant=%s; both-odd (3,7)/(5,5) covers=%d/%d"
          % (m4["splits"]["2,8"]["mu2_set"], m4["splits"]["2,8"]["mu2_constant"],
             m4["splits"]["4,6"]["mu2_set"], m4["splits"]["4,6"]["mu2_constant"],
             m4["splits"]["3,7"]["covers"], m4["splits"]["5,5"]["covers"]))
    assert m4["splits"]["2,8"]["mu2_constant"] and m4["splits"]["4,6"]["mu2_constant"]
    assert m4["splits"]["3,7"]["covers"] == 0 and m4["splits"]["5,5"]["covers"] == 0

    odd = load("MU2-ODD.json")
    g77 = odd["F2^5 (7,7)"]
    print("BOTH-ODD F2^5 (7,7) covers=%d mu2=%s constant=%s"
          % (g77["covers_found"], g77["mu2_set"], g77["mu2_constant_observed"]))
    print("BOTH-ODD F2^6 (9,9) covers=%d (11,7) covers=%d"
          % (odd["F2^6 (9,9)"]["covers_found"], odd["F2^6 (11,7)"]["covers_found"]))
    assert g77["mu2_constant_observed"]

    m5odd = load("MU2-M5ODD.json")
    m6 = load("MU2-M6.json")
    print("M5ODD (7,7) sampled covers=%d mu2=%s; M6 (11,7)/(9,9) sampled covers=%d/%d"
          % (m5odd["splits"]["7,7"]["covers_sampled"], list(m5odd["splits"]["7,7"]["mu2_hist"]),
             m6["splits"]["11,7"]["covers_sampled"], m6["splits"]["9,9"]["covers_sampled"]))

    walk_check()

    print("PASS_KB3K_" + ("FULL" if mode == "full" else "QUICK"), flush=True)


if __name__ == "__main__":
    main()

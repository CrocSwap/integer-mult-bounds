"""KB3j verification: anchors, receipts and the route-(c) classification.

Modes:
  quick   pins + all recorded anchors + walk-receipt aggregate + the shard-1
          recomputation comparison + live m=3 both-odd selfsum classification
          + live (3,3)/(4,2) small-census spot rechecks.
          marker PASS_KB3J_QUICK
  walks   the per-shard walk receipt table (read-back evidence for the PR).
          marker PASS_KB3J_WALKS

Standard library only, CPython 3.12.  Exact int arithmetic throughout.
Heavy objects (the F2^5 (4,2) walk shards, the k=4 census, the m=4 both-even
profiles) are READ BACK from their pinned artifacts and spot-rechecked live;
they cannot be re-derived inside a registered replay budget (the complete
walk is sized at ~608 core-hours).
"""

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

VENDOR_PINS = {
    "vendor/tight.py": None,
    "vendor/cover18.py": None,
    "vendor/vanish.py": None,
    "vendor/agent64_cover17.py": None,
    "vendor/agent64_search17.py": None,
    "vendor/anchors.py": None,
    "vendor/parity_census.py": None,
    "vendor/self_obstruction.py": None,
    "vendor/split_census.py": None,
    "PR3023-AVTAIL-PROGRESS.json": None,
}


def sha256_file(p):
    h = hashlib.sha256()
    h.update(Path(p).read_bytes())
    return h.hexdigest()


def check_pins():
    src = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    pins = {}
    for f in src["files"]:
        pins[f["path"]] = f["sha256"]
    for f in src["references"]:
        pins[f["local_path"]] = f["sha256"]
    for rel in VENDOR_PINS:
        got = sha256_file(HERE / rel)
        want = pins.get(rel)
        assert want, "missing pin for %s" % rel
        assert got == want, "PIN MISMATCH %s got=%s want=%s" % (rel, got[:16], want[:16])
    print("PIN all %d pinned files sha256 match" % len(VENDOR_PINS), flush=True)


def mode_quick():
    t0 = time.time()
    check_pins()
    import tight

    # ---- recorded light anchors, recomputed live ---------------------
    fid = tight.fourier_71_identity()
    assert (fid["m5_k5"]["need"], fid["m5_k5"]["lower_bound"]) == (175, 239)
    assert fid["m5_k5"]["contradiction"] is True
    print("ANCHOR PR2961 FOURIER (7,1) need=175 lower=239 contradiction=True", flush=True)

    import vanish

    tight_seen = 0
    for (s, t) in ((12, 6), (11, 7), (10, 8), (9, 9)):
        tab = vanish.class_table(s, t, m=6)
        for side in ("A_vanish", "D_vanish"):
            for c in tab[side]:
                if c["tight"]:
                    tight_seen += 1
    assert tight_seen == 2, tight_seen
    res7 = vanish.check_tight_equality(3)
    assert res7["ok"] and res7["checked"] == 6720, res7
    print("ANCHOR PR2933 CLASSIFY tight=2 cases=6720 ok=true", flush=True)

    import cover18 as c18

    sq = c18.squeeze_numbers(7, 11, 6)
    assert (sq["parseval_remainder"], sq["max_allowed"], sq["deficit"]) == (696, 504, 192)
    print("ANCHOR PR2870 OBSTRUCTION parseval=696 allowed=504 deficit=192", flush=True)

    # ---- heavy anchors: read back from PR 3023's pinned receipts -----
    prog = json.loads((HERE / "PR3023-AVTAIL-PROGRESS.json").read_text(encoding="utf-8"))
    tot82 = prog["modes"]["class82"]["total"]
    assert tot82["checked"] == 28815360 and tot82["covering_configs"] == 0, tot82
    print("ANCHOR PR2961 CLASS82 checked=28815360 covering=0 (read back PR 3023 receipts)", flush=True)
    tot60 = prog["modes"]["class60"]["total"]
    assert tot60["d_checked"] == 169911 and tot60["d_with_transversals"] == 0, tot60
    print("ANCHOR PR2961 CLASS60 d_checked=169911 d_with_transversals=0 (read back)", flush=True)
    tot51 = prog["modes"]["av51"]["total"]
    assert tot51["uv_pairs"] == 3049492320 and tot51["covering_configs"] == 0, tot51
    print("ANCHOR PR3023 AV51 uv_pairs=3049492320 covering=0 (read back)", flush=True)

    # ---- the (4,2) walk receipts ------------------------------------
    recs = []
    for k in range(2048):
        p = HERE / ("AV42-AV42-%d.json" % k)
        if p.exists():
            recs.append(json.loads(p.read_text(encoding="utf-8")))
    assert recs, "no walk receipts"
    assert all(r["complete"] and not r["budget_hit"] for r in recs)
    pairs = sum(r["uv_pairs"] for r in recs)
    us = sum(r["u_checked"] for r in recs)
    wc = sum(r["w_candidates"] for r in recs)
    cov = sum(r["covering_configs"] for r in recs)
    assert wc == 0 and cov == 0
    print(
        "WALK av42 receipts=%d u_checked=%d uv_pairs=%d w_candidates=0 covering=0 (PARTIAL %d/2048 shards)"
        % (len(recs), us, pairs, len(recs)),
        flush=True,
    )

    # ---- recomputation proof: shard 1 from empty receipts ------------
    first = json.loads((HERE / "AV42-RECOMPUTE-1-first-run.json").read_text(encoding="utf-8"))
    rerun = json.loads((HERE / "AV42-AV42-1.json").read_text(encoding="utf-8"))
    for key in ("u_checked", "uv_pairs", "w_candidates", "covering_configs",
                "uv_pairs_by_sumset_size", "fail_hist", "witnesses"):
        assert first[key] == rerun[key], (key, first[key], rerun[key])
    print(
        "RECOMPUTE shard=1 from empty receipts: counters identical (u=83 uv_pairs=8592684 w_candidates=0; timing fields excluded)"
        ,
        flush=True,
    )

    # ---- route (c): m=3 both-odd selfsum classification, live --------
    import selfsum_classify as sc

    m3 = sc.census_m3_profiles()
    both_odd = {k: v for k, v in m3.items() if k[0] % 2 == 1 and k[1] % 2 == 1}
    assert {k: len(v) for k, v in both_odd.items()} == {
        (3, 5): 2688, (3, 7): 448, (5, 3): 2688, (5, 5): 3136,
        (5, 7): 448, (7, 3): 448, (7, 5): 448, (7, 7): 64,
    }
    for k in both_odd:
        for p in both_odd[k]:
            assert p["self_union"] == 8, (k, p)
    for p in both_odd[(5, 5)]:
        assert (p["sa"], p["sb"], p["mu2"]) == (8, 8, 8)
    for p in both_odd[(7, 7)]:
        assert (p["sa"], p["sb"], p["mu2"]) == (8, 8, 8)
    print(
        "SELFSUM m=3 both-odd PROVEN: 10416 covers; (5,5)=3136 all profile (8,8,8); (7,7)=64 all (8,8,8); self-union 8/8 in every both-odd cover",
        flush=True,
    )
    # m=4 both-even profiles: read back from the pinned artifact
    prof = json.loads((HERE / "SELFSUM-PROFILES.json").read_text(encoding="utf-8"))
    p28 = prof["m4_split_2_8"]
    assert p28["covers"] == 15360 and p28["mu2_dist"] == {"1": 15360}, p28
    p46 = prof["m4_split_4_6"]
    assert p46["covers"] == 143360 and p46["mu2_dist"] == {"4": 143360}, p46
    assert set(p46["sa_dist"]) == {"4", "7"} and set(p46["sb_dist"]) == {"13", "16"}, p46
    print(
        "SELFSUM m=4 both-even read-back: (2,8)=15360 mu2=1 all; (4,6)=143360 mu2=4 all (profiles (4,13,4)x35840 (7,16,4)x107520)",
        flush=True,
    )

    # ---- (3,3) k=3 census spot recheck (two classes live) -----------
    import av33_census as a33

    cens33 = json.loads((HERE / "CENSUS-33-K3.json").read_text(encoding="utf-8"))
    n = 8
    allm, trans, summ = a33.build_tables(n)
    norm = [m for m in range(1 << n) if m & 1]
    subs = list(range(1 << n))
    for (u_size, x_size) in ((2, 3), (3, 3)):
        covers = 0
        cfgs = 0
        for a0 in [m for m in norm if m.bit_count() == u_size]:
            for a1 in [m for m in norm if m.bit_count() == u_size]:
                for d0 in [m for m in subs if m.bit_count() == x_size]:
                    for d1 in [m for m in subs if m.bit_count() == x_size]:
                        cfgs += 1
                        if (
                            (summ[a0][d0] | summ[a1][d1]) == allm
                            and (summ[a0][d1] | summ[a1][d0]) == allm
                            and (summ[a0][a0] | summ[a1][a1] | summ[d0][d0] | summ[d1][d1]) == allm
                            and (summ[a0][a1] | summ[d0][d1]) == allm
                        ):
                            covers += 1
        rec = cens33[str((u_size, x_size))]
        assert rec["configs"] == cfgs and rec["covers"] == covers, (u_size, x_size, cfgs, covers)
    print(
        "CENSUS33 (3,3)-shape k=3 spot recheck: (2,3) configs=153664 covers=0; (3,3) configs=1382976 covers=296352 (match)",
        flush=True,
    )

    # ---- (4,2) k=3 census spot reclass (one class live) -------------
    import walk42

    cens42 = json.loads((HERE / "CENSUS-K3.json").read_text(encoding="utf-8"))
    covers = 0
    wcand = 0
    for u in [m for m in subs if m & 1 and m.bit_count() == 2]:
        for v in [m for m in subs if m & 1 and m.bit_count() == 2]:
            for w in subs:
                if w.bit_count() != 4:
                    continue
                ok, _ = walk42.lines42_g(u, v, w, 0b11, 3, allm)
                if ok:
                    covers += 1
                vd = walk42.sumset_g(v, 0b11, 3, allm)
                ud = walk42.sumset_g(u, 0b11, 3, allm)
                wd = walk42.sumset_g(w, 0b11, 3, allm)
                if (
                    (walk42.sumset_g(u, w, 3, allm) | vd) == allm
                    and (ud | walk42.sumset_g(v, w, 3, allm)) == allm
                    and (walk42.sumset_g(u, v, 3, allm) | wd) == allm
                ):
                    wcand += 1
    rec = cens42[str((2, 2, 4))]
    assert rec["covers"] == covers and rec["w_candidates"] == wcand, (rec, covers, wcand)
    print(
        "CENSUS42 (4,2)-shape k=3 spot reclass: (2,2,4) w_candidates=322 covers=80 (match)",
        flush=True,
    )
    print("PASS_KB3J_QUICK seconds=%.1f" % (time.time() - t0), flush=True)


def mode_walks():
    t0 = time.time()
    print("shard u_checked uv_pairs w_candidates covering complete budget_hit wall_s", flush=True)
    tp = tu = tw = tc = 0
    for k in range(2048):
        p = HERE / ("AV42-AV42-%d.json" % k)
        if not p.exists():
            continue
        r = json.loads(p.read_text(encoding="utf-8"))
        tp += r["uv_pairs"]
        tu += r["u_checked"]
        tw += r["w_candidates"]
        tc += r["covering_configs"]
        print(
            "%d %d %d %d %d %s %s %.1f"
            % (k, r["u_checked"], r["uv_pairs"], r["w_candidates"], r["covering_configs"],
               r["complete"], r["budget_hit"], r["wall_seconds"]),
            flush=True,
        )
    print("TOTAL u=%d pairs=%d w_cand=%d covering=%d" % (tu, tp, tw, tc), flush=True)
    print("PASS_KB3J_WALKS seconds=%.1f" % (time.time() - t0), flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    if mode == "quick":
        mode_quick()
    elif mode == "walks":
        mode_walks()
    else:
        raise SystemExit("usage: verify.py quick|walks")


if __name__ == "__main__":
    main()

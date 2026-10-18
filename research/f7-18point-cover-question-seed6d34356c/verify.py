"""Registered replay for the KB3e package (18-point cover question, F2^7).

Modes (each bounded; see VERIFY.json):

  quick    vendored byte pins, reduction and witness soundness controls,
           the squeeze/deficit bookkeeping for all six splits, and the
           recorded anchor receipts.            marker PASS_F7_18POINT_QUICK
  fourier  the per-character profile system and its no-vanishing sub-case.
           marker PASS_F7_18POINT_FOURIER
  rows     the pair-representation rows after the census floors.
           marker PASS_F7_18POINT_ROWS
  search   the bounded seeded construction search (a found cover is printed
           loudly; the search never asserts nonexistence).
           marker PASS_F7_18POINT_SEARCH

Everything is exact integer arithmetic (no floats).  The heavy PR 2773 census
anchors are recomputed by anchors.py (byte-vendored from PR 2870; resumable,
per-sub-shard receipts in ANCHOR-PROGRESS.json) and were recomputed in full
in-session -- see ANCHOR-REPRO.json.
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import cover18 as c18  # noqa: E402

SPLITS = [(12, 6), (11, 7), (10, 8), (9, 9)]
CONTROLS = [(11, 6), (10, 7)]
# Census floors: min pair-sum excess of k-sets in F2^6 (= E).  floor(6..9)=0
# (Sidon k-sets exist; PR 2773 receipts k7_budget0=34,122,816 and
# k9_budget0=17,776,640), floor(10)=3 and floor(11)=5 (the two heavy anchors
# reproduced here), floor(12)=3 (counting: C(12,2)=66 > 63).
FLOORS = {6: 0, 7: 0, 8: 0, 9: 0, 10: 3, 11: 5, 12: 3}
VENDOR_PINS = {
    "vendor/agent64_cover17.py": c18.VENDOR_PIN_COVER17,
    "vendor/agent64_search17.py": c18.VENDOR_PIN_SEARCH17,
    "anchors.py": "73d73a9b94539403448d7ff8c914c03711907f75c019c4ccb6843b32c259e8e7",
}


def check_pins():
    import hashlib

    for rel, want in VENDOR_PINS.items():
        got = hashlib.sha256((HERE / rel).read_bytes()).hexdigest()
        assert got == want, (rel, got, want)
        print("PIN %s sha256=%s" % (rel, got[:16]), flush=True)


def mode_quick():
    t0 = time.time()
    check_pins()
    # reduction + witness soundness (exhaustive at n = 3, sampled at n = 4/5)
    import itertools

    n3 = 0
    for r in range(9):
        for pts in itertools.combinations(range(8), r):
            A = [p for p in pts if not (p.bit_count() % 2)]
            B = [p for p in pts if p.bit_count() % 2]
            direct = c18.covers(pts, n=3)
            assert direct == all(c18.reduction_conditions(A, B, n=3)), pts
            n3 += 1
    print("CONTROL reduction exhaustive n=3 subsets=%d ok=true" % n3, flush=True)
    S = [0, 1, 2, 3, 4, 5, 6, 8, 16, 31]
    A = [p for p in S if not (p.bit_count() % 2)]
    B = [p for p in S if p.bit_count() % 2]
    assert c18.covers(S, n=5) and c18.witness_constraints_ok(A, B, 5)
    print("CONTROL n5 real cover split=(4,6) witness_ok=true", flush=True)
    assert 46 not in c18.rho_square_values(8)
    print("CONTROL rho_square_values(8) excludes 46 (the (12,6) no-vanishing value)", flush=True)
    # squeeze / deficit bookkeeping for every split
    for (s, t) in SPLITS + CONTROLS:
        rec = c18.squeeze_numbers(7, s, t)
        sides = rec["sides"]
        line = " ".join(
            "%s rem=%s max_char=%s allowed=%s deficit=%s"
            % (x["side"], x["parseval_remainder"], x["max_char"], x["max_allowed"], x["deficit"])
            for x in sides
        )
        print(
            "SQUEEZE (%d, %d) eo=%d opposite_parity=%s contradiction=%s | %s"
            % (s, t, rec["odd_excess"], rec["opposite_parity"], rec["contradiction"], line),
            flush=True,
        )
    rec = c18.squeeze_numbers(7, 11, 6)
    assert rec["parseval_remainder"] == 696 and rec["max_allowed"] == 504 and rec["deficit"] == 192
    print("CONTROL PR2870 obstruction reproduced: parseval=696 allowed=504 deficit=192", flush=True)
    # recorded anchor receipts (recomputed in full in-session; see ANCHOR-REPRO.json)
    prog = json.loads((HERE / "ANCHOR-PROGRESS.json").read_text(encoding="utf-8"))
    k10 = prog["modes"]["k10b3"]
    k11 = prog["modes"]["k11b4"]
    assert k10.get("complete") and k10["total_hist"] == {"3": 149990400}
    assert k11.get("complete") and k11["total_hist"] == {}
    print("ANCHORS receipts k10b3 count=149990400 total_hist={'3': 149990400} shards=%d" % len(k10["shards"]), flush=True)
    print("ANCHORS receipts k11b4 count=0 total_hist={} shards=%d" % len(k11["shards"]), flush=True)
    print("PASS_F7_18POINT_QUICK seconds=%.1f" % (time.time() - t0), flush=True)


def mode_fourier():
    t0 = time.time()
    expect = {(12, 6): True, (11, 7): True, (10, 8): True, (9, 9): True, (11, 6): False, (10, 7): False}
    for (s, t) in SPLITS + CONTROLS:
        rec = c18.fourier_profile_feasibility(7, s, t)
        print(
            "PROFILE18 (%d, %d) eo=%d feasible=%s capped=%s S_count=%d rem=(%d, %d)"
            % (
                s,
                t,
                rec["odd_excess"],
                rec["feasible"],
                rec.get("capped"),
                len(rec["feasible_S"]),
                rec["parseval_remainders"][0],
                rec["parseval_remainders"][1],
            ),
            flush=True,
        )
        assert rec["feasible"] is expect[(s, t)], (s, t, rec["reason"])
    for (s, t) in SPLITS:
        rec = c18.fourier_profile_feasibility(7, s, t, nonzero_both=True)
        tag = "PROVEN every (s,t) cover has a vanishing character off {0,1}" if not rec["feasible"] else "no constraint"
        print("NOVANISH (%d, %d) feasible=%s capped=%s -> %s" % (s, t, rec["feasible"], rec.get("capped"), tag), flush=True)
        if (s, t) in ((12, 6), (10, 8)):
            assert not rec["feasible"]
    print("PASS_F7_18POINT_FOURIER seconds=%.1f" % (time.time() - t0), flush=True)


def mode_rows():
    t0 = time.time()
    want = {(12, 6): 808, (11, 7): 501, (10, 8): 251, (9, 9): 196}
    for (s, t) in SPLITS:
        rows = c18.sharp_rows_fast(7, s, t, min_e_ex=FLOORS[s], min_b_ex=FLOORS[t])
        eb = sorted({(r["e_ex"], r["b_ex"]) for r in rows["rows"]})
        print(
            "ROWS18 (%d, %d) rows=%d distinct_eb=%d best=%d need=%d c_vals=%d floors=(e>=%d, b>=%d)"
            % (s, t, len(rows["rows"]), len(eb), rows["best"], rows["need"], len(rows["c_vals"]), FLOORS[s], FLOORS[t]),
            flush=True,
        )
        assert len(rows["rows"]) == want[(s, t)], (s, t, len(rows["rows"]))
        assert all(r["status"] == "sharp" for r in rows["rows"])
    # 17-point control: the recorded remainder (5,1),(6,0) must reappear
    rows = c18.surviving_rows_fast(7, 11, 6, min_e_ex=5, min_b_ex=0)
    got = sorted((r["e_ex"], r["b_ex"]) for r in rows["rows"])
    assert got == [(5, 1), (6, 0)], got
    rows = c18.surviving_rows_fast(7, 10, 7, min_e_ex=3, min_b_ex=0)
    assert rows["rows"] == []
    print("CONTROL 17-point rows reproduce: (11,6) remainder (5,1),(6,0); (10,7) empty after floor", flush=True)
    print("PASS_F7_18POINT_ROWS seconds=%.1f" % (time.time() - t0), flush=True)


def mode_search():
    t0 = time.time()
    res = c18.search_direct(k=18, restarts=200, seed=20261016, seconds=60.0)
    print(
        "SEARCH18 direct k=18 found=%s score=%s restarts=%s seconds=%s"
        % (res["found"], res["score"], res.get("restarts"), res["seconds"]),
        flush=True,
    )
    if res["found"]:
        print("SEARCH18 FOUND COVER S=%s" % res["S"], flush=True)
    for (s, t) in SPLITS:
        res = c18.search_split(s, t, restarts=60, seed=20261016 + s, seconds=25.0)
        print(
            "SEARCH18 (%d, %d) found=%s score=%s moves=%s seconds=%s"
            % (s, t, res["found"], res["score"], res.get("moves"), res["seconds"]),
            flush=True,
        )
        if res["found"]:
            print("SEARCH18 FOUND PAIR A=%s D=%s" % (res["A"], res["D"]), flush=True)
    res = c18.search_direct(k=19, restarts=60, seed=1919, seconds=15.0)
    print("SEARCH18 probe k=19 found=%s score=%s" % (res["found"], res["score"]), flush=True)
    found = 0
    for seed in range(5):
        res = c18.search_direct(k=20, restarts=3, seed=1000 + seed, seconds=8.0)
        found += 1 if res["found"] else 0
    print("CONTROL SEARCH k=20 covers found in %d/5 runs (non-vacuity)" % found, flush=True)
    assert found >= 1, "search machinery must find known-abundant 20-point covers"
    print("PASS_F7_18POINT_SEARCH seconds=%.1f" % (time.time() - t0), flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    fn = {
        "quick": mode_quick,
        "fourier": mode_fourier,
        "rows": mode_rows,
        "search": mode_search,
    }[mode]
    fn()


if __name__ == "__main__":
    main()

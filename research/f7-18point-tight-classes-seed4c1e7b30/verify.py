"""Registered replay for the KB3g package (tight-class resolution for the
18-point cover question for F2^7, set level; no words).

Modes (each bounded; see VERIFY.json):

  quick     byte pins, the exact Fourier contradiction for class (7,1), the
            rho classification numbers, the empty Sidon 5-pair enumeration,
            the m=4 brute-force control, the PR 2933 CLASS table incl. the
            (7,1)/(8,2) 32=32 TIGHT lines and L7 m=3 cases=6720, the
            PR 2870 OBSTRUCTION control (696/504/192), the F2^4 census, and
            the heavy-anchor receipt totals.
            marker PASS_TIGHT_QUICK
  novanish  reproduction of the load-bearing PR 2911 NOVANISH premise from
            the byte-vendored PR 2911 engine.
            marker PASS_TIGHT_NOVANISH
  rows      reproduction of the PR 2911 ROWS18 lines (808/501/251/196) and
            the 17-point row controls.
            marker PASS_TIGHT_ROWS
  classes   the tight-class decision receipts: class71 (0 pairs), class82
            (all equality configurations fail all three lines) and class60
            (complete D-side transversal walk), aggregated from
            TIGHT-PROGRESS.json / TIGHT-C60-*.json.
            marker PASS_TIGHT_CLASSES
  anchors   the two heavy PR 2773 anchor receipts (k10b3 = 149,990,400,
            k11b4 = 0/0).  Receipt validation of this package's own fresh
            empty-receipt walk (recorded in ANCHOR-REPRO.json), not a
            re-walk; run vendor/anchors.py or run_anchors_all-style loops to
            recompute.
            marker PASS_TIGHT_ANCHORS

Everything is exact integer arithmetic (no floats).
"""

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import tight  # noqa: E402

VENDOR_PINS = {
    "vendor/agent64_cover17.py": (
        "082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654"
    ),
    "vendor/agent64_search17.py": (
        "9eb1bf79ffb99b0efcdaf57916c493bc781abd4a0096d584dc6bc6ca294bf674"
    ),
    "anchors.py": (
        "73d73a9b94539403448d7ff8c914c03711907f75c019c4ccb6843b32c259e8e7"
    ),
    "vendor/cover18.py": (
        "24c6a2f4911dc2d5de76972eb5ae93dc4e66d8fa1e904443de6d0638e70c0a04"
    ),
    "vendor/vanish.py": (
        "6c605c54074f725321c5d770d538a652bf7727598a128270831f92fe7b9746d9"
    ),
}

SPLITS = [(12, 6), (11, 7), (10, 8), (9, 9)]


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_pins():
    for rel, want in VENDOR_PINS.items():
        got = sha256_file(HERE / rel)
        assert got == want, (rel, got, want)
        print("PIN %s sha256=%s" % (rel, got[:16]), flush=True)


def mode_quick():
    t0 = time.time()
    check_pins()
    fid = tight.fourier_71_identity()
    assert fid["m5_k5"]["contradiction"] is True
    assert (fid["m5_k5"]["need"], fid["m5_k5"]["lower_bound"]) == (175, 239)
    assert fid["m3_analogue_71"]["contradiction"] is False
    print(
        "FOURIER (7,1) need=%d lower=%d contradiction=%s"
        % (fid["m5_k5"]["need"], fid["m5_k5"]["lower_bound"], fid["m5_k5"]["contradiction"]),
        flush=True,
    )
    print(
        "FOURIER m4-analogue need=%d lower=%d contradiction=%s"
        % (
            fid["m3_analogue_71"]["need"],
            fid["m3_analogue_71"]["lower_bound"],
            fid["m3_analogue_71"]["contradiction"],
        ),
        flush=True,
    )
    rho = tight.rho_classification()
    print("RHO surviving=%s dead=%s" % (
        rho["surviving"],
        sorted(t["rho"] for t in rho["types"] if t["verdict"] == "DEAD"),
    ), flush=True)
    pairs = tight.class71_pairs()
    assert len(pairs) == 0, len(pairs)
    print("CLASS71 normalized Sidon 5-pairs=%d (class empty)" % len(pairs), flush=True)
    rec = tight.control_m4_bruteforce()
    assert rec["m4_class71_analogue"]["all_have_l7_structure"] in (True, None)
    assert rec["m4_class82_analogue"]["all_have_l7_structure"] in (True, None)
    print(
        "CONTROL m4 analogues: (7,1) covers=%d all_l7=%s; (8,2) covers=%d"
        % (
            rec["m4_class71_analogue"]["direct_covers"],
            rec["m4_class71_analogue"]["all_have_l7_structure"],
            rec["m4_class82_analogue"]["direct_covers"],
        ),
        flush=True,
    )
    # PR 2933 class table incl. the 32=32 TIGHT lines (vendored engine)
    import vanish

    for (s, t) in SPLITS:
        tab = vanish.class_table(s, t, m=6)
        for side in ("A_vanish", "D_vanish"):
            for c in tab[side]:
                print(
                    "CLASS (%d,%d) %s vanish_split=%s other=%s value=%d need=%d -> %s%s"
                    % (
                        s,
                        t,
                        side,
                        c["vanishing_split"],
                        c["other_split"],
                        c["floor_value"],
                        c["floor_need"],
                        c["verdict"],
                        " TIGHT" if c["tight"] else "",
                    ),
                    flush=True,
                )
        if not tab["vanishing_possible"]:
            print(
                "CLASS (%d,%d) NO VANISHING POSSIBLE (both sides odd): L2 blocks every character"
                % (s, t),
                flush=True,
            )
    res7 = vanish.check_tight_equality(3)
    assert res7["ok"], res7
    print("LEMMA tight-equality Sidon exhaustive m=3 cases=%d ok=true" % res7["checked"], flush=True)
    assert res7["checked"] == 6720, res7
    rec4 = vanish.census_f4()
    assert rec4["dead_classes_hit"] == [], rec4["dead_classes_hit"]
    print("CENSUS f2^4 covers=%d (dead classes hit: none)" % rec4["covers_total"], flush=True)
    assert rec4["covers_total"] == 41341, rec4["covers_total"]
    # PR 2870 OBSTRUCTION control (vendored PR 2911 engine)
    import cover18 as c18

    sq = c18.squeeze_numbers(7, 11, 6)
    assert (sq["parseval_remainder"], sq["max_allowed"], sq["deficit"]) == (696, 504, 192)
    print("CONTROL PR2870 obstruction reproduced: parseval=696 allowed=504 deficit=192", flush=True)
    # heavy-anchor receipts of this package's fresh empty-receipt walk
    prog = json.loads((HERE / "ANCHOR-PROGRESS.json").read_text(encoding="utf-8"))
    for mode, want_total in (("k10b3", {"3": 149990400}), ("k11b4", {})):
        mrec = prog["modes"][mode]
        assert mrec.get("complete"), mode
        assert mrec["total_hist"] == want_total, (mode, mrec["total_hist"])
        print(
            "ANCHORS receipts %s count=%d total_hist=%s shards=%d"
            % (mode, sum(mrec["total_hist"].values()), mrec["total_hist"], len(mrec["shards"])),
            flush=True,
        )
    print("PASS_TIGHT_QUICK seconds=%.1f" % (time.time() - t0), flush=True)


def mode_novanish():
    t0 = time.time()
    check_pins()
    import cover18 as c18

    for (s, t) in ((12, 6), (10, 8)):
        rec = c18.fourier_profile_feasibility(7, s, t, nonzero_both=True)
        print(
            "NOVANISH (%d, %d) feasible=%s capped=%s -> %s"
            % (
                s,
                t,
                rec["feasible"],
                rec.get("capped"),
                "PROVEN every (s,t) cover has a vanishing character off {0,1}"
                if not rec["feasible"]
                else "no constraint",
            ),
            flush=True,
        )
        assert rec["feasible"] is False, (s, t, rec)
    print("PASS_TIGHT_NOVANISH seconds=%.1f" % (time.time() - t0), flush=True)


def mode_rows():
    t0 = time.time()
    check_pins()
    import cover18 as c18

    FLOORS = {12: 3, 11: 5, 10: 3, 9: 0}
    want = {(12, 6): 808, (11, 7): 501, (10, 8): 251, (9, 9): 196}
    for (s, t) in SPLITS:
        rows = c18.sharp_rows_fast(7, s, t, min_e_ex=FLOORS[s], min_b_ex=0)
        eb = sorted({(r["e_ex"], r["b_ex"]) for r in rows["rows"]})
        print(
            "ROWS18 (%d, %d) rows=%d distinct_eb=%d best=%d need=%d c_vals=%d floors=(e>=%d, b>=%d)"
            % (
                s,
                t,
                len(rows["rows"]),
                len(eb),
                rows["best"],
                rows["need"],
                len(rows["c_vals"]),
                FLOORS[s],
                0,
            ),
            flush=True,
        )
        assert len(rows["rows"]) == want[(s, t)], (s, t, len(rows["rows"]))
    rows = c18.surviving_rows_fast(7, 11, 6, min_e_ex=5, min_b_ex=0)
    got = sorted((r["e_ex"], r["b_ex"]) for r in rows["rows"])
    assert got == [(5, 1), (6, 0)], got
    rows = c18.surviving_rows_fast(7, 10, 7, min_e_ex=3, min_b_ex=0)
    assert rows["rows"] == []
    print(
        "CONTROL 17-point rows reproduce: (11,6) remainder (5,1),(6,0); (10,7) empty after floor",
        flush=True,
    )
    print("PASS_TIGHT_ROWS seconds=%.1f" % (time.time() - t0), flush=True)


def mode_classes():
    t0 = time.time()
    check_pins()
    prog = json.loads((HERE / "TIGHT-PROGRESS.json").read_text(encoding="utf-8"))
    m71 = prog["modes"]["class71"]["shards"]["0"]
    assert m71.get("complete"), m71
    assert m71["normalized_pairs"] == 0 and m71["covering_pairs"] == 0, m71
    print(
        "CLASS71 normalized_pairs=%d covering_pairs=%d (PROVEN empty; Fourier need=175 < lower=239)"
        % (m71["normalized_pairs"], m71["covering_pairs"]),
        flush=True,
    )
    m82 = prog["modes"]["class82"]
    assert m82.get("complete"), "class82 incomplete"
    tot = m82["total"]
    assert tot["covering_configs"] == 0, tot
    print(
        "CLASS82 normalized_sidon_pairs=%d noninv=%d checked=%d covering=%d fail_hist=%s"
        % (
            tot["normalized_sidon_pairs"],
            tot["non_1_invariant_pairs"],
            tot["checked"],
            tot["covering_configs"],
            tot["fail_hist"],
        ),
        flush=True,
    )
    m60 = prog["modes"]["class60"]
    assert m60.get("complete"), "class60 incomplete"
    tot = m60["total"]
    assert tot["covering_triples"] == 0, tot
    print(
        "CLASS60 d_checked=%d d_with_transversals=%d transversals=%d covering_triples=%d"
        % (
            tot["d_checked"],
            tot["d_with_transversals"],
            tot["transversals_total"],
            tot["covering_triples"],
        ),
        flush=True,
    )
    for (s, t) in ((11, 7), (9, 9)):
        rec = tight.identity_odd_sides(s, t)
        print(
            "IDENTITY (%d,%d) excess=%d sum_rho2_min=%d sum_rho2_max=%d contradiction=%s"
            % (
                s,
                t,
                rec["excess"],
                rec["sum_rho2_min"],
                rec["sum_rho2_max"],
                rec["contradiction"],
            ),
            flush=True,
        )
    print("PASS_TIGHT_CLASSES seconds=%.1f" % (time.time() - t0), flush=True)


def mode_anchors():
    t0 = time.time()
    check_pins()
    prog = json.loads((HERE / "ANCHOR-PROGRESS.json").read_text(encoding="utf-8"))
    for mode, want_total in (("k10b3", {"3": 149990400}), ("k11b4", {})):
        mrec = prog["modes"][mode]
        assert mrec.get("complete"), mode
        assert mrec["total_hist"] == want_total, (mode, mrec["total_hist"])
        assert len(mrec["shards"]) == 62, (mode, len(mrec["shards"]))
        print(
            "ANCHORS %s count=%d total_hist=%s shards=%d (receipt validation of the fresh walk)"
            % (mode, sum(mrec["total_hist"].values()), mrec["total_hist"], len(mrec["shards"])),
            flush=True,
        )
    print("PASS_TIGHT_ANCHORS seconds=%.1f" % (time.time() - t0), flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    if mode == "quick":
        mode_quick()
    elif mode == "novanish":
        mode_novanish()
    elif mode == "rows":
        mode_rows()
    elif mode == "classes":
        mode_classes()
    elif mode == "anchors":
        mode_anchors()
    else:
        raise SystemExit("usage: verify.py quick|novanish|rows|classes|anchors")


if __name__ == "__main__":
    main()

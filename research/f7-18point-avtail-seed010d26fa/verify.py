"""Registered replay for the KB3h package (the (12,6) A-vanish tail classes
(5,1)/(4,2)/(3,3) of the 18-point cover question for F2^7, set level; no
words).

Modes (each bounded; see VERIFY.json):

  quick     byte pins, the PR 2961 FOURIER (7,1) anchor (need=175
            lower=239), the rho classification numbers, the PR 2933
            CLASSIFY lines incl. the 32=32 TIGHT cases=6720 and the
            PR 2870 OBSTRUCTION anchor (696/504/192).
            marker PASS_AVTAIL_QUICK
  novanish  the PR 2911 NOVANISH premise from the byte-vendored engine.
            marker PASS_AVTAIL_NOVANISH
  rows      the PR 2911 ROWS18 anchor (808/501/251/196) and the 17-point
            row controls.
            marker PASS_AVTAIL_ROWS
  anchors   receipt validation of this package's OWN fresh empty-receipt
            re-walks: CLASS71 (0 pairs), CLASS82 (28,815,360 checked,
            covering=0), CLASS60 (169,911 D walked, 0 with transversals).
            The walks themselves: run_avtail.py class71/class82/class60.
            marker PASS_AVTAIL_ANCHORS
  m4        the m=4 analogue positive control: direct census vs machinery
            per D-split, with semantic failure controls (line mutants).
            marker PASS_AVTAIL_M4
  av51      the class (5,1) decision receipts (run_avtail.py av51).
            marker PASS_AVTAIL_AV51

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
import avtail  # noqa: E402

VENDOR_PINS = {
    "vendor/tight.py": (
        "14670ef2d3df9e4ecc9e1db962f4e8cb77545d1c889144352760c1fd14e2273b"
    ),
    "vendor/cover18.py": (
        "24c6a2f4911dc2d5de76972eb5ae93dc4e66d8fa1e904443de6d0638e70c0a04"
    ),
    "vendor/vanish.py": (
        "6c605c54074f725321c5d770d538a652bf7727598a128270831f92fe7b9746d9"
    ),
    "vendor/agent64_cover17.py": (
        "082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654"
    ),
    "vendor/agent64_search17.py": (
        "9eb1bf79ffb99b0efcdaf57916c493bc781abd4a0096d584dc6bc6ca294bf674"
    ),
    "vendor/anchors.py": (
        "73d73a9b94539403448d7ff8c914c03711907f75c019c4ccb6843b32c259e8e7"
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
    assert (fid["m5_k5"]["need"], fid["m5_k5"]["lower_bound"]) == (175, 239)
    assert fid["m5_k5"]["contradiction"] is True
    print(
        "FOURIER (7,1) need=%d lower=%d contradiction=%s"
        % (fid["m5_k5"]["need"], fid["m5_k5"]["lower_bound"], fid["m5_k5"]["contradiction"]),
        flush=True,
    )
    rho = tight.rho_classification()
    print("RHO surviving=%s dead=%s" % (
        rho["surviving"],
        sorted(t["rho"] for t in rho["types"] if t["verdict"] == "DEAD"),
    ), flush=True)
    import vanish

    tight_seen = 0
    for (s, t) in SPLITS:
        tab = vanish.class_table(s, t, m=6)
        for side in ("A_vanish", "D_vanish"):
            for c in tab[side]:
                if c["tight"]:
                    tight_seen += 1
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
    assert tight_seen == 2, tight_seen
    res7 = vanish.check_tight_equality(3)
    assert res7["ok"], res7
    assert res7["checked"] == 6720, res7
    print("LEMMA tight-equality Sidon exhaustive m=3 cases=%d ok=true" % res7["checked"], flush=True)
    import cover18 as c18

    sq = c18.squeeze_numbers(7, 11, 6)
    assert (sq["parseval_remainder"], sq["max_allowed"], sq["deficit"]) == (696, 504, 192)
    print("ANCHOR PR2870 OBSTRUCTION parseval=696 allowed=504 deficit=192", flush=True)
    print("PASS_AVTAIL_QUICK seconds=%.1f" % (time.time() - t0), flush=True)


def mode_novanish():
    t0 = time.time()
    check_pins()
    import cover18 as c18

    for (s, t) in ((12, 6), (10, 8)):
        rec = c18.fourier_profile_feasibility(7, s, t, nonzero_both=True)
        print(
            "NOVANISH (%d, %d) feasible=%s -> %s"
            % (
                s,
                t,
                rec["feasible"],
                "PROVEN every (s,t) cover has a vanishing character off {0,1}"
                if not rec["feasible"]
                else "no constraint",
            ),
            flush=True,
        )
        assert rec["feasible"] is False, (s, t, rec)
    print("PASS_AVTAIL_NOVANISH seconds=%.1f" % (time.time() - t0), flush=True)


def mode_rows():
    t0 = time.time()
    check_pins()
    import cover18 as c18

    FLOORS = {12: 3, 11: 5, 10: 3, 9: 0}
    want = {(12, 6): 808, (11, 7): 501, (10, 8): 251, (9, 9): 196}
    for (s, t) in SPLITS:
        rows = c18.sharp_rows_fast(7, s, t, min_e_ex=FLOORS[s], min_b_ex=0)
        print(
            "ROWS18 (%d, %d) rows=%d best=%d need=%d"
            % (s, t, len(rows["rows"]), rows["best"], rows["need"]),
            flush=True,
        )
        assert len(rows["rows"]) == want[(s, t)], (s, t, len(rows["rows"]))
    rows = c18.surviving_rows_fast(7, 11, 6, min_e_ex=5, min_b_ex=0)
    got = sorted((r["e_ex"], r["b_ex"]) for r in rows["rows"])
    assert got == [(5, 1), (6, 0)], got
    rows = c18.surviving_rows_fast(7, 10, 7, min_e_ex=3, min_b_ex=0)
    assert rows["rows"] == []
    print("CONTROL 17-point rows reproduce: (11,6) remainder (5,1),(6,0); (10,7) empty", flush=True)
    print("PASS_AVTAIL_ROWS seconds=%.1f" % (time.time() - t0), flush=True)


def mode_anchors():
    t0 = time.time()
    check_pins()
    prog = json.loads((HERE / "AVTAIL-PROGRESS.json").read_text(encoding="utf-8"))
    m71 = prog["modes"]["class71"]["shards"]["0"]
    assert m71.get("complete"), m71
    assert m71["normalized_pairs"] == 0 and m71["covering_pairs"] == 0, m71
    print(
        "ANCHOR CLASS71 normalized_pairs=%d covering_pairs=%d"
        % (m71["normalized_pairs"], m71["covering_pairs"]),
        flush=True,
    )
    m82 = prog["modes"]["class82"]
    assert m82.get("complete"), "class82 incomplete"
    tot = m82["total"]
    assert tot["checked"] == 28815360, tot
    assert tot["covering_configs"] == 0, tot
    print(
        "ANCHOR CLASS82 normalized_sidon_pairs=%d checked=%d covering=%d fail_hist=%s"
        % (
            tot["normalized_sidon_pairs"],
            tot["checked"],
            tot["covering_configs"],
            tot["fail_hist"],
        ),
        flush=True,
    )
    m60 = prog["modes"]["class60"]
    assert m60.get("complete"), "class60 incomplete"
    tot = m60["total"]
    assert tot["d_checked"] == 169911, tot
    assert tot["d_with_transversals"] == 0 and tot["covering_triples"] == 0, tot
    print(
        "ANCHOR CLASS60 d_checked=%d d_with_transversals=%d covering_triples=%d"
        % (tot["d_checked"], tot["d_with_transversals"], tot["covering_triples"]),
        flush=True,
    )
    print("PASS_AVTAIL_ANCHORS seconds=%.1f" % (time.time() - t0), flush=True)


def mode_m4():
    t0 = time.time()
    check_pins()
    rec = avtail.control_m4()
    load_bearing = False
    nonempty = 0
    for k in sorted(rec):
        r = rec[k]
        print(
            "M4 %s direct=%d direct_l3=%d machinery=%d mutant_drop_a=%d mutant_drop_d=%d agreement=%s"
            % (
                k,
                r["direct_covers"],
                r["direct_l3_covers"],
                r["machinery_covers"],
                r["mutant_drop_a"],
                r["mutant_drop_d"],
                r["agreement"],
            ),
            flush=True,
        )
        assert r["agreement"], (k, r)
        if r["direct_covers"] > 0:
            nonempty += 1
        if r["mutant_drop_a"] != r["machinery_covers"] or r["mutant_drop_d"] != r["machinery_covers"]:
            load_bearing = True
    assert load_bearing, "line-checker mutants must change at least one census count"
    assert nonempty >= 1, "positive control needs a cover-bearing class"
    print("M4 semantic failure controls load-bearing=true positive_classes=%d" % nonempty, flush=True)
    print("PASS_AVTAIL_M4 seconds=%.1f" % (time.time() - t0), flush=True)


def mode_av51():
    t0 = time.time()
    check_pins()
    prog = json.loads((HERE / "AVTAIL-PROGRESS.json").read_text(encoding="utf-8"))
    m = prog["modes"]["av51"]
    assert m.get("complete"), "av51 incomplete"
    tot = m["total"]
    print(
        "AV51 u_checked=%d uv_pairs=%d w_candidates=%d covering_configs=%d fail_hist=%s"
        % (
            tot["u_checked"],
            tot["uv_pairs"],
            tot["w_candidates"],
            tot["covering_configs"],
            tot["fail_hist"],
        ),
        flush=True,
    )
    print("AV51 pairs_by_sumset_size=%s" % json.dumps(tot.get("uv_pairs_by_sumset_size", {}), sort_keys=True), flush=True)
    verdict = "PROVEN empty" if tot["covering_configs"] == 0 else "WITNESS FOUND - class realized"
    print("AV51 class (12,6) A-vanish (5,1): %s" % verdict, flush=True)
    assert tot["u_checked"] == 169911, tot
    print("PASS_AVTAIL_AV51 seconds=%.1f" % (time.time() - t0), flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    modes = {
        "quick": mode_quick,
        "novanish": mode_novanish,
        "rows": mode_rows,
        "anchors": mode_anchors,
        "m4": mode_m4,
        "av51": mode_av51,
    }
    if mode not in modes:
        raise SystemExit("usage: verify.py quick|novanish|rows|anchors|m4|av51")
    modes[mode]()


if __name__ == "__main__":
    main()

"""Registered replay for the KB3f package (vanishing-character classification
for the 18-point cover question, F2^7).

Modes (each bounded; see VERIFY.json):

  quick     vendored byte pins, the half-decomposition lemma exhaustive at
            n = 3, the class tables for all four splits, the F2^4 census
            soundness, the SQUEEZE reproduction of the PR 2911 split table,
            and the heavy-anchor receipt totals.
            marker PASS_F7_18POINT_QUICK
  novanish  reproduction of the load-bearing PR 2911 NOVANISH premise
            (any (12,6) or (10,8) cover has a vanishing character off the
            all-ones hyperplane) from the byte-vendored PR 2911 engine.
            marker PASS_F7_18POINT_NOVANISH
  classify  the ground-truth vanishing census: all covers of F2^4 (complete)
            and all 10-point covers of F2^5 (complete C(32,10) enumeration,
            resumable per shard in CENSUS-PROGRESS.json; one invocation runs
            shards until its time budget, re-invoke to continue).
            marker PASS_F7_18POINT_CLASSIFY
  search    the class-restricted bounded searches (a found pair is printed
            loudly; a failed bounded search is never an exclusion) plus a
            non-vacuity control on F2^5.
            marker PASS_F7_18POINT_SEARCH

Everything is exact integer arithmetic (no floats).
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import vanish  # noqa: E402

VENDOR_PINS = {
    "vendor/agent64_cover17.py": (
        "082bc838134cba9754368cff894d53c729467a689b4cafee8374423688d93654"
    ),
    "vendor/agent64_search17.py": (
        "9eb1bf79ffb99b0efcdaf57916c493bc781abd4a0096d584dc6bc6ca294bf674"
    ),
    "anchors.py": "73d73a9b94539403448d7ff8c914c03711907f75c019c4ccb6843b32c259e8e7",
    "vendor/cover18.py": (
        "24c6a2f4911dc2d5de76972eb5ae93dc4e66d8fa1e904443de6d0638e70c0a04"
    ),
}

SPLITS = [(12, 6), (11, 7), (10, 8), (9, 9)]


def check_pins():
    for rel, want in VENDOR_PINS.items():
        got = vanish.sha256_file(HERE / rel)
        assert got == want, (rel, got, want)
        print("PIN %s sha256=%s" % (rel, got[:16]), flush=True)


def mode_quick():
    t0 = time.time()
    check_pins()
    res = vanish.check_half_decomposition(3, exhaustive=True)
    assert res["ok"], res
    print("LEMMA half-decomposition exhaustive m=3 pairs=%d ok=true" % res["pairs"], flush=True)
    res5 = vanish.check_multi_vanishing(3)
    assert res5["ok"], res5
    print("LEMMA multi-vanishing grid exhaustive m=3 pairs=%d ok=true" % res5["checked"], flush=True)
    res7 = vanish.check_tight_equality(3)
    assert res7["ok"], res7
    print("LEMMA tight-equality Sidon exhaustive m=3 cases=%d ok=true" % res7["checked"], flush=True)
    for (s, t) in SPLITS:
        tab = vanish.class_table(s, t, m=6)
        for side in ("A_vanish", "D_vanish"):
            for c in tab[side]:
                print(
                    "CLASS (%d,%d) %s vanish_split=%s other=%s floors=%s value=%d need=%d -> %s%s"
                    % (
                        s,
                        t,
                        side,
                        c["vanishing_split"],
                        c["other_split"],
                        c["floors"],
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
    rec = vanish.census_f4()
    assert rec["dead_classes_hit"] == [], rec["dead_classes_hit"]
    print(
        "CENSUS f2^4 covers=%d (dead classes hit: none) agg=%s"
        % (rec["covers_total"], rec["agg"]),
        flush=True,
    )
    # SQUEEZE reproduction of the PR 2911 split table (byte-vendored engine).
    import cover18 as c18

    for (s, t) in SPLITS + [(11, 6)]:
        sq = c18.squeeze_numbers(7, s, t)
        sides = sq["sides"]
        line = " ".join(
            "%s rem=%s max_char=%s allowed=%s deficit=%s"
            % (
                x["side"],
                x["parseval_remainder"],
                x["max_char"],
                x["max_allowed"],
                x["deficit"],
            )
            for x in sides
        )
        print(
            "SQUEEZE (%d, %d) eo=%d opposite_parity=%s contradiction=%s | %s"
            % (s, t, sq["odd_excess"], sq["opposite_parity"], sq["contradiction"], line),
            flush=True,
        )
    sq = c18.squeeze_numbers(7, 11, 6)
    assert (sq["parseval_remainder"], sq["max_allowed"], sq["deficit"]) == (696, 504, 192)
    print("CONTROL PR2870 obstruction reproduced: parseval=696 allowed=504 deficit=192", flush=True)
    # heavy-anchor receipts (this package's own fresh-receipt re-walk)
    prog = json.loads((HERE / "ANCHOR-PROGRESS.json").read_text(encoding="utf-8"))
    for mode, want_total in (("k10b3", {"3": 149990400}), ("k11b4", {})):
        mrec = prog["modes"][mode]
        assert mrec.get("complete"), mode
        assert mrec["total_hist"] == want_total, (mode, mrec["total_hist"])
        print(
            "ANCHORS receipts %s count=%d total_hist=%s shards=%d (re-walked from empty receipts)"
            % (mode, sum(mrec["total_hist"].values()), mrec["total_hist"], len(mrec["shards"])),
            flush=True,
        )
    print("PASS_F7_18POINT_QUICK seconds=%.1f" % (time.time() - t0), flush=True)


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
    print("PASS_F7_18POINT_NOVANISH seconds=%.1f" % (time.time() - t0), flush=True)


def mode_classify(budget=540.0):
    t0 = time.time()
    rec4 = vanish.census_f4()
    assert rec4["dead_classes_hit"] == []
    print(
        "CENSUS f2^4 covers=%d agg=%s class_agg=%s"
        % (rec4["covers_total"], rec4["agg"], rec4["class_agg"]),
        flush=True,
    )
    prog_path = HERE / "CENSUS-PROGRESS.json"
    prog = {"shards": {}}
    if prog_path.exists():
        prog = json.loads(prog_path.read_text(encoding="utf-8"))
    shards = 32
    for shard in range(shards):
        key = str(shard)
        if key in prog["shards"]:
            continue
        sres = vanish.census_f5(shard=shard, shards=shards, keep_covers=3)
        assert sres["dead_classes_hit"] == [], (shard, sres["dead_classes_hit"][:3])
        prog["shards"][key] = {
            "combos": sres["combos"],
            "covers_total": sres["covers_total"],
            "agg": sres["agg"],
            "class_agg": sres["class_agg"],
            "covers": sres["covers"],
        }
        prog_path.write_text(json.dumps(prog, indent=2, sort_keys=True), encoding="utf-8")
        print(
            "CENSUS f2^5 shard=%d/%d combos=%d covers=%d"
            % (shard, shards, sres["combos"], sres["covers_total"]),
            flush=True,
        )
        if time.time() - t0 > budget:
            print(
                "RECEIPT classify checkpoint shards=%d/%d" % (len(prog["shards"]), shards),
                flush=True,
            )
            return
    # full aggregation over all shards
    total_covers = sum(r["covers_total"] for r in prog["shards"].values())
    total_combos = sum(r["combos"] for r in prog["shards"].values())
    agg = {}
    class_agg = {}
    for r in prog["shards"].values():
        for item, cnt in r["agg"]:
            agg[item] = agg.get(item, 0) + cnt
        for item, cnt in r["class_agg"]:
            class_agg[item] = class_agg.get(item, 0) + cnt
    prog["complete"] = True
    prog["total_combos"] = total_combos
    prog["total_covers"] = total_covers
    prog_path.write_text(json.dumps(prog, indent=2, sort_keys=True), encoding="utf-8")
    print("CENSUS f2^5 combos=%d covers=%d" % (total_combos, total_covers), flush=True)
    for item in sorted(agg):
        print("CENSUS-SPLIT %s count=%d" % (item, agg[item]), flush=True)
    for item in sorted(class_agg):
        print("CENSUS-CLASS %s count=%d" % (item, class_agg[item]), flush=True)
    # PR 2773's n5 control counts covers through {0} (its engine fixes 0 in
    # every draw); shard 0 of this un-normalized enumeration is exactly the
    # 0-containing slice, and 99,200 * 32 / 10 = 317,440 is the full count.
    covers_through_0 = prog["shards"]["0"]["covers_total"]
    assert covers_through_0 == 99200, covers_through_0
    assert total_covers * 10 == covers_through_0 * 32, (total_covers, covers_through_0)
    print(
        "CONTROL PR2773 n5 control value reproduced: %d ten-point covers through {0}"
        " (all translations %d = %d * 32 / 10)"
        % (covers_through_0, total_covers, covers_through_0),
        flush=True,
    )
    print("PASS_F7_18POINT_CLASSIFY seconds=%.1f" % (time.time() - t0), flush=True)


def mode_search():
    t0 = time.time()
    jobs = []
    for (s, t) in SPLITS:
        tab = vanish.class_table(s, t, m=6)
        for c in tab["A_vanish"]:
            if c["verdict"] == "dead":
                continue
            jobs.append((s, t, "A_vanish", c["other_split"]))
        for c in tab["D_vanish"]:
            if c["verdict"] == "dead":
                continue
            jobs.append((s, t, "D_vanish", c["other_split"]))
    found_any = False
    for idx, (s, t, side, other) in enumerate(jobs):
        res = vanish.search_class(
            s, t, side=side, other_split=other, restarts=30, seed=7000 + idx, seconds=25.0
        )
        print(
            "SEARCH-CLASS (%d,%d) %s other=%s found=%s score=%s/%d moves=%s"
            % (s, t, side, other, res["found"], res["score"], 128, res.get("moves")),
            flush=True,
        )
        if res["found"]:
            found_any = True
            print("SEARCH-CLASS FOUND A=%s D=%s" % (res["A"], res["D"]), flush=True)
    # non-vacuity: the same machinery finds a real (4,6) cover of F2^4 = E of
    # F2^5 fast (the (A, D) reduction of an F2^n cover lives in E = F2^(n-1))
    res = vanish.search_free(4, 6, restarts=40, seed=5, seconds=20.0, m=4)
    print(
        "CONTROL search_free m=4 (4,6) found=%s score=%s/%d (non-vacuity)"
        % (res["found"], res["score"], 32),
        flush=True,
    )
    if res["found"]:
        print("CONTROL search_free cover A=%s D=%s" % (res["A"], res["D"]), flush=True)
    assert res["found"], "class machinery must find known 10-point covers of F2^5"
    # class-restricted non-vacuity: the census proves this class nonempty
    res = vanish.search_class(4, 6, side="A_vanish", other_split=(2, 4), restarts=40, seed=6, seconds=20.0, m=4)
    print(
        "CONTROL search_class m=4 (4,6) A_vanish other=(2,4) found=%s score=%s/%d"
        % (res["found"], res["score"], 32),
        flush=True,
    )
    assert res["found"], "class search must find a cover in a census-nonempty class"
    print("PASS_F7_18POINT_SEARCH seconds=%.1f found_18=%s" % (time.time() - t0, found_any), flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    mode = sys.argv[1] if len(sys.argv) > 1 else "quick"
    if mode == "quick":
        mode_quick()
    elif mode == "novanish":
        mode_novanish()
    elif mode == "classify":
        budget = 540.0
        if "--seconds" in sys.argv:
            budget = float(sys.argv[sys.argv.index("--seconds") + 1])
        mode_classify(budget)
    elif mode == "search":
        mode_search()
    else:
        raise SystemExit("usage: verify.py quick|novanish|classify|search [--seconds S]")


if __name__ == "__main__":
    main()

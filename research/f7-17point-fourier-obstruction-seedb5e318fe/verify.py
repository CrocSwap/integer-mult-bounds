"""Reproduction and verification for the KB3d Fourier obstruction package.

Quick mode (< 600 s): vendored PR 2773 engine byte pins, the exact (11,6) and
(6,11) obstructions (Parseval remainder 696 > allowed 504, deficit 192), the
non-vacuity control on the other four 17-point splits, the real 10-point cover
of F2^5 as positive control, the recorded row remainder (5,1),(6,0) reproduced
from the vendored engine, the vendored-engine small-group control against the
PR 2773 receipt values, and the recorded predecessor anchor values from
ANCHOR-REPRO.json (in-session reproductions; see the README anchors table).

Expected marker: PASS_FOURIER_VERIFY ...
"""

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import fourier17
import agent64_cover17
import agent64_search17

# The canonical recorded predecessor anchors (PR 2773 / PR 2542 / PR 2634).
EXPECTED_ANCHORS = {
    "k10_budget3": 149990400,
    "k11_level3": 0,
    "k11_level4": 0,
    "l18_nodes": 15775992,
    "l18_cycles": 312064,
    "l18_universal": 0,
    "tier_n5_l10": [945, 31],
    "tier_n6_l12": [10395, 49],
    "tier_n6_l14": [945945, 59],
}


def main():
    t0 = time.time()

    # 1. vendored PR 2773 engine byte pins (credit: Aaron Wang, PR 2773).
    for name, pin in (
        ("agent64_cover17.py", fourier17.VENDOR_PIN_COVER17),
        ("agent64_search17.py", fourier17.VENDOR_PIN_SEARCH17),
    ):
        digest = hashlib.sha256((HERE / "vendor" / name).read_bytes()).hexdigest()
        assert digest == pin, (name, digest)
        print(f"PIN vendor/{name} sha256={digest[:16]}", flush=True)

    # 2. the exact obstructions, both parity orders.
    for split in ((11, 6), (6, 11)):
        res = fourier17.obstruction(7, *split)
        assert res["contradiction"] is True, (split, res)
        assert res["odd_excess"] == 2, res
        assert res["parseval_remainder"] == 696, res
        assert res["max_allowed"] == 504, res
        assert res["deficit"] == 192, res
        assert res["character_values"] == [-2, 0, 2], res
        print(
            f"OBSTRUCTION {split} odd_excess={res['odd_excess']}"
            f" bounded={res['bounded_side']} parseval={res['parseval_remainder']}"
            f" allowed={res['max_allowed']} deficit={res['deficit']}"
            f" contradiction=True",
            flush=True,
        )

    # 3. non-vacuity: the other four 17-point splits do not fire here
    #    (they are excluded by PR 2542 rows / PR 2773 census floor instead).
    for split in ((10, 7), (7, 10), (9, 8), (8, 9)):
        res = fourier17.obstruction(7, *split)
        assert res["contradiction"] is False, (split, res)
    print(
        "CONTROL other 17-point splits (10,7),(7,10),(9,8),(8,9):"
        " no Fourier contradiction",
        flush=True,
    )

    # 4. positive control: a real 10-point cover of F2^5 passes everything.
    cover = [0, 1, 2, 3, 4, 5, 6, 8, 16, 31]
    a = [x for x in cover if x.bit_count() % 2 == 0]
    b = [x for x in cover if x.bit_count() % 2 == 1]
    assert fourier17.sumset_mask(cover, 5) == (1 << 32) - 1
    assert fourier17.split_of(cover, 5) == (4, 6)
    assert fourier17.ft_convolution_ok(a, b, 5)
    info = fourier17.cross_info(a, b, 5)
    assert info["covers_odd"] and info["odd_excess"] == 8, info
    assert fourier17.obstruction(5, 4, 6)["contradiction"] is False
    print("CONTROL real 10-point cover of F2^5 passes every check", flush=True)

    # 5. the recorded remainder rows, reproduced from the vendored engine.
    rows = agent64_cover17.sharp_rows(7, 11, 6)["rows"]
    survivors = sorted((r["e_ex"], r["b_ex"]) for r in rows if r["e_ex"] >= 5)
    assert survivors == [(5, 1), (6, 0)], survivors
    assert all((r["shared"], r["c"]) == (1, 1) for r in rows)
    mirror = agent64_cover17.sharp_rows(7, 6, 11)["rows"]
    m_surv = sorted((r["e_ex"], r["b_ex"]) for r in mirror if r["e_ex"] >= 5)
    assert m_surv == [(5, 1), (6, 0)], m_surv
    print(
        "REPRO rows remainder (5,1),(6,0) shared=1 c=1"
        " (both orders; census floor e_ex >= 5)",
        flush=True,
    )

    # 6. vendored-engine small-group control (PR 2773 receipt values).
    sub = [x for x in agent64_search17.EVEN if x < 32]
    counts = []
    for k in (4, 5, 6):
        n, _ = agent64_search17.count_sets(sub, k, 0, fixed=(0,))
        counts.append(n)
    assert counts == [420, 840, 168], counts
    print(f"CONTROL vendored engine small-group 420/840/168 ok {counts}", flush=True)

    # 7. recorded predecessor anchors (in-session reproductions, ANCHOR-REPRO).
    record = json.loads((HERE / "ANCHOR-REPRO.json").read_text(encoding="utf-8"))
    assert record["recorded_anchor_values"] == EXPECTED_ANCHORS, record
    print("ANCHORS " + json.dumps(EXPECTED_ANCHORS, sort_keys=True), flush=True)
    print(record["status"], flush=True)

    print(f"PASS_FOURIER_VERIFY seconds={time.time() - t0:.1f}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

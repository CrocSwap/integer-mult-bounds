"""Reproduction and verification for the 17-point cover audit.

Quick mode (< 600 s): vendored-engine byte pin, the pinned n = 5 / n = 6
tier reproductions, the full PR 2542 length-18 census re-run against the
vendored engine, the sharp 17-point row table with the min-excess census
filter, the exact n = 5 set-level controls and the receipt consistency
checks.  `--full` additionally re-runs the four load-bearing zero-count
census shards (~17 min) and compares them with SIDON-RECEIPT.json.

Expected marker: PASS_17POINT_VERIFY ...
"""

import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "vendor"))

import cover17
import pr2542_engine
import search17


def main():
    t0 = time.time()
    full = "--full" in sys.argv

    # 1. vendored engine byte pin (credit: PR 2542, Aaron Wang)
    digest = hashlib.sha256((HERE / "vendor" / "pr2542_engine.py").read_bytes())
    assert digest.hexdigest() == cover17.VENDOR_PIN_PR2542, digest.hexdigest()
    print(f"PIN vendor/pr2542_engine.py sha256={digest.hexdigest()[:16]}", flush=True)

    # 2. pinned tier reproductions (research/universal-connector-six-source)
    pinned = json.loads(
        (ROOT / "research" / "universal-connector-six-source" / "EXPECTED.json").read_text(
            encoding="utf-8"
        )
    )
    by_key = {(c["sources"], c["length"]): c for c in pinned["censuses"]}
    for n, L in ((5, 10), (6, 12), (6, 14)):
        hist, sha, words = pr2542_engine.census_words(n, L)
        exp = by_key[(n, L)]
        assert words == exp["words"], (n, L, words)
        assert max(k for k, v in hist.items() if v) == exp["max_coverage"], (n, L)
        assert sha == exp["records_sha256"], (n, L, sha)
        print(
            f"REPRO n={n} L={L} words={words} max={exp['max_coverage']}"
            f" sha={sha[:16]}",
            flush=True,
        )

    # 3. PR 2542's decisive length-18 census, re-run shard by shard against
    #    the vendored engine (shard nodes sum with the +10 shard overhead).
    tot = {"nodes": 0, "leaves": 0, "hits": 0}
    for pref in pr2542_engine.rg_prefixes(7, 3):
        rr = pr2542_engine.cyclic_census(7, 18, budget=9, simple=True, prefix=pref)
        tot["nodes"] += rr["nodes"]
        tot["leaves"] += rr["leaves"]
        tot["hits"] += rr["hits"]
    assert tot == {"nodes": 15775992, "leaves": 312064, "hits": 0}, tot
    print(
        f"REPRO PR2542 L18 nodes={tot['nodes']} cycles={tot['leaves']}"
        f" universal_words={tot['hits']}",
        flush=True,
    )

    # 4. sharp 17-point row table with the min-excess census filter
    #    (10-set floor e_ex >= 3; 11-set floor e_ex >= 5, both raw-domain
    #    complete by GL(6,2) transitivity)
    table = {}
    for s, t in ((9, 8), (8, 9), (10, 7), (7, 10), (11, 6), (6, 11)):
        sharp = cover17.sharp_rows(7, s, t)
        if (s, t) in ((10, 7), (7, 10)):
            filt = cover17.surviving_rows(7, s, t, 3, 0) if s >= t else cover17.surviving_rows(7, s, t, 0, 3)
        else:
            filt = cover17.surviving_rows(7, s, t, 5, 0) if s >= t else cover17.surviving_rows(7, s, t, 0, 5)
        table[f"{s}_{t}"] = {
            "sharp_feasible": sharp["feasible"],
            "rows_after_min_excess": len(filt["rows"]),
        }
    assert table["9_8"]["sharp_feasible"] is False
    assert table["8_9"]["sharp_feasible"] is False
    assert table["10_7"]["rows_after_min_excess"] == 0
    assert table["7_10"]["rows_after_min_excess"] == 0
    assert table["11_6"]["rows_after_min_excess"] == 2
    assert table["6_11"]["rows_after_min_excess"] == 2
    print("ROWS17 " + json.dumps(table, sort_keys=True), flush=True)

    # 5. exact n = 5 set-level controls (community facts)
    covers9, best9 = cover17.brute_force_set_census(5, 9)
    covers10, best10 = cover17.brute_force_set_census(5, 10)
    assert (covers9, best9) == (0, 29), (covers9, best9)
    assert (covers10, best10) == (99200, 32), (covers10, best10)
    print(
        f"CONTROL n5 k=9 covers={covers9} max={best9} k=10 covers={covers10}"
        f" max={best10}",
        flush=True,
    )

    # 6. receipt consistency (examples valid, counts recorded)
    receipt = json.loads((HERE / "SIDON-RECEIPT.json").read_text(encoding="utf-8"))
    zeros = sorted(
        k for k, v in receipt["shard_e03"].items() if v["count"] == 0
    )
    assert "k10_budget2" in zeros and "k11_budget2" in zeros, zeros
    print(f"RECEIPT zeros={zeros} k9={receipt['shard_e03']['k9_budget0']['count']}", flush=True)
    k11 = receipt["k11_raw_budget4"]
    assert k11["complete"] is True and k11["sub_shards"] == 62, k11
    assert k11["total_hist"] == {}, k11["total_hist"]
    prog11 = json.loads((HERE / "RAW11-PROGRESS.json").read_text(encoding="utf-8"))
    assert prog11["complete"] is True and prog11["total_hist"] == {}
    print(
        "K11 census complete: 62/62 sub-shards, level3=0 level4=0"
        " (zero 11-sets of excess <= 4 through {0,3})",
        flush=True,
    )

    if full:
        for key, k, budget in (
            ("k10_budget0", 10, 0),
            ("k10_budget1", 10, 1),
            ("k10_budget2", 10, 2),
            ("k11_budget2", 11, 2),
        ):
            n, first = search17.count_sets(search17.EVEN, k, budget, fixed=(0, 3))
            assert n == receipt["shard_e03"][key]["count"], (key, n)
            print(f"FULL {key} n={n} matches receipt", flush=True)

    print(f"PASS_17POINT_VERIFY seconds={time.time() - t0:.1f} full={full}")


if __name__ == "__main__":
    main()

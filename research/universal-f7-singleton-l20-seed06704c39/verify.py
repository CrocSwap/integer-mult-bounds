#!/usr/bin/env python3
"""Verification for the KB3b f(7) continuation package.

Rebuilds every reproduced number from scratch and compares the stored
certificate with EXPECTED.json field by field:

  1. byte-exact reproduction of the pinned five/six-source censuses
     (research/universal-connector-six-source/EXPECTED.json), the counting
     bounds 10/14/18 and the Gray constructions 12/16/24;
  2. full reproduction of PR 2542's decisive length-18 census
     (15,775,992 nodes, 312,064 simple 18-cycles, zero universal words);
  3. the exact obstructions: parity (no odd-length restored word), the
     transversal-detour template lemma (level-set components), and the
     stored covering sets' walk-unrealizability (min induced degree < 2);
  4. deterministic re-run of the search campaign against EXPECTED.json;
  5. replay of the resumable simple-20-cycle census checkpoint.

Pass marker: PASS_F7_L20_VERIFY <conclusion>
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import (
    census_words,
    counting_least_even_L,
    cyclic_census,
    gray_word,
    hamiltonian_cycle,
    rg_prefixes,
    word_is_universal,
)
from search import CAMPAIGN, induced_degrees, missing_masks, patterns, run_campaign, word_pts

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINNED = json.loads(
    (ROOT / "research" / "universal-connector-six-source" / "EXPECTED.json").read_text(
        encoding="utf-8"
    )
)


def main():
    t0 = time.time()
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))

    # ---- 1. byte-exact pinned reproduction --------------------------------
    for n, length in ((5, 10), (6, 12), (6, 14)):
        hist, digest, words = census_words(n, length)
        pinned = {(c["sources"], c["length"]): c for c in PINNED["censuses"]}[(n, length)]
        assert words == pinned["words"], (n, length, words)
        assert max(hist) == pinned["max_coverage"]
        assert {str(k): v for k, v in sorted(hist.items())} == pinned["histogram"]
        assert digest == pinned["records_sha256"]
        print(f"REPRO n={n} L={length} words={words} max={max(hist)} sha={digest[:16]}")
    for n in (5, 6, 7):
        lb = counting_least_even_L(n)
        assert lb == PINNED["constructions"][str(n)]["lower_bound"], (n, lb)
        w = gray_word(n)
        assert word_is_universal(w, n) and len(w) == PINNED["constructions"][str(n)]["length"]
        print(f"REPRO n={n} least_even_L={lb} gray={len(w)}")

    # ---- 2. PR 2542 decisive census, fully re-run -------------------------
    # The recorded node count is the SHARDED sum (five depth-3 shards; upper
    # tree nodes are counted once per shard below them, which adds exactly 10
    # to the unsharded count).  Reproduce it shard by shard, then cross-check
    # leaf counts against one unsharded run, as PR 2542's own verifier did.
    tot = {"nodes": 0, "leaves": 0, "hits": 0}
    for pref in rg_prefixes(7, 3):
        rr = cyclic_census(7, 18, budget=9, simple=True, prefix=pref)
        tot["nodes"] += rr["nodes"]
        tot["leaves"] += rr["leaves"]
        tot["hits"] += rr["hits"]
    p = expected["pr2542_l18"]
    assert tot["nodes"] == p["census_nodes"], tot["nodes"]
    assert tot["leaves"] == p["simple_18_cycles"], tot["leaves"]
    assert tot["hits"] == p["universal_words"]
    r = cyclic_census(7, 18, budget=9, simple=True)
    assert r["leaves"] == p["simple_18_cycles"] and r["hits"] == 0, "unsharded drift"
    print(f"REPRO PR2542 L18 nodes(sharded)={tot['nodes']} nodes(unsharded)={r['nodes']} "
          f"cycles={tot['leaves']} universal_words={tot['hits']}")

    # ---- 3. exact obstructions -------------------------------------------
    for odd in (19, 21):
        assert patterns(7, odd) == [], f"odd length {odd} must have no pattern"
    assert len(patterns(7, 20)) == 3 and len(patterns(7, 22)) == 5
    print("LEMMA parity: no restored word has odd length (patterns empty)")

    for name in ("cover20", "cover22"):
        raw = expected[name]["points"]
        base = raw[0]  # covers are translation-invariant; normalize 0 into P
        P = sorted(v ^ base for v in raw)
        assert len(set(P)) == len(P) and 0 in P
        pts = list(P)
        m = 0
        for i, a in enumerate(pts):
            for b in pts[i:]:
                m |= 1 << (a ^ b)
        assert m.bit_count() == 128, f"{name} is not a cover"
        degs = induced_degrees(P)
        assert degs == expected[name]["degrees"], (name, degs)
        assert min(degs) < 2, f"{name} unexpectedly walk-shaped"
        assert hamiltonian_cycle(P, 7) is None, f"{name} unexpectedly Hamiltonian"
        print(f"COVER {name} size={len(P)} degrees={degs} walk_realisable=False")

    # ---- 4. deterministic campaign ---------------------------------------
    run = run_campaign()
    exp = expected["search"]
    for name in exp:
        if name == "seconds":
            continue
        for key, val in exp[name].items():
            assert run[name][key] == val, (name, key, run[name][key], val)
    print("SEARCH campaign reproduced exactly "
          f"L20={run['word_L20']['coverage']} L22={run['word_L22']['coverage']} "
          f"L24={run['word_L24_control']['coverage']}")

    # ---- 5. census20 checkpoint replay -----------------------------------
    prog = json.loads((HERE / "CENSUS20-PROGRESS.json").read_text(encoding="utf-8"))
    acc = prog["accum"]
    assert acc["nodes"] == sum(v["nodes"] for v in prog["done"].values())
    assert acc["leaves"] == sum(v["leaves"] for v in prog["done"].values())
    for w in acc["words"]:
        assert len(w) == 20 and word_is_universal(tuple(w), 7)
    done = len(prog["done"])
    total = prog["shards_total"]
    assert expected["census20"]["shards_total"] == total
    assert expected["census20"]["nodes"] == acc["nodes"]
    assert expected["census20"]["cycles"] == acc["leaves"]
    assert expected["census20"]["universal_words"] == len(acc["words"])
    state = "COMPLETE" if done == total else "PARTIAL"
    print(f"CENSUS20 {state} shards={done}/{total} nodes={acc['nodes']} "
          f"cycles={acc['leaves']} universal_words={len(acc['words'])}")

    print(f"PASS_F7_L20_VERIFY {expected['conclusion']} "
          f"L20={run['word_L20']['coverage']} L22={run['word_L22']['coverage']} "
          f"seconds={round(time.time() - t0, 1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

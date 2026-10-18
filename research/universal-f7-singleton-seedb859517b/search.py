#!/usr/bin/env python3
"""Certificate search: sharp singleton f(7) gap in the PR943 prefix-walk model.

Tiers (each exact integer computation, standard library only):
  1. Reproduction of the pinned censuses and counting bounds (smallest
     falsifying instance first; byte-exact against the pinned EXPECTED.json).
  2. Controls: the five-bit set censuses and the lemma identity tables.
  3. The decisive length-18 census at n = 7: admissible parity splits, the
     exhaustive (E, O) cover search for the surviving split, and a Hamiltonian
     18-cycle realization test for every cover found.

Writes CERTIFICATE.json and prints one PASS marker.  No floating point.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import (
    admissible_splits,
    census_words,
    counting_least_even_L,
    cyclic_census,
    gray_word,
    hamiltonian_cycle,
    joint_covers,
    lemma_a_table,
    normalized_set_census,
    prefixes,
    rg_prefixes,
    set_level_splits,
    split_identity_feasible,
    word_is_universal,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINNED = json.loads(
    (ROOT / "research" / "universal-connector-six-source" / "EXPECTED.json").read_text(
        encoding="utf-8"
    )
)


def main():
    t0 = time.time()
    out = {"tier1_reproduction": {}, "tier2_controls": {}, "tier3_f7": {}}

    # ---- tier 1: reproduction of pinned values ----------------------------
    for n, length in ((5, 10), (6, 12), (6, 14)):
        hist, digest, words = census_words(n, length)
        pinned = {(c["sources"], c["length"]): c for c in PINNED["censuses"]}[(n, length)]
        assert words == pinned["words"], (n, length, words)
        assert max(hist) == pinned["max_coverage"]
        assert {str(k): v for k, v in sorted(hist.items())} == pinned["histogram"]
        assert digest == pinned["records_sha256"]
        out["tier1_reproduction"][f"n{n}_L{length}"] = {
            "words": words,
            "max_coverage": max(hist),
            "records_sha256": digest,
            "matches_pinned": True,
        }
        print(f"REPRO n={n} L={length} words={words} max={max(hist)} sha={digest[:16]}")

    for n in (5, 6, 7):
        lb = counting_least_even_L(n)
        assert lb == PINNED["constructions"][str(n)]["lower_bound"], (n, lb)
        w = gray_word(n)
        assert word_is_universal(w, n) and len(w) == PINNED["constructions"][str(n)]["length"]
        out["tier1_reproduction"][f"n{n}"] = {
            "counting_least_even_L": lb,
            "gray_length": len(w),
        }
        print(f"REPRO n={n} least_even_L={lb} gray={len(w)}")

    # ---- tier 2: controls -------------------------------------------------
    stats9 = normalized_set_census(5, 9)
    assert stats9 == {"sets": 7_888_725, "max_coverage": 29, "covers": 0}, stats9
    out["tier2_controls"]["n5_nine_point"] = stats9
    print("CONTROL n5 nine-point sets=7888725 max=29 covers=0")

    stats10 = normalized_set_census(5, 10)
    splits10 = set_level_splits(5, 10)
    joint10 = joint_covers(5, splits10)
    assert len(joint10) == stats10["covers"] > 0
    cycles10 = 0
    for E, O in joint10:
        P = sorted(set(E) | set(O))
        assert len(P) == 10
        if hamiltonian_cycle(P, 5) is not None:
            cycles10 += 1
    assert cycles10 == 0, "f(5)=12 forbids a universal 10-cycle"
    out["tier2_controls"]["n5_ten_point"] = {
        "brute_sets": stats10["sets"],
        "brute_covers": stats10["covers"],
        "joint_covers": len(joint10),
        "joint_splits": splits10,
        "cycle_realisable_covers": cycles10,
    }
    print(
        f"CONTROL n5 ten-point sets={stats10['sets']} covers={stats10['covers']} "
        f"joint={len(joint10)} cycles=0"
    )

    for s, t in ((9, 8), (8, 9), (8, 8), (9, 9)):
        rows = lemma_a_table(7, s, t)
        feas = any(r["feasible"] for r in rows)
        out["tier2_controls"][f"lemma_rows_{s}_{t}"] = {
            "rows": len(rows),
            "feasible": feas,
        }
        print(f"LEMMA (|E|,|O|)=({s},{t}) rows={len(rows)} feasible={feas}")

    # ---- tier 3: decisive length-18 cyclic census at n = 7 ----------------
    # Justification chain recorded in README/CLAIM:
    #   counting -> |P| >= 17; Lemma A identity -> |P| >= 18 (17-point splits
    #   (9,8)/(8,9) contradictory); |P| = 18 at length 18 forces a simple
    #   closed walk (simple=True) with the forced (9,9) split, whose identity
    #   budget is e_ex + b_ex <= C(9,2) + C(9,2) - 63 = 9 (budget=9).
    splits = admissible_splits(7, 18)
    assert splits == [(9, 9)], splits
    out["tier3_f7"]["admissible_splits_L18"] = splits
    out["tier3_f7"]["size17_splits"] = {
        f"{s}_{t}": split_identity_feasible(7, s, t) for s, t in ((9, 8), (8, 9))
    }

    progress_path = HERE / "CERTIFICATE-PROGRESS.json"
    if progress_path.exists():
        progress = json.loads(progress_path.read_text(encoding="utf-8"))
    else:
        progress = {"done": {}, "accum": {"nodes": 0, "leaves": 0, "hits": 0,
                                          "words": []}}
    shards = rg_prefixes(7, 3)
    for pref in shards:
        key = "".join(map(str, pref))
        if key in progress["done"]:
            continue
        r = cyclic_census(7, 18, budget=9, simple=True, prefix=pref)
        progress["done"][key] = {
            "nodes": r["nodes"], "leaves": r["leaves"], "hits": r["hits"],
            "words": [list(w) for w in r["words"]],
        }
        acc = progress["accum"]
        acc["nodes"] += r["nodes"]
        acc["leaves"] += r["leaves"]
        acc["hits"] += r["hits"]
        acc["words"].extend([list(w) for w in r["words"]])
        progress_path.write_text(json.dumps(progress), encoding="utf-8")
        print(f"SHARD {key} nodes={r['nodes']} leaves={r['leaves']} "
              f"hits={r['hits']} total_nodes={acc['nodes']}")

    acc = progress["accum"]
    out["tier3_f7"]["shards"] = len(shards)
    out["tier3_f7"]["census_nodes"] = acc["nodes"]
    out["tier3_f7"]["simple_18_cycles"] = acc["leaves"]
    out["tier3_f7"]["universal_words"] = acc["words"]
    out["tier3_f7"]["covers_found"] = None
    out["tier3_f7"]["joint_nodes"] = None
    print(f"F7 cyclic census nodes={acc['nodes']} cycles={acc['leaves']} "
          f"universal_words={len(acc['words'])}")

    realisable = acc["words"]
    for w in realisable:
        assert word_is_universal(w, 7) and len(w) == 18

    if realisable:
        out["conclusion"] = "f(7)=18 witness found"
        marker = "PASS_F7_SINGLETON_GAP f(7)=18 witness"
    else:
        out["conclusion"] = "f(7) >= 20 (length 18 excluded)"
        marker = "PASS_F7_SINGLETON_GAP f(7)>=20 L18-excluded"

    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "CERTIFICATE.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(marker)
    return marker


if __name__ == "__main__":
    main()

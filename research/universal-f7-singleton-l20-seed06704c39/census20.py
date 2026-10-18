#!/usr/bin/env python3
"""Resumable restricted-growth simple-20-cycle census at n = 7 (split (10,10)).

Scope: every canonical restored word of length 20 whose 20 boundary states are
distinct (a simple 20-cycle; |P| = 20 forces the (10,10) split).  Prunes are
PR 2542's proved-necessary ones: multiplicity room, self-avoidance (justified
by |P| = L here), and the pair-representation collision budget e_ex + b_ex <= 90 - 63 = 27.
Words with repeated boundary states (|P| in {17,18,19}) are NOT covered by
this census; they are recorded as the open remainder.

Shards are the restricted-growth prefixes of depth 4 (Bell(4) = 15 subtrees,
exactly one per canonical word).  CENSUS20-PROGRESS.json checkpoints after
each shard, so the run is resumable and a partial run still records exact
node/leaf counts.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import cyclic_census, rg_prefixes, word_is_universal

HERE = Path(__file__).resolve().parent
PROGRESS = HERE / "CENSUS20-PROGRESS.json"


def main():
    t0 = time.time()
    if PROGRESS.exists():
        progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
    else:
        progress = {"done": {}, "accum": {"nodes": 0, "leaves": 0, "hits": 0,
                                          "words": []}}
    shards = rg_prefixes(7, 4)
    for pref in shards:
        key = "".join(map(str, pref))
        if key in progress["done"]:
            continue
        r = cyclic_census(7, 20, budget=27, simple=True, prefix=pref)
        progress["done"][key] = {
            "nodes": r["nodes"], "leaves": r["leaves"], "hits": r["hits"],
            "words": [list(w) for w in r["words"]],
        }
        acc = progress["accum"]
        acc["nodes"] += r["nodes"]
        acc["leaves"] += r["leaves"]
        acc["hits"] += r["hits"]
        acc["words"].extend([list(w) for w in r["words"]])
        progress["shards_total"] = len(shards)
        PROGRESS.write_text(json.dumps(progress), encoding="utf-8")
        print(f"SHARD {key} nodes={r['nodes']} leaves={r['leaves']} "
              f"hits={r['hits']} total_nodes={acc['nodes']} "
              f"done={len(progress['done'])}/{len(shards)} "
              f"secs={round(time.time()-t0, 1)}")

    acc = progress["accum"]
    for w in acc["words"]:
        assert word_is_universal(tuple(w), 7) and len(w) == 20
    complete = len(progress["done"]) == len(shards)
    print(f"CENSUS20 {'COMPLETE' if complete else 'PARTIAL'} "
          f"shards={len(progress['done'])}/{len(shards)} nodes={acc['nodes']} "
          f"cycles={acc['leaves']} universal_words={len(acc['words'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

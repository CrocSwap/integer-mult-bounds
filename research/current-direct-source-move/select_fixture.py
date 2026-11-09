"""Bounded finite-source fixture search; gate count is not measured time.

The completed archived search inspected all 2886 pairs under a 180-second
external cap. Prepared for @CubeJerry with substantial OpenAI assistance.
Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
from collections import Counter
import json
from direct_sources import activate

S = activate()


def search(limit=None):
    word, entries, pairs, _report = S.catalog.catalog(); by_pair = {}
    for pc in entries:
        by_pair.setdefault(tuple(word["program"][pc][2:4]), []).append(pc)
    rows = []; histogram = Counter()
    for first, second in pairs[:limit]:
        _original, record = S.catalog.chart(first, second); sides = {}
        for side in ("right", "left"):
            recipe = S.common.shared.engine.Recipe(record[side], tuple("v"+str(i) for i in range(9)))
            sides[side] = dict(affine_gates=len(recipe.word), quadratic_terms=len(recipe.quadratic),
                              linear_terms=sum(x != 0 for x in recipe.linear), constant_phase=recipe.constant)
        score = sum(x["affine_gates"] for x in sides.values()); histogram[score] += 1
        rows.append(dict(pair=[first, second], events=by_pair[first, second], rank=record["rank"], stats=sides, score=score))
    rows.sort(key=lambda x:(x["score"], x["rank"], sum(v["quadratic_terms"] for v in x["stats"].values())))
    return dict(completed=len(rows), total=len(pairs), unexamined=len(pairs)-len(rows),
                ranked_by="literal source affine gate count, then paid rank, then quadratic terms; not a time optimum",
                affine_gate_histogram=dict(sorted(histogram.items())), best=rows[:20])


if __name__ == "__main__":
    parser = ArgumentParser(); parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        raise ValueError("positive optional finite search limit")
    print(json.dumps(search(args.limit), sort_keys=True))

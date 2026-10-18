#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional native-cardinality proposal search; acceptance uses exact replay."""
import argparse
import json
from pathlib import Path
import time
import search


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-hits", type=int, default=1120)
    parser.add_argument("--coordinate", action="store_true")
    parser.add_argument("--all-cliques", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to overwrite an experiment")
    from pysat.solvers import Minicard
    data, frames, records, census = search.candidates(args.min_hits)
    print("SAT_CENSUS", census, flush=True)
    size = len(records)
    misses = [[] for _ in frames]
    diagonals = {i: [] for i in data["live"]}
    full = (1 << len(frames)) - 1
    for j, (met, diag, *_) in enumerate(records, 1):
        for i in search.engine.bits(full ^ met):
            misses[i].append(j)
        for i in search.engine.bits(diag):
            diagonals[i].append(j)
    coordinate_root = data["punctured_frame"][0]
    _, _, supports, _ = search.engine.geometry(data)
    coordinate_support = supports[2 * coordinate_root] if args.coordinate else 0
    count = 9 if args.coordinate else 10
    from screen import clique_masks
    cliques = clique_masks(data) if args.all_cliques else []
    start = time.monotonic()
    with Minicard() as solver:
        solver.add_atmost(list(range(1, size + 1)), count)
        solver.add_atmost(list(range(-size, 0)), size - count)
        for row in misses:
            solver.add_atmost(row, 2)
        for root, row in diagonals.items():
            if not coordinate_support >> root & 1:
                solver.add_clause(row)
        if not args.coordinate:
            solver.add_clause([1])
        rounds = 0
        while True:
            result = solver.solve()
            if not result:
                break
            ids = [j-1 for j in solver.get_model() if 0 < j <= size]
            terms = [(records[j][5], records[j][6]) for j in ids]
            if args.coordinate:
                terms.append((coordinate_support, coordinate_support))
            failures = [mask for mask in cliques
                        if sum(bool(left & mask and right & mask) for left, right in terms) < mask.bit_count()]
            print("SAT_CLIQUE_ROUND", rounds, "failures", len(failures), flush=True)
            if not failures:
                break
            for mask in failures:
                missed = [j for j, record in enumerate(records, 1)
                          if not (record[5] & mask and record[6] & mask)]
                bound = count - mask.bit_count() + bool(coordinate_support & mask)
                solver.add_atmost(missed, bound)
            rounds += 1
        receipt = dict(census=census, forced_first=not args.coordinate, min_hits=args.min_hits,
                       coordinate_root=coordinate_root if args.coordinate else None,
                       all_cliques=args.all_cliques, separation_rounds=rounds,
                       elapsed_seconds=time.monotonic()-start, satisfiable=result,
                       solver="PySAT Minicard; no UNSAT certificate claimed")
        if result:
            ids = [j-1 for j in solver.get_model() if 0 < j <= size]
            receipt["terms"] = [[records[j][2], records[j][3], format(records[j][4], "x")] for j in ids]
        args.output.write_text(json.dumps(receipt, indent=2)+"\n")
        print("SAT_RESULT", result, receipt.get("terms"), flush=True)


if __name__ == "__main__":
    main()

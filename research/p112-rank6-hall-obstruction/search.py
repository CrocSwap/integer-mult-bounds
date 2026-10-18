#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional floating MILP proposal search; not an exclusion certificate."""
import argparse
import importlib.util
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location(
    "rank6_predecessor", ROOT / "research/p112-rank6-frame-coverage/engine.py")
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)


def candidates(min_hits=1120):
    data = engine.model()
    _, pairing, supports, frames = engine.geometry(data)
    frame_masks = [sum(1 << i for i in frame) for frame in frames]
    hit_cache = {}

    def hits(support):
        if support not in hit_cache:
            hit_cache[support] = sum(1 << i for i, f in enumerate(frame_masks) if f & support)
        return hit_cache[support]

    dictionary = {}
    parents = slices = 0
    for a, left in enumerate(supports):
        for b, right in enumerate(supports):
            if engine.rank(pairing, left, right) != 7:
                continue
            parents += 1
            right_hits = hits(right)
            for cut in engine.column_code(pairing, left, right):
                slices += 1
                row = left ^ cut
                met = hits(row) & right_hits
                if met.bit_count() >= min_hits:
                    key = (met, row & right)
                    dictionary.setdefault(key, (a, b, cut, row, right))
    records = [(met, diag, *dictionary[(met, diag)]) for met, diag in sorted(dictionary)]
    return data, frames, records, dict(parents=parents, slices=slices, candidates=len(records))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-hits", type=int, default=1120)
    parser.add_argument("--seconds", type=int, default=180)
    parser.add_argument("--force-first", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("refusing to overwrite an experiment")
    import numpy as np
    import scipy
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix
    data, frames, records, census = candidates(args.min_hits)
    print("SEARCH_CENSUS", census, flush=True)
    all_frames = (1 << len(frames)) - 1
    live_index = {root: index for index, root in enumerate(data["live"])}
    rr, cc = [], []
    for j, (met, diag, *_) in enumerate(records):
        for i in engine.bits(all_frames ^ met):
            rr.append(i)
            cc.append(j)
        rr.append(1260)
        cc.append(j)
        for root in engine.bits(diag):
            rr.append(1261 + live_index[root])
            cc.append(j)
    matrix = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(1373, len(records))).tocsc()
    lower, upper = np.zeros(len(records)), np.full(len(records), 10.)
    if args.force_first:
        lower[0] = 1
    low, high = np.full(1373, -np.inf), np.full(1373, 2.)
    low[1260] = high[1260] = 10
    low[1261:], high[1261:] = 1, np.inf
    start = time.monotonic()
    result = milp(np.zeros(len(records)), integrality=np.ones(len(records)),
                  bounds=Bounds(lower, upper), constraints=LinearConstraint(matrix, low, high),
                  options={"time_limit": args.seconds, "mip_rel_gap": 0.})
    receipt = dict(census=census, min_hits=args.min_hits, forced_first=args.force_first,
                   seconds_limit=args.seconds, elapsed_seconds=time.monotonic()-start,
                   numpy=np.__version__, scipy=scipy.__version__, status=int(result.status),
                   message=result.message, feasible=False,
                   scope="Necessary frame-count and diagonal-cover constraints only; floating solver is not proof.")
    if result.x is not None:
        chosen = [j for j, value in enumerate(result.x) for _ in range(round(float(value)))]
        terms = [records[j] for j in chosen]
        counts = [sum(bool(term[0] >> i & 1) for term in terms) for i in range(1260)]
        diagonal = [sum(bool(term[1] >> root & 1) for term in terms) for root in data["live"]]
        receipt.update(terms=[[a, b, format(cut, "x")] for _, _, a, b, cut, _, _ in terms],
                       minimum_frame_hits=min(counts), minimum_diagonal_hits=min(diagonal),
                       feasible=len(terms)==10 and min(counts)>=8 and min(diagonal)>=1)
    args.output.write_text(json.dumps(receipt, indent=2)+"\n")
    print("SEARCH_RESULT", receipt["feasible"], receipt["status"], receipt["message"])


if __name__ == "__main__":
    main()

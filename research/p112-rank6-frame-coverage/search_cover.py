#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Optional bounded MILP proposal search; the standard-library replay is exact."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine


def candidates():
    data = engine.model()
    _, n, support, frames = engine.geometry(data)
    frame_masks = [sum(1 << i for i in f) for f in frames]
    cache, dictionary = {}, {}

    def hits(mask):
        if mask not in cache:
            cache[mask] = sum(1 << i for i, f in enumerate(frame_masks) if f & mask)
        return cache[mask]
    for a, left in enumerate(support):
        for b, right in enumerate(support):
            if engine.rank(n, left, right) != 7:
                continue
            code = [0]
            for generator in engine.basis(n[j] & left for j in engine.bits(right)):
                code += [v ^ generator for v in code]
            for word in code[1:]:
                met = hits(left ^ word) & hits(right)
                if met.bit_count() == 1120:
                    missing = ((1 << len(frames))-1) ^ met
                    dictionary.setdefault(missing, (a, b, hex(word)))
    return [[a, b, cut, format(missing, "x")]
            for missing, (a, b, cut) in sorted(dictionary.items())]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--diagonal", action="store_true", help="also cover every live diagonal position")
    args = parser.parse_args()
    engine.require(not args.output.exists(), "search output already exists")
    import numpy as np
    import scipy
    from scipy.optimize import Bounds, LinearConstraint, milp
    from scipy.sparse import coo_matrix
    records = candidates()
    engine.require(len(records) == 5376, "restricted candidate census changed")
    data = engine.model()
    _, _, support, _ = engine.geometry(data)
    rr, cc = [], []
    for j, (a, b, cut, missing) in enumerate(records):
        rr.extend(engine.bits(int(missing, 16)))
        cc.extend([j] * int(missing, 16).bit_count())
        rr.append(1260)
        cc.append(j)
        if args.diagonal:
            both = (support[a] ^ int(cut, 16)) & support[b]
            for k, i in enumerate(data["live"]):
                if both & (1 << i):
                    rr.append(1261 + k)
                    cc.append(j)
    size = 1373 if args.diagonal else 1261
    matrix = coo_matrix((np.ones(len(rr)), (rr, cc)), shape=(size, len(records))).tocsc()
    low, high = np.full(size, -np.inf), np.full(size, 2.)
    low[1260] = high[1260] = 10
    if args.diagonal:
        low[1261:], high[1261:] = 1., np.inf
    lower, upper = np.zeros(len(records)), np.ones(len(records))
    lower[20] = 1  # Assignment seed chooses the forced frame pattern.
    start = time.monotonic()
    result = milp(np.zeros(len(records)), integrality=np.ones(len(records)),
                  bounds=Bounds(lower, upper), constraints=LinearConstraint(matrix, low, high),
                  options={"time_limit": 120., "mip_rel_gap": 0.})
    receipt = dict(solver="scipy.optimize.milp", seed=20,
                   domain="5376 distinct 1120-hit maximal row-cut frame patterns; sorted index20 forced; choose10 distinct patterns",
                   require_diagonal_coverage=args.diagonal, time_limit_seconds=120,
                   stopping_rule="Return one feasible incumbent or stop at the 120-second solver limit; no exclusion theorem from failure.",
                   elapsed_seconds=time.monotonic()-start, status=int(result.status),
                   message=result.message,
                   candidate_sha256=hashlib.sha256(json.dumps(records).encode()).hexdigest(),
                   environment=dict(python=sys.version.split()[0], numpy=np.__version__, scipy=scipy.__version__),
                   feasible=False)
    if result.x is not None:
        selected = [int(i) for i, value in enumerate(result.x) if value > .5]
        misses = [0] * 1260
        diagonals = [0] * 112
        for index in selected:
            a, b, cut, missing = records[index]
            for f in engine.bits(int(missing, 16)):
                misses[f] += 1
            both = (support[a] ^ int(cut, 16)) & support[b]
            for k, i in enumerate(data["live"]):
                diagonals[k] += bool(both & (1 << i))
        receipt.update(terms=[records[i][:3] for i in selected], minimum_hits=10-max(misses),
                       minimum_diagonal_coverage=min(diagonals))
        receipt["feasible"] = (len(selected) == 10 and max(misses) <= 2 and
                               (not args.diagonal or min(diagonals) >= 1))
    args.output.write_text(json.dumps(receipt, indent=2)+"\n")
    print("SEARCH_RESULT", receipt["feasible"], receipt["status"])


if __name__ == "__main__":
    main()

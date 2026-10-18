#!/usr/bin/env python3
"""Bounded deterministic MRV cover/factor search for the tri-plane P112 experiment."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction as Q
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
import verify as V  # noqa: E402
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import ceiling  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cover-limit", type=int, default=10_000)
    parser.add_argument("--out", type=Path, default=PACKAGE / "CANDIDATE.json")
    args = parser.parse_args()
    if args.cover_limit < 1:
        raise SystemExit("cover-limit must be positive")

    labels = V.load_labels()
    triple_count = len(V.candidate_triples(labels, residual=0))
    V.need(triple_count == 24_416, "candidate triple domain drift")
    best = None
    examined = 0
    for cover in V.iter_orthogonal_covers(labels, residual=0):
        examined += 1
        groups = [[0], *[list(edge) for edge in cover]]
        matrices = V.solve_identity(groups, labels)
        if matrices is None:
            if examined >= args.cover_limit:
                break
            continue
        terms = [term for g, matrix in zip(groups, matrices)
                 for term in V.factor_matrix(g, matrix, labels)]
        hist: dict[int, int] = {}
        for term in terms:
            charge = term["copy_rank"]
            V.need(charge > 0, "zero-rank support term outside the priced interface")
            hist[charge] = hist.get(charge, 0) + 1
        copy_charge = sum(r * n for r, n in hist.items())
        profile = V.CORE.copy()
        for r, n in hist.items():
            profile[r] = profile.get(r, 0) + n
        moment = ceiling.relax(profile, 73, 896, 9, copy_charge,
                               Q(1, 99), unpaid=3)
        key = (moment[1], copy_charge, len(terms), tuple(sorted(hist.items())))
        if best is None or key < best[0]:
            best = (key, groups, matrices, terms, hist, profile)
            print("BEST", f"covers={examined}", f"copy={copy_charge}",
                  f"terms={len(terms)}", f"hist={dict(sorted(hist.items()))}",
                  f"moment_upper={float(moment[1]):.15f}", flush=True)
        if moment[1] < 1:
            break
        if examined >= args.cover_limit:
            break
    if best is None:
        raise SystemExit(f"no exact factorization among {examined} covers")

    key, groups, matrices, terms, hist, profile = best
    charge = sum(r * n for r, n in hist.items())
    cap = ceiling.ceiling(profile, 73, 896, 9, charge,
                          grid=Q(1, 10**12), unpaid=3)[1]
    candidate = {
        "residual": [0],
        "groups": groups,
        "matrices": matrices,
        "matrix_rank_hist": {
            str(r): sum(V.matrix_rank(m) == r for m in matrices)
            for r in sorted({V.matrix_rank(m) for m in matrices})
        },
        "copy_hist": {str(r): n for r, n in sorted(hist.items())},
        "copy_charge": charge,
        "terms": terms,
        "local_profile": {str(r): n for r, n in sorted(profile.items())},
        "covers_examined": examined,
        "passes_target": key[0] < 1,
        "moment_upper_at_1_over_99": str(key[0]),
        "a_ceiling": str(cap),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(candidate, separators=(",", ":")) + "\n",
                        encoding="utf-8")
    print("PASS_TRI_PLANE_SEARCH", f"covers={examined}",
          f"triples={len(groups)-1}", f"terms={len(terms)}", f"copy={charge}",
          f"moment_upper={float(key[0]):.15f}", f"a_cap={float(cap):.12f}",
          f"target={'PASS' if key[0] < 1 else 'MISS'}", f"certificate={args.out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One 90-second single-thread MILP discovery solve; never certifies infeasibility."""
import argparse
import importlib.util
import json
from pathlib import Path
import time
import warnings

import numpy as np
import scipy
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_array, vstack


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("output must be new")
    spec = importlib.util.spec_from_file_location("support_checker", Path(__file__).with_name("verify.py"))
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    started = time.monotonic()
    _, dots, live, pairing, adjacency = checker.geometry()
    atoms = checker.dictionary(dots, live, pairing)
    constraints = checker.cliques(adjacency, live, {1, 2, 8})
    masks = [m for m, _ in constraints]
    indices, indptr = [], [0]
    for support, _ in atoms:
        indices.extend(i for i, clique in enumerate(masks) if support & clique)
        indptr.append(len(indices))
    matrix = csc_array((np.ones(len(indices)), np.asarray(indices, dtype=np.int32),
                        np.asarray(indptr, dtype=np.int32)), shape=(len(masks), len(atoms)))
    prices = np.array([r for _, r in atoms], dtype=float)
    matrix = vstack((matrix, csc_array(prices.reshape(1, -1))), format="csc")
    lower = np.array([size for _, size in constraints] + [-np.inf], dtype=float)
    upper = np.array([np.inf] * len(constraints) + [63], dtype=float)
    print(json.dumps({"atoms": len(atoms), "constraints": len(lower),
                      "nonzeros": matrix.nnz, "setup_seconds": time.monotonic() - started}), flush=True)
    solve_start = time.monotonic()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Unrecognized options detected")
        result = milp(prices, integrality=np.ones(len(atoms)),
                      bounds=Bounds(0, np.floor(63 / prices)),
                      constraints=LinearConstraint(matrix, lower, upper),
                      options={"time_limit": 90.0, "mip_rel_gap": 0.0, "threads": 1, "random_seed": 20261023})
    selected = []
    if result.x is not None:
        for (support, price), value in zip(atoms, result.x):
            if value > 0.5:
                if abs(value - round(value)) > 1e-5:
                    raise ValueError("nonintegral discovery incumbent")
                selected.append({"support": hex(support), "rank": price, "count": round(value)})
    record = {"status": int(result.status), "message": result.message,
              "selected": selected, "solver_seconds": time.monotonic() - solve_start,
              "total_seconds": time.monotonic() - started,
              "objective": None if result.x is None else float(result.fun),
              "mip_dual_bound": getattr(result, "mip_dual_bound", None),
              "scipy": scipy.__version__, "numpy": np.__version__,
              "scope": "Floating discovery; no proof of infeasibility or mathematical acceptance."}
    with args.output.open("x") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()

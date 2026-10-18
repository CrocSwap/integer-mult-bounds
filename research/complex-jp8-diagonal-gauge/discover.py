#!/usr/bin/env python3
"""Optional nomination using SciPy/HiGHS; exact checking is in verify.py.

Prints a freshly nominated primal/dual certificate, without overwriting files.
Alternative optima may differ by solver version. Apache-2.0; substantial
OpenAI Codex assistance for Luis Leon (@mythrilium).
"""
import importlib.util
import json
import random
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, vstack

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gauge_verify", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def main():
    word, _, _ = V.load_inputs()
    n = 2 * word["v"] + word["R"]
    edges = V.native_edges(word["cleanup"])
    adjacent = [[] for _ in range(n)]
    for t, s, e in edges:
        adjacent[t].append((t, s, e))
        adjacent[s].append((t, s, e))
    g = [0] * n
    order = [r for r in range(n) if adjacent[r]]
    random.Random(35).shuffle(order)

    def local(r, x):
        return 2 * abs(x) + sum(abs(e + (x if t == r else g[t]) - (x if s == r else g[s]))
                               for t, s, e in adjacent[r])

    history = []
    for sweep in range(10):
        changes = 0
        for r in order:
            best = min(range(-2, 3), key=lambda x: (local(r, x), abs(x - g[r]), abs(x), x))
            if local(r, best) < local(r, g[r]):
                g[r] = best
                changes += 1
        objective = 2 * sum(map(abs, g)) + sum(abs(e + g[t] - g[s]) for t, s, e in edges)
        history.append({"sweep": sweep + 1, "changed": changes, "price": objective})
        if not changes:
            break
    # An optimistic profitable screen motivates the same object's exact dual LP.
    rows, cols, vals = [], [], []
    for i, (t, s, _) in enumerate(edges):
        rows.extend([t, s])
        cols.extend([i, i])
        vals.extend([1, -1])
    incidence = coo_matrix((vals, (rows, cols)), shape=(n, len(edges))).tocsc()
    result = linprog(-np.array([e for _, _, e in edges]),
                     A_ub=vstack([incidence, -incidence]), b_ub=np.full(2 * n, 2),
                     bounds=(-1, 1), method="highs")
    V.require(result.success, "solver did not nominate a solution")
    dual = [round(x) for x in result.x]
    h = result.ineqlin.marginals
    gauge = [round(h[i] - h[n + i]) for i in range(n)]
    # Rounded solver output is merely a nomination: exact feasibility AND zero
    # gap are mandatory, and are sufficient independently of solver status.
    objective = V.check_duality(edges, gauge, dual)
    certificate = {"schema": "jp8-diagonal-gauge-v1", "assignment_seed": 35,
                   "exponents": gauge, "edge_dual": dual, "objective": objective,
                   "original_objective": sum(abs(e) for _, _, e in edges),
                   "nonzero": sum(x != 0 for x in gauge), "l1_exponents": sum(map(abs, gauge))}
    print(json.dumps({"coordinate_screen": history, "certificate": certificate}, indent=2))


if __name__ == "__main__":
    main()

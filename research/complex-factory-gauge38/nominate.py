#!/usr/bin/env python3
"""Optional solver nomination; the published verifier uses only exact integers.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Requires NumPy/SciPy. Does not overwrite any committed certificate or receipt.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import Bounds, LinearConstraint, linprog, milp

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gauge_check", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
v.source_check()
word = v.read(v.FACTORY / "CIRCUIT.json")["replacement"]
nodes, edges, adds, negations = v.graph(word)
n, m = nodes - 1, len(edges)
A, b = np.zeros((2 * m, n + m)), np.zeros(2 * m)
for j, (u, target, e, *_) in enumerate(edges):
    if target:
        A[2*j, target-1], A[2*j+1, target-1] = 1, -1
    if u:
        A[2*j, u-1], A[2*j+1, u-1] = -1, 1
    A[2*j, n+j] = A[2*j+1, n+j] = -1
    b[2*j], b[2*j+1] = -e, e
lp = linprog([0]*n + [1]*m, A_ub=A, b_ub=b,
             bounds=[(None, None)]*n + [(0, None)]*m, method="highs")
v.need(lp.success, "LP nomination failed")
g = [0] + [round(x) for x in lp.x[:n]]
y = [round(-lp.ineqlin.marginals[2*j] + lp.ineqlin.marginals[2*j+1]) for j in range(m)]
cert = v.read(HERE / "CERTIFICATE.json")
cert.update(potentials=g, dual=y, replacement=v.construct(word, g))
v.certificate_check(word, cert)

# Charge each original negative-scale interval as a macro even when its dyadic
# exponent is zero. Extra wire scales and nonunit additions get binary flags.
signs, negative, j = [1]*8, set(), 0
for op in word:
    if op[0] == "scale":
        signs[op[1]] *= -1 if v.Q(op[2], op[3]) < 0 else 1
    else:
        for r in op[1:3]:
            if signs[r] < 0:
                negative.add(j)
            signs[r] = 1
            j += 1
        j += 1
for r in range(8):
    if signs[r] < 0:
        negative.add(j)
    j += 1
N = n + 2*m
rows, lows, highs = [], [], []


def constraint(terms, low, high):
    row = np.zeros(N)
    for i, x in terms.items():
        row[i] = x
    rows.append(row)
    lows.append(low)
    highs.append(high)


for j, (u, target, e, *_) in enumerate(edges):
    terms = {}
    if target:
        terms[target-1] = 1
    if u:
        terms[u-1] = -1
    constraint(terms | {n+j: -1}, -np.inf, -e)
    constraint({k: -x for k, x in terms.items()} | {n+j: -1}, -np.inf, e)
    constraint({n+j: 1, n+m+j: -23}, -np.inf, 0)
constraint({n+m+j: 1 for j in range(m) if edges[j][3] == "wire" and j not in negative},
           -np.inf, 4)
objective = [0]*n + [1]*m + [int(edge[3] == "add") for edge in edges]
constraint({i: x for i, x in enumerate(objective) if x}, -np.inf, 23)
result = milp(objective, integrality=np.ones(N),
              bounds=Bounds([-37]*n + [0]*m + [0]*m, [37]*n + [23]*m + [1]*m),
              constraints=LinearConstraint(np.array(rows), lows, highs),
              options={"time_limit": 20})
v.need(result.x is not None, "bounded MILP found no incumbent")
budget_g = [0] + [round(x) for x in result.x[:n]]
budget_word = v.construct(word, budget_g)
old = v.module("nomination_old", v.FACTORY / "verify.py")
lower = v.module("nomination_lower", v.ROOT / "research/complex-dyadic-lowering/lower.py")
price = len(v.circuit_primitives(lower, budget_word))
v.need(len(budget_word) <= 34 and price <= 81, "rounded nomination exceeds budget")
v.local_check(old, lower, word, budget_word, price)
print(json.dumps({"scipy": scipy.__version__, "numpy": np.__version__,
                  "lp_exact_tension": 9, "lp_exact_pr696_optimum": 67,
                  "milp_nomination_only": True, "milp_seconds_limit": 20,
                  "milp_status": result.message, "budget_price": price,
                  "budget_macro_count": len(budget_word),
                  "budget_potentials": budget_g,
                  "scope": "No macro-budget optimality claim; ties and solver status can vary."}, indent=2))

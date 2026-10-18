#!/usr/bin/env python3
"""Optional solver discovery; never imported by the acceptance checkers.

Adapted from navinor's complex-x4-frame-bound/gen_duals.py, retained unchanged
under references/gen_duals.py. Gareth Davidson with OpenAI Codex assistance.
Apache-2.0. Needs highspy, numpy and scipy; their actual versions are recorded.
"""
import gzip
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

import highspy
import numpy as np
import scipy
import scipy.sparse as sp
import scipy.sparse.linalg as spla

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("retained_frame_model", HERE / "references/frame_model.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
RANKS = range(2, 10)
A = Q(1690054109089, 10**15)


def solve(rows, rhs, cols, gamma):
    nr, nc = len(rows), len(cols)
    start, index, value, cost = [0], [], [], []
    for _, c, entries in cols:
        cost.append(sum(c[d] * gamma[d] for d in range(len(c))))
        for i, a in sorted(entries):
            index.append(i)
            value.append(float(a))
        start.append(len(index))
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = nc, nr
    lp.col_cost_ = np.array(cost)
    lp.col_lower_ = np.zeros(nc)
    lp.col_upper_ = np.full(nc, highspy.kHighsInf)
    lp.row_lower_ = np.array(rhs, dtype=float)
    lp.row_upper_ = np.array(rhs, dtype=float)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = np.array(start, dtype=np.int32)
    lp.a_matrix_.index_ = np.array(index, dtype=np.int32)
    lp.a_matrix_.value_ = np.array(value)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("presolve", "off")
    h.setOptionValue("solver", "simplex")
    h.passModel(lp)
    h.run()
    if h.getModelStatus() != highspy.HighsModelStatus.kOptimal:
        raise ValueError(h.modelStatusToString(h.getModelStatus()))
    return h.getInfo().objective_function_value, h.getBasis(), list(h.getSolution().col_value)


def symbolic_duals(rows, cols, basis):
    basic = [j for j in range(len(cols)) if basis.col_status[j] == highspy.HighsBasisStatus.kBasic]
    active = [i for i in range(len(rows)) if basis.row_status[i] != highspy.HighsBasisStatus.kBasic]
    if len(basic) != len(active):
        raise ValueError("nonsquare basis")
    pos = {i: k for k, i in enumerate(active)}
    data, ri, ci = [], [], []
    for k, j in enumerate(basic):
        for i, a in cols[j][2]:
            if i in pos:
                ri.append(k)
                ci.append(pos[i])
                data.append(float(a))
    matrix = sp.csc_matrix((data, (ri, ci)), shape=(len(basic), len(active)))
    lu = spla.splu(matrix)
    dual = {}
    for d in RANKS:
        solution = lu.solve(np.array([float(cols[j][1][d]) for j in basic]))
        for k, i in enumerate(active):
            x = Q(float(solution[k])).limit_denominator(1 << 20)
            if x:
                dual.setdefault(i, {})[d] = x
    for j in basic:
        for d in RANKS:
            value = sum((a * dual.get(i, {}).get(d, 0) for i, a in cols[j][2]), Q(0))
            if value != cols[j][1][d]:
                raise ValueError("rationalized basis identity failed")
    return dual


def main():
    raw = gzip.decompress((HERE / "references/WORD.json.gz").read_bytes())
    word = json.loads(raw)
    model = M.Model(word)
    a = float(A)
    gamma = [0.0, 0.0] + [(d ** (1-a) - d) / a for d in RANKS]
    out = {"schema": "selected-k8-frame-duals-v1", "nomination_a": str(A),
           "word_sha256": hashlib.sha256(raw).hexdigest(), "components": []}
    report = {"versions": {"highspy": highspy.Highs().version(), "numpy": np.__version__,
                           "scipy": scipy.__version__}, "components": []}
    all_same = True
    for index, comp in enumerate(model.components()):
        labels, unary, pairs = model.component_problem(comp)
        rows, rhs, cols = M.lp(labels, unary, pairs)
        obj, basis, primal = solve(rows, rhs, cols, gamma)
        dual = symbolic_duals(rows, cols, basis)
        base = M.assignment_cost(labels, unary, pairs, {node: model.baseline()[node] for node in comp})
        objective = {d: sum((rhs[i] * vec.get(d, 0) for i, vec in dual.items()), Q(0)) for d in RANKS}
        same = all(objective[d] == base[d] for d in RANKS)
        all_same &= same
        fractional = sum(1 for x in primal if 1e-8 < x < 1-1e-8)
        report["components"].append({"first_gate": comp[0][1], "nodes": len(comp),
                                      "rows": len(rows), "columns": len(cols),
                                      "dual_matches_baseline": same, "fractional_columns": fractional,
                                      "numerical_gap": sum(base[d]*gamma[d] for d in RANKS)-obj})
        out["components"].append({"first": json.dumps(comp[0]), "nodes": len(comp),
                                  "duals": {json.dumps(rows[i]): {str(d): str(x) for d, x in sorted(vec.items())}
                                            for i, vec in sorted(dual.items())}})
        if not same or index % 20 == 0:
            print(index, len(comp), "same_baseline", same, "fractional", fractional, flush=True)
    data = json.dumps(out, sort_keys=True, separators=(",", ":")).encode()
    (HERE / "DUALS.json.gz").write_bytes(gzip.compress(data, mtime=0))
    report["all_duals_match_baseline"] = all_same
    report["canonical_duals_sha256"] = hashlib.sha256(data).hexdigest()
    (HERE / "DISCOVERY.json").write_text(json.dumps(report, indent=2) + "\n")
    print("NOMINATED_NOT_YET_CERTIFIED", len(out["components"]), "same_baseline", all_same,
          "sha256", report["canonical_duals_sha256"], flush=True)


if __name__ == "__main__":
    main()

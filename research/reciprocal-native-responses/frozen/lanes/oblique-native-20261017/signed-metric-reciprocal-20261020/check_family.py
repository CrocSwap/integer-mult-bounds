#!/usr/bin/env python3
"""Check the reciprocal family and the diagonal-metric equations."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
MODEL_PIN = "9d7052a27139990fe9eb4e397b672d2ae7069de75636e3b068f172760cf173fb"
need_path = HERE / "check_model.py"
if sha256(need_path.read_bytes()).hexdigest() != MODEL_PIN:
    raise ValueError("Frozen model checker pin")
spec = importlib.util.spec_from_file_location("reciprocal_family_model", need_path)
model = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = model
spec.loader.exec_module(model)
r, need = model.r, model.need


def metric_constraints(E):
    n = len(E)
    result = []
    for i in range(n):
        for j in range(i, n):
            row = {k: E[k].get(i, F(0)) * E[k].get(j, F(0)) for k in range(n)
                   if E[k].get(i, 0) * E[k].get(j, 0)}
            if i == j:
                r.add(row, {i: F(-1)})
            if row:
                result.append(row)
    return result


def unit(c):
    a, b = abs(c.numerator), c.denominator
    return bool(a) and not a & (a - 1) and not b & (b - 1)


def reflection_response(n):
    m, k = n - 4, n - 2
    u, ell = [F(1)] * k + [F(m), F(0)], [F(-1)] * k + [F(1), F(0)]
    R = r.identity(n)
    for i in range(n):
        r.add(R[i], {j: c for j, c in enumerate(ell) if c}, u[i])
    P = r.identity(n)
    P[-2], P[-1] = P[-1], P[-2]
    return r.product(P, R), r.product(R, P)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    reports = []
    for n in range(5, 25):
        E, Ei, R, P, J, Ji, u, ell = model.block(n)
        constraints = metric_constraints(E)
        need(r.rank(constraints, n) == n - 1, "Exact diagonal-metric nullity one")
        need(all(sum(c * J[i][i] for i, c in row.items()) == 0 for row in constraints),
             "The stated metric spans the kernel")
        m = n - 4
        need(all(unit(row[i]) for i, row in enumerate(J)) == (not m & (m - 1)),
             "The exact dyadic-unit condition")
        need(r.rank(model.difference(E, P), n) == 1
             and r.rank(model.difference(E, r.identity(n)), n) == 2,
             "The two exact displacement ranks")
        A = [{j: F(int(i == j) - 1) for j in range(n) if i != j} for i in range(n)]
        Ai = [{j: F(int(i == j)) - F(1, n - 1) for j in range(n)} for i in range(n)]
        need(r.product(A, Ai) == r.product(Ai, A) == r.identity(n),
             "Both rank-one comparison inverse orders")
        need(all(Ai[i][i] == F(n - 2, n - 1) for i in range(n)),
             "The nonzero reciprocal diagonal obstruction")
        reports.append({"n": n, "metric_equation_rank": n - 1,
                        "dyadic_unit_metric": all(unit(row[i]) for i, row in enumerate(J)),
                        "rank_E_minus_I": 2, "rank_E_minus_P": 1,
                        "centre_signed_norm": "2"})
    swap = [{1: F(1)}, {0: F(1)}]
    need(r.product(swap, swap) == r.identity(2)
         and r.rank(model.difference(swap, r.identity(2)), 2) == 1,
         "The n=2 lower-bound exception")
    E3, Ei3 = reflection_response(3)
    need(r.product(r.transpose(E3, 3), E3) == r.identity(3)
         and all(not row.get(i) for i, row in enumerate(Ei3)),
         "The positive n=3 exception")
    E4, Ei4 = reflection_response(4)
    constraints4 = metric_constraints(E4)
    need(r.rank(constraints4, 4) == 3
         and all(sum(row.get(i, F(0)) for i in (2, 3)) == 0 for row in constraints4),
         "The singular n=4 metric kernel")
    checks = {
        "status": "PASS_RECIPROCAL_FAMILY",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "model_checker_sha256": MODEL_PIN, "reports": reports,
        "boundary_controls": {"n2_rank_one_swap": True, "n3_positive_metric": True,
                              "n4_only_singular_diagonal_metrics": True},
        "scope": "Finite exact checks support the quantified algebraic proof in FAMILY.md. No global native or supplier lower bound is inferred.",
    }
    (args.out / "CHECKS.json").write_text(json.dumps(checks, sort_keys=True, indent=2) + "\n")
    print(json.dumps(checks, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()

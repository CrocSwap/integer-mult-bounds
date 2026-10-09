#!/usr/bin/env python3
"""Search vector-linear, all-input completions on a fixed Fano topology.

Each former edge holds k independent bits. Every vertex may apply any binary
linear map on all 2k incident bits. Requiring the final map to be a complete
permutation forces every local square map to be invertible. There are no
zero-initialized bits and no appended decoder. A solver UNSAT/timeout is only
a discovery receipt, not an independently checked impossibility certificate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import z3
from fano_reuse import topologies


def synthesize(case, block, timeout_ms, canonical_edges=False):
    width = case["W"] * block
    solver = z3.SolverFor("QF_BV")
    solver.set(timeout=timeout_ms, random_seed=0)
    last = [z3.BitVecVal(1 << r, width) for r in range(width)]
    symbolic_gates = []
    for index, (a, b) in enumerate(case["pairs"]):
        roles = [block * r + j for r in (a, b) for j in range(block)]
        old = [last[r] for r in roles]
        coefficients = []
        for out, r in enumerate(roles):
            row = [z3.Bool(f"c_{index}_{out}_{j}") for j in range(len(roles))]
            coefficients.append(row)
            value = z3.BitVecVal(0, width)
            for coeff, operand in zip(row, old):
                value = value ^ z3.If(coeff, operand, z3.BitVecVal(0, width))
            current = z3.BitVec(f"g_{index}_{out}", width)
            solver.add(current == value)
            last[r] = current
        symbolic_gates.append((roles, coefficients))
        if canonical_edges:
            # Independent basis changes on each internal block are absorbed
            # into its adjacent GL(2k) vertices. A final free auxiliary block
            # can sort its unit vectors; the prescribed blocks are already
            # sorted. Thus row-reduced internal edge bases lose no existence
            # cases in this scalar model.
            for start in (0, block):
                values = [last[r] for r in roles[start:start + block]]
                pivots = [x & -x for x in values]
                for x in values:
                    solver.add(x != 0)
                for i in range(block - 1):
                    solver.add(z3.ULT(pivots[i], pivots[i + 1]))
                for i in range(block):
                    for j in range(block):
                        if i != j:
                            solver.add(values[i] & pivots[j] == 0)
    for row in last:
        solver.add(row != 0, row & (row - 1) == 0)
    solver.add(z3.Distinct(*last))
    for source, target in case["prescribed"].items():
        for j in range(block):
            solver.add(last[block * target + j] == 1 << (block * source + j))
    start = time.monotonic()
    status = solver.check()
    result = {"case_id": case["id"], "block": block, "W": width,
              "status": str(status), "elapsed_seconds": time.monotonic() - start,
              "solver": z3.get_version_string(), "timeout_ms": timeout_ms,
              "canonical_internal_edge_bases": canonical_edges,
              "scope": "Fixed balanced topology, arbitrary GL(2k,F2) gates and free auxiliary bit permutation; solver discovery only."}
    if status == z3.unknown:
        result["reason"] = solver.reason_unknown()
    if status != z3.sat:
        return result
    model = solver.model()
    rows = [1 << r for r in range(width)]
    gates = []
    for roles, coefficients in symbolic_gates:
        matrix = [[int(z3.is_true(model.eval(c, model_completion=True))) for c in row]
                  for row in coefficients]
        old = [rows[r] for r in roles]
        new = []
        for row in matrix:
            value = 0
            for c, operand in zip(row, old):
                if c:
                    value ^= operand
            new.append(value)
        for r, value in zip(roles, new):
            rows[r] = value
        gates.append({"roles": roles, "matrix": matrix})
    assert sorted(rows) == [1 << r for r in range(width)]
    rho = [rows.index(1 << r) for r in range(width)]
    assert all(rho[block * source + j] == block * target + j
               for source, target in case["prescribed"].items() for j in range(block))
    result.update(gates=gates, rho=rho, independently_replayed_all_columns=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block", type=int, default=2)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--case", type=int, action="append")
    parser.add_argument("--canonical-edges", action="store_true")
    args = parser.parse_args()
    assert 1 <= args.block <= 4
    cases = [c for c in topologies() if not c["routing"]["routable"]]
    if args.case is not None:
        cases = [c for c in cases if c["id"] in args.case]
    for case in cases:
        print(json.dumps(synthesize(case, args.block, args.timeout_ms, args.canonical_edges)), flush=True)


if __name__ == "__main__":
    main()

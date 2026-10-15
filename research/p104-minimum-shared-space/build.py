"""Optional deterministic rational witness discovery; not used for acceptance.

Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import need, sources
from verify import replay, verify_witness


def subtract(row, other, factor):
    for j, value in other.items():
        new = row.get(j, Q(0)) - factor * value
        if new:
            row[j] = new
        else:
            row.pop(j, None)


def build():
    trace = replay(sources(), [])
    pivots, witnesses, variables = {}, {}, []
    for target, ids in enumerate(trace["local_bases"]):
        for row_id in ids:
            coeff = trace["coefficients"][row_id]
            row = {8 * i + j: Q(trace["ports"][target][i]) * coeff[j]
                   for i in range(8) for j in range(8)
                   if trace["ports"][target][i] * coeff[j]}
            combination = {len(variables): Q(1)}
            variables.append((target, row_id))
            while row:
                pivot = min(row)
                factor = row[pivot]
                if pivot not in pivots:
                    pivots[pivot] = {j: v / factor for j, v in row.items()}
                    witnesses[pivot] = {j: v / factor for j, v in combination.items()}
                    break
                subtract(row, pivots[pivot], factor)
                subtract(combination, witnesses[pivot], factor)
    row, solution = {9 * i: Q(1) for i in range(8)}, {}
    while row:
        pivot = min(row)
        need(pivot in pivots, "no projector complement in this family")
        factor = row[pivot]
        subtract(row, pivots[pivot], factor)
        subtract(solution, witnesses[pivot], -factor)
    terms = []
    for index, weight in sorted(solution.items()):
        target, row_id = variables[index]
        cut, reg = trace["occurrences"][target][row_id]
        terms.append([target, cut, reg, str(weight)])
    result = {"schema": "p104-shared-complement/1", "terms": terms}
    # Acceptance still reconstructs these contacts independently of discovery.
    print("LINEAR_SYSTEM", len(variables), "variables", len(pivots), "rank",
          len(terms), "terms")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), "output already exists")
    result = build()
    with args.out.open("x") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")

#!/usr/bin/env python3
"""Emit the finite dyadic-run schedules; verification is in a separate file."""
from fractions import Fraction
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent


def runs(indices):
    out = []
    for j in indices:
        if out and out[-1][-1] + 1 == j:
            out[-1].append(j)
        else:
            out.append([j])
    return out


def schedule(indices):
    word = []
    for run in runs(indices):
        vertices = [-(1 << j) for j in reversed(run)] + [1 << j for j in run]
        previous = 0
        for vertex in vertices:
            word.extend([vertex - previous, "X"])
            previous = vertex
        word.append(-previous)
    return word


def lowering(k):
    a = Fraction(k, 4)

    def affine(target, diagonal, controls):
        return ["A", target, str(diagonal), [[i, str(v)] for i, v in controls]]

    return [
        affine(2, 1, [(0, -1)]),
        affine(3, 1, [(0, 1)]),
        affine(5, a, [(0, 1+a), (2, -a), (3, -a)]),
        ["C", 0, 5],
        affine(2, 1, [(0, 1)]),
        affine(3, 1, [(0, -1)]),
        affine(5, -1/a, [(0, 1/a-1), (2, 1), (3, 1)]),
    ]


def invoice(word):
    powers = sorted(set(k for k in word if type(k) is int))
    queries = sum(type(k) is int for k in word)
    return {"children": queries, "affines": 6*queries,
            "xor_scans": word.count("X"),
            "query_multiplicities": {str(k): word.count(k) for k in powers}}


def certificate():
    cases = []
    for mask in range(1, 64):
        indices = [j for j in range(6) if mask & (1 << j)]
        fused = schedule(indices)
        baseline = [op for j in indices for op in [-(1 << j), "X", 2 << j, "X", -(1 << j)]]
        cases.append({"mask": mask, "indices": indices, "word": fused,
                      "baseline": baseline, "invoice": invoice(fused),
                      "baseline_invoice": invoice(baseline)})
    powers = {k for case in cases for name in ["word", "baseline"]
              for k in case[name] if type(k) is int}
    powers |= {-k for k in powers}
    return {"format": "dyadic-query-runs-v1", "assignment_seed": 55,
            "domain": {"indices": list(range(6)), "masks": [1, 63]},
            "instruction_format": "integer k: Q(k) on target; X: target XOR source",
            "cases": cases,
            "lowerings": {str(k): lowering(k) for k in sorted(powers)}}


def encode(data):
    # One case per line keeps the literal finite schedule easy to inspect.
    compact = lambda x: json.dumps(x, sort_keys=True)
    lines = ["{"]
    for key in sorted(set(data) - {"cases", "lowerings"}):
        lines.append("  " + compact(key) + ": " + compact(data[key]) + ",")
    lines.append('  "cases": [')
    lines.extend("    " + compact(case) + ("," if i+1 < len(data["cases"]) else "")
                 for i, case in enumerate(data["cases"]))
    lines.append("  ],")
    lines.append('  "lowerings": {')
    items = list(data["lowerings"].items())
    lines.extend("    " + compact(key) + ": " + compact(value) +
                 ("," if i+1 < len(items) else "")
                 for i, (key, value) in enumerate(items))
    lines.extend(["  }", "}"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    (ROOT / "CERTIFICATE.json").write_text(encode(certificate()), encoding="utf-8")
    print("WROTE_DYADIC_QUERY_RUNS cases=63 seed=55")

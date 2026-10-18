#!/usr/bin/env python3
"""Choose rational echelon minors; verify.py checks integer determinants.

CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
Writes only a new explicitly requested file; never overwrites a certificate.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path

import verify


def choose_minor(matrix, available):
    basis, selected, pivots = [], [], []
    for index in available:
        row = list(map(Fraction, matrix[index]))
        for pivot, vector in zip(pivots, basis):
            coefficient = row[pivot]
            row = [x - coefficient * y for x, y in zip(row, vector)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            basis.append([x / scale for x in row])
            pivots.append(pivot)
            selected.append(index)
    # Separate rational Gaussian determinant, not verifier's Bareiss routine.
    a = [[Fraction(matrix[i][j]) for j in pivots] for i in selected]
    determinant = Fraction(1)
    for k in range(len(a)):
        pivot = next(i for i in range(k, len(a)) if a[i][k])
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            determinant = -determinant
        scale = a[k][k]
        determinant *= scale
        a[k] = [x / scale for x in a[k]]
        for i in range(k + 1, len(a)):
            factor = a[i][k]
            a[i] = [x - factor * y for x, y in zip(a[i], a[k])]
    verify.require(determinant.denominator == 1, "nonintegral minor")
    return {"rows": selected, "columns": pivots, "determinant": int(determinant)}


def build():
    verify.check_sources()
    g = verify.geometry()
    records = []
    for h in range(1, 512):
        complement = [t for t, label in enumerate(g["labels"]) if verify.parity(h & label)]
        old = [t for t in complement if t < 112]
        minor112 = choose_minor(g["C"], old)
        rank = len(minor112["rows"])
        zero = [j for j in range(8) if all(g["C"][t][j] == 0 for t in old)]
        verify.require((rank == 8 and not zero) or (rank == 7 and len(zero) == 1), "unexpected rank")
        records.append({"character": h, "rank112": rank, "kernel_axis": zero[0] if zero else None,
                        "minor112": minor112, "minor120": choose_minor(g["C"], complement)})
    return {"schema": "one-sided-padding-annihilators/v1", "characters": records}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = build()
    with args.output.open("x") as stream:
        stream.write('{"schema": "' + result["schema"] + '", "characters": [\n')
        stream.write(',\n'.join(json.dumps(row, separators=(",", ":")) for row in result["characters"]))
        stream.write('\n]}\n')
    print("WROTE_511_EXACT_MINOR_PAIRS", args.output)

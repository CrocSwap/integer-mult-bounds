#!/usr/bin/env python3
"""Direct integer-elimination oracle. Imports no primary verifier code. Apache-2.0."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path


SOURCE = "research/joint-query/certificate.json.gz"
DIGEST = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
BASE = (1, 2, 3, 4, 5, 6, 8, 12)
HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def determinant(matrix):
    """Fraction-free elimination, including row-pivot sign and exact division."""
    n = len(matrix)
    need(1 <= n <= 8 and all(len(row) == n for row in matrix), "matrix shape")
    work = [row[:] for row in matrix]
    previous, sign = 1, 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if work[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            work[k], work[pivot_row] = work[pivot_row], work[k]
            sign = -sign
        pivot = work[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                value = work[i][j] * pivot - work[i][k] * work[k][j]
                quotient, remainder = divmod(value, previous)
                need(remainder == 0, "nonexact Bareiss division")
                work[i][j] = quotient
            work[i][k] = 0
        previous = pivot
    return sign * work[-1][-1]


def adjugate_inverse(matrix):
    det = determinant(matrix)
    need(det != 0, "singular adjugate input")
    result = []
    for i in range(8):
        row = []
        for j in range(8):
            submatrix = [[matrix[a][b] for b in range(8) if b != i]
                         for a in range(8) if a != j]
            cofactor = (-1) ** (i + j) * determinant(submatrix)
            row.append(str(Fraction(cofactor, det)))
        result.append(row)
    return result


def direct_census(matrix, ordinary):
    outside = tuple(p for p in ordinary if p not in BASE)
    need(len(outside) == 88 and len(set(ordinary)) == 96, "ordinary alphabet")
    histograms = []
    for distance in range(3):
        counts = Counter()
        for removed in combinations(BASE, distance):
            retained = tuple(p for p in BASE if p not in removed)
            for inserted in combinations(outside, distance):
                ports = retained + inserted
                square = [[row[p] for p in ports] for row in matrix]
                counts[abs(determinant(square))] += 1
        histograms.append({str(d): count for d, count in sorted(counts.items())})
    return histograms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=HERE.parents[1])
    parser.add_argument("--receipt", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    path = args.repo / SOURCE
    need(path.stat().st_size <= 8_000_000, "oversize input")
    raw = path.read_bytes()
    need(sha256(raw).hexdigest() == DIGEST, "oracle source pin differs")
    packet = json.loads(gzip.decompress(raw))
    matrix = [[int(row.get(str(p), "0")) for p in range(112)]
              for row in packet["R_rows"]]
    need(len(matrix) == 8, "query dimension")
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    histograms = direct_census(matrix, tuple(packet["U_ports"]))
    need(histograms == receipt["absolute_determinant_histograms_by_distance"],
         "direct census and determinant lemma disagree")
    certificate = receipt["certificate"]
    for prefix in ("base", "bad"):
        ports = certificate[prefix + "_ports_ordered"]
        need(len(ports) == len(set(ports)) == 8, "certificate port shape")
        square = [[row[p] for p in ports] for row in matrix]
        need(determinant(square) == certificate[prefix + "_determinant"],
             "direct witness determinant disagrees")
        need(adjugate_inverse(square) == certificate[prefix + "_inverse"],
             "cofactor inverse disagrees")
    need(determinant([[0, 1], [1, 0]]) == -1, "pivot-sign control")
    need(determinant([[1, 2], [2, 4]]) == 0, "singular control")
    print("PASS_QQ16_DIRECT_MINOR_ORACLE sets=107889 full_census_and_cofactor_inverses")


if __name__ == "__main__":
    main()

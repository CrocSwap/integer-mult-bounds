#!/usr/bin/env python3
"""Independent finite-prefix/analytic-tail certificate for fixed bucket roles."""
from fractions import Fraction as F
from hashlib import sha256
from math import gcd
from pathlib import Path
import argparse
import json


def need(condition, message):
    if not condition:
        raise ArithmeticError(message)


def ceil(x):
    return -(-x.numerator // x.denominator)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    source = args.source.resolve()
    manifest = json.loads((source / "SOURCE-BINDINGS.json").read_text())
    for module, record in manifest["modules"].items():
        data = (source / "sources" / record["file"]).read_bytes()
        need(len(data) == record["size"] and sha256(data).hexdigest() == record["sha256"],
             "source mismatch: " + module)
    coefficients = [F(1), F(1, 2)] + [F(1, 3)] * 12 + [F(1, 9)] * 4 + [F(1, 19), F(1, 20)]
    small_cases, equality_cases, thresholds = [], [], []
    for k in range(2, 21):
        if gcd(k, 3) != 1:
            continue
        for j in range(k):
            alpha = coefficients[j]
            need(alpha >= F(1, k), "coefficient cannot bound the asymptotic limit")
            if alpha == F(1, k):
                need(j == k - 1, "unhandled equality case")
                # C_(k-1)=q-ceil(q-q/k)=floor(q/k) for every integer q.
                equality_cases.append([k, j])
                continue
            threshold = ceil(1 / (alpha - F(1, k)))
            thresholds.append(threshold)
            # For every real q>=threshold, C_j<q/k+1<=alpha*q.
            # Below threshold, enumerate the complete positive 3-power prefix.
            q = 3
            while q < threshold:
                distribution = [0] * k
                for value in range(q):
                    distribution[(-pow(q, -1, k) * value) % k] += 1
                count = distribution[j]
                difference = ceil(F((j + 1) * q, k)) - ceil(F(j * q, k))
                need(count == difference, "independent residue allocation differs")
                need(F(count, q) <= alpha, "finite prefix exceeds role cap")
                small_cases.append([k, j, q, count])
                q *= 3
    need(equality_cases == [[2, 1], [19, 18], [20, 19]], "equality classification changed")
    need(max(thresholds) == 380, "tail threshold changed")
    total = 2 + sum(coefficients)
    need(total == F(27521, 3420) < 9, "uniform total is incorrect")
    need(F(ceil(F(14 * 3, 20)) - ceil(F(13 * 3, 20)), 3) > F(1, 4),
         "undersized coefficient control escaped")
    # Independent exact arithmetic for root padding, residuals and the
    # serial rectangle. This does not simulate a native child computation.
    roots = 0
    for rows in (1, 2, 3, 4, 8, 9, 10, 26, 27, 28, 101):
        extent, k = 1, 0
        while extent < rows:
            extent *= 3
            k += 1
        padded = ((extent + rows - 1) // rows) * rows
        need(extent <= padded < 2 * extent, "padded role exceeds two volumes")
        for width in (1, 2, 7):
            for e in (2 * k + width + 1, 2 * k + 3 * width + 2):
                c, r = divmod(e - k, width)
                need(2 * c * width + 2 * r + k == 2 * e - k,
                     "child residual volume identity failed")
                need(2 * F(padded, extent) + 3 < 7, "root role total failed")
                roots += 1
    rectangles = 0
    for bits in range(1, 65):
        a, b = 1 << bits, 1
        while b < a:
            b *= 3
        need(a <= b < 3 * a, "least ternary power bound failed")
        need(2 * F(b * b, a * a) < 18, "rectangle role total failed")
        rectangles += 1
    report = {"status": "PASS_INDEPENDENT_DIRECT_ROLE_ENVELOPE",
              "proof_sha256": sha256((source / "PROOF.md").read_bytes()).hexdigest(),
              "authenticated_modules": len(manifest["modules"]),
              "method": "Analytic ceil-gap tail plus full finite 3-power prefix; no author scientific imports",
              "small_bucket_cases": len(small_cases), "largest_tail_threshold": max(thresholds),
              "equality_cases": equality_cases, "root_identities": roots,
              "rectangle_identities": rectangles, "whole_coefficient": str(total),
              "negative_control": "bucket13,k20,q3 rejects1/4", "prefix_witnesses": small_cases}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], len(small_cases), roots, rectangles)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact certificates for four residual asymmetric C5 cost floors.

The scalar-factor reduction is in README.md. LP discovers candidate
certificates; replay uses only integer/Fraction arithmetic.
"""

import argparse
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/c5-dyadic-decoder-gate/inputs/"
HASHES = {
    "DATA-PHASES.json.gz": "682092a4c656e0be4bdaa419783440772a80ae875cca4845aea2067927b560f6",
    "MATCHING.json": "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1",
}
CORES = ((3, 10, 4, 6, 13), (3, 10, 12, 23, 13),
         (6, 13, 23, 54, 26), (14, 24, 47, 18, 55))
BLOCKS = (1, 2, 4, 8, 16, 5, 9, 10, 18, 20)
RANKS = (2,) * 5 + (4,) * 5


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(weights, values):
    return sum(a * b for a, b in zip(weights, values, strict=True))


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def geometry(root):
    raw = {}
    for name, expected in HASHES.items():
        path = root / INPUT / name
        require(path.is_file() and not path.is_symlink(), "regular scientific input")
        require(path.stat().st_size < 2_000_000, "bounded scientific input")
        raw[name] = path.read_bytes()
        require(hashlib.sha256(raw[name]).hexdigest() == expected, "scientific input SHA256")
    payload = gzip.decompress(raw["DATA-PHASES.json.gz"])
    require(len(payload) < 2_000_000, "bounded geometry payload")
    recipes = json.loads(payload)["recipes"]
    labels = {row["port"]: row["q"] for row in recipes}
    require(len(recipes) == 112 and sorted(labels) == list(range(112)), "112 ports")
    require(all(type(q) is int and 0 < q < 512 for q in labels.values()), "binary labels")
    matching = json.loads(raw["MATCHING.json"])["matching"]
    require(len(matching) == 56 and all(len(p) == 2 for p in matching), "56 planes")
    require(sorted(p for pair in matching for p in pair) == list(range(112)), "partition")
    return tuple(tuple(labels[p] for p in pair) for pair in matching)


def pairing_rank(left, right):
    pivots = {}
    for label in left:
        row = sum(((label & other).bit_count() % 2) << j for j, other in enumerate(right))
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def check_cycle(local):
    for i, plane in enumerate(local):
        require([[(a & b).bit_count() % 2 for b in plane] for a in plane]
                == [[1, 0], [0, 1]], "plane Gram I2")
        for j in range(i + 1, 5):
            adjacent = j - i in (1, 4)
            require((pairing_rank(plane, local[j]) == 0) == adjacent, "physical C5 order")


def support_rows(local):
    bases = [tuple(q for i, p in enumerate(local) if mask >> i & 1 for q in p)
             for mask in range(32)]
    return [(a, b, pairing_rank(bases[a], bases[b]),
             tuple(int(bool(a & h) and bool(b & h)) for h in BLOCKS))
            for a in range(32) for b in range(32)]


def trace_consistent(a, b, hits, tight):
    equations = []
    for i in range(5):
        if not (a & b) >> i & 1:
            equations.append([Fraction(int(i == j)) for j in range(5)] + [Fraction(0)])
    for h, value, active in zip(BLOCKS, hits, tight, strict=True):
        if active:
            equations.append([Fraction((h >> j) & 1) for j in range(5)] + [Fraction(value)])
    pivot_row = 0
    for col in range(5):
        pivot = next((r for r in range(pivot_row, len(equations)) if equations[r][col]), None)
        if pivot is None:
            continue
        equations[pivot_row], equations[pivot] = equations[pivot], equations[pivot_row]
        value = equations[pivot_row][col]
        equations[pivot_row] = [x / value for x in equations[pivot_row]]
        for r in range(len(equations)):
            if r != pivot_row and equations[r][col]:
                value = equations[r][col]
                equations[r] = [x - value * y for x, y in
                                zip(equations[r], equations[pivot_row], strict=True)]
        pivot_row += 1
    return not any(not any(row[:5]) and row[5] for row in equations)


def slack_vectors(weights, budget):
    if not weights:
        yield ()
        return
    for value in range(budget // weights[0] + 1 if weights[0] else 1):
        for rest in slack_vectors(weights[1:], budget - value * weights[0]):
            yield (value,) + rest


def check_case(rows, weights, scale, case):
    excess = tuple(case["excess"])
    target = tuple(r + e for r, e in zip(RANKS, excess, strict=True))
    budget = scale * 19 - dot(weights, target)
    tight = [bool(w) and not e for w, e in zip(weights, excess, strict=True)]
    dual, denominator = case["dual_weights"], case["dual_scale"]
    require(len(dual) == 10 and all(type(v) is int for v in dual), "integer dual")
    require(type(denominator) is int and denominator > 0, "positive dual scale")
    require(all(w or y >= 0 for w, y in zip(weights, dual, strict=True)),
            "nonnegative dual on lower-bound-only counts")
    require(dot(dual, target) >= 20 * denominator, "separating bound at least20")
    admitted = 0
    for a, b, cost, hits in rows:
        defect = scale * cost - dot(weights, hits)
        if defect <= budget and trace_consistent(a, b, hits, tight):
            admitted += 1
            require(dot(dual, hits) <= denominator * cost, "admissible-term dual inequality")
    require(admitted == case["admissible_support_pairs"], "admissible pair count")
    return admitted


def attainment(local):
    matrix = [[0] * 10 for _ in range(10)]
    cost = 0
    for i in range(5):
        ports = (2 * i + 1, 2 * ((i + 1) % 5))
        complete = local[i] + local[(i + 1) % 5]
        cost += pairing_rank(complete, complete)
        for a in ports:
            for b in ports:
                matrix[a][b] += 1
    for a in range(10):
        for b in range(10):
            if a // 2 == b // 2 or pairing_rank(local[a // 2], local[b // 2]):
                require(matrix[a][b] == int(a == b), "complete scalar fit")
    require(cost == 20, "attainment cost20")


def verify(root=ROOT, certificate=None):
    certificate = json.loads((HERE / "CERTIFICATE.json").read_bytes()) if certificate is None else certificate
    require(certificate["schema_version"] == 1 and tuple(certificate["blocks"]) == BLOCKS,
            "certificate schema and block order")
    cores = certificate["cores"]
    require(tuple(tuple(row["core"]) for row in cores) == CORES, "four exact residuals")
    planes = geometry(root)
    total_cases = total_pairs = 0
    for entry in cores:
        local = tuple(planes[p] for p in entry["core"])
        check_cycle(local)
        rows = support_rows(local)
        require(digest([row[2] for row in rows]) == entry["tariff_sha256"], "tariff receipt")
        weights, scale = entry["cover_weights"], entry["cover_scale"]
        require(len(weights) == 10 and all(type(w) is int and w >= 0 for w in weights),
                "nonnegative integer cover")
        require(type(scale) is int and scale > 0, "positive cover scale")
        require(all(dot(weights, h) <= scale * c for _, _, c, h in rows), "cover inequality")
        slack = scale * 19 - dot(weights, RANKS)
        require(0 <= slack <= 2, "bounded residual slack")
        expected = set(slack_vectors(weights, slack))
        actual = [tuple(case["excess"]) for case in entry["cases"]]
        require(len(actual) == len(set(actual)) and set(actual) == expected, "complete slack cases")
        for case in entry["cases"]:
            total_pairs += check_case(rows, weights, scale, case)
            total_cases += 1
        attainment(local)
    require(total_cases == 57, "57 exact cases")
    return {"cores": 4, "tariffs": 4096, "slack_cases": total_cases,
            "admissible_term_checks": total_pairs, "sharp_cost": 20, "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = verify(args.root)
    print("PASS_C5_FOUR_RESIDUAL_FLOORS", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

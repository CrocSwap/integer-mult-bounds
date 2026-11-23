#!/usr/bin/env python3
"""Review emitted routes using fraction-free pivot minors, without constructor imports."""
from fractions import Fraction as F
from hashlib import sha1, sha256
from math import gcd
from pathlib import Path
import argparse
import gzip
import json


def need(condition, message):
    if not condition:
        raise ArithmeticError(message)


def determinant(matrix):
    """Bareiss fraction-free determinant with independently chosen pivot rows."""
    if not matrix:
        return 1
    a = [list(row) for row in matrix]
    sign, divisor, n = 1, 1, len(a)
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if a[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = pivot * a[i][j] - a[i][k] * a[k][j]
                need(numerator % divisor == 0, "Bareiss division ceased to be exact")
                a[i][j] = numerator // divisor
            a[i][k] = 0
        divisor = pivot
    return sign * a[-1][-1]


def apply_word(word, matrix):
    a = [[F(x) for x in row] for row in matrix]
    for operation in word:
        if operation[0] == "swap":
            _, i, j = operation
            a[i], a[j] = a[j], a[i]
        elif operation[0] == "scale":
            _, i, coefficient = operation
            a[i] = [F(coefficient) * x for x in a[i]]
        elif operation[0] == "add":
            _, i, j, coefficient = operation
            a[i] = [x + F(coefficient) * y for x, y in zip(a[i], a[j], strict=True)]
        else:
            raise ArithmeticError("unknown route opcode")
    return a


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.source.resolve()
    proof_sha = sha256((root / "PROOF.md").read_bytes()).hexdigest()
    need(proof_sha == "cbf42e276c2d1b25d72064801b6f0c0fb1ecab2d7cb0f771640a8bc4301dc14b",
         "reviewed proof changed")
    origins = json.loads((root / "ORIGINS.json").read_text())["files"]
    for item in origins:
        raw = (root / item["local"]).read_bytes()
        need(len(raw) == item["bytes"] and sha256(raw).hexdigest() == item["sha256"],
             "source SHA binding failed: " + item["local"])
        if item.get("git_blob") is not None:
            need(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == item["git_blob"],
                 "source Git binding failed: " + item["local"])
    raw = (root / "DESCRIPTORS.json.gz").read_bytes()
    need(sha256(raw).hexdigest() == "0b3c8aea707c92c06d7efc85426ade1f8f48d0729af09a5decb86f8c57741502",
         "descriptor catalogue changed")
    catalogue = json.loads(gzip.decompress(raw))
    matrices = {item["id"]: [[F(x) for x in row] for row in item["matrix"]]
                for item in catalogue["matrices"]}
    minors = products = scalings = additions = nonunit_additions = 0
    boundary = {}
    for route in catalogue["routes"]:
        matrix = matrices[route["matrix_id"]]
        n, q = len(matrix), route["q"]
        identity = [[F(i == j) for j in range(n)] for i in range(n)]
        transpose = list(map(list, zip(*matrix)))
        need(apply_word(route["forward"], identity) == transpose, "forward transpose/order differs")
        need(apply_word(route["inverse"], transpose) == identity, "inverse order differs")
        products += 2
        denominator = max(x.denominator for row in matrix for x in row)
        integral = [[int(x * denominator) for x in row] for row in transpose]
        maximum = max(1, *(abs(x) for row in integral for x in row))
        bound = denominator.bit_length() - 1 + n * (maximum.bit_length() + n.bit_length()) + 1
        need(bound == route["coefficient_bits_bound"], "input height cap differs")
        row_order, previous = list(range(n)), 1
        for k, pivot in enumerate(route["pivots"]):
            chosen = pivot["selected_row"]
            row_order[k], row_order[chosen] = row_order[chosen], row_order[k]
            minor = determinant([[integral[i][j] for j in range(k + 1)]
                                 for i in row_order[:k + 1]])
            need(gcd(minor, q) == 1, "selected pivot minor is not a q-unit")
            need(F(minor, denominator * previous) == F(pivot["value"]),
                 "pivot is not the claimed fraction-free minor ratio")
            previous = minor
            minors += 1
        for word in (route["forward"], route["inverse"]):
            counts = {"swap": 0, "add": 0, "scale": 0}
            for operation in word:
                kind = operation[0]
                counts[kind] += 1
                if kind == "swap":
                    continue
                coefficient = F(operation[-1])
                need(gcd(coefficient.denominator, q) == 1, "non-q-integral coefficient")
                need(abs(coefficient.numerator) < 1 << bound and coefficient.denominator < 1 << bound,
                     "coefficient exceeded universal minor-height cap")
                if kind == "scale":
                    need(gcd(coefficient.numerator, q) == 1, "nonunit scale")
                    scalings += 1
                else:
                    additions += 1
                    nonunit_additions += gcd(coefficient.numerator, q) != 1
            need(counts["add"] <= n * (n - 1) and counts["scale"] <= n and counts["swap"] <= n,
                 "elementary record count failed")
            need(n * (2 * counts["add"] + counts["swap"]) <= 2 * n**3,
                 "ordinary interchange invoice failed")
            need(n * counts["add"] + n * n <= n**3, "carry-inclusive shift invoice failed")
            need(n * counts["scale"] <= n * n, "rational scaling invoice failed")
        if route["matrix_id"] == "order-control" and q == 3:
            need(apply_word(list(reversed(route["forward"])), identity) != transpose,
                 "wrong-order control failed to discriminate")
            boundary["reversed-forward-order"] = "rejected"
        if route["matrix_id"] == "nonunit-shear-control" and q == 3:
            stripped = [op for op in route["forward"] if op[0] != "add" or F(op[-1]).numerator % q]
            wrong = apply_word(stripped, identity)
            need(any((wrong[i][j] - transpose[i][j]).numerator % (q*q)
                     for i in range(n) for j in range(n)),
                 "discarded-low-zero-shear control did not change the q-square action")
            boundary["discarded-low-zero-shear"] = "rejected at q^2"
    composite = [[3, 5], [1, 2]]
    need(determinant(composite) == 1 and all(gcd(x, 15) != 1 for x in composite[0]),
         "composite-modulus pivot boundary failed")
    boundary["composite-pivot"] = "determinant one does not supply an entry-unit pivot mod15"
    need(nonunit_additions > 0, "source alphabet control absent")
    report = {"status": "PASS_INDEPENDENT_DYADIC_ROUTE_REVIEW", "proof_sha256": proof_sha,
              "source_files": len(origins), "descriptors": len(catalogue["routes"]),
              "exact_word_products": products, "fraction_free_pivot_minors": minors,
              "unit_scalings_checked": scalings, "additions_checked": additions,
              "nonunit_addition_numerators_retained": nonunit_additions,
              "controls": boundary,
              "scope": "Independent minor/word/count corroboration of the written local-ring construction; no physical execution"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], report["descriptors"], minors, products)


if __name__ == "__main__":
    main()

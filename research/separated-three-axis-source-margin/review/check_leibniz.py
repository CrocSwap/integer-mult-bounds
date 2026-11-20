#!/usr/bin/env python3
"""Independent Kronecker/Leibniz reconstruction with packed exponents.

Imports no primary-verifier code. Distinct arithmetic path, same AI worker;
this is not a claim of independent human or formal-kernel review.
Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
SPDX-License-Identifier: Apache-2.0
"""
from collections import defaultdict
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import json

ORDER = (0, 1, 2, 4, 6, 5, 3, 7)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def packed_tensor():
    # Matrix entries are monomial codes. Adding codes multiplies monomials.
    # Six base-16 digits record the exponents of u,v,x,y,r,z respectively.
    a = [[0]]
    for axis in range(3):
        b = [[0, 1 << (8*axis)], [1 << (8*axis+4), 0]]
        a = [[x+y for x in ra for y in rb] for ra in a for rb in b]
    return a


def packed_displacement(order):
    tensor = packed_tensor()
    source = [[tensor[r][c] for c in order] for r in order]
    result = []
    for i in range(8):
        row = []
        for j in range(8):
            first = source[i][j]
            if not i or not j:
                row.append([(first, 1)])
            else:
                second = source[i-1][j-1]
                row.append([] if first == second else [(first, 1), (second, -1)])
        result.append(row)
    return result


def leibniz(order):
    matrix = packed_displacement(order)
    total = defaultdict(int)
    nonzero_products = expanded_count = 0
    for permutation in permutations(range(8)):
        entries = [matrix[row][col] for row, col in enumerate(permutation)]
        if any(not entry for entry in entries):
            continue
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(8) for j in range(i+1, 8))
        terms = [(0, -1 if inversions % 2 else 1)]
        for entry in entries:
            terms = [(code+key, sign*coefficient)
                     for code, sign in terms for key, coefficient in entry]
        for code, sign in terms:
            total[code] += sign
        nonzero_products += 1
        expanded_count += len(terms)
    collected = {tuple((code >> (4*axis)) & 15 for axis in range(6)): value
                 for code, value in total.items() if value}
    # Each product has eight entries, each individual exponent <= 1.
    # Consequently exponent addition never carries in base 16.
    need(all(max(key) <= 8 for key in collected), "packed exponents fit without carry")
    return collected, nonzero_products, expanded_count


def digest(poly):
    rows = [[list(key), value] for key, value in sorted(poly.items())]
    return sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def main():
    expected = json.loads((Path(__file__).resolve().parents[1]/"RESULT.json").read_text())
    rows = []
    for order, field in ((ORDER, "polynomial_sha256"),
                         (tuple(reversed(ORDER)), "reverse_polynomial_sha256")):
        poly, products, expanded = leibniz(order)
        need(len(poly) == 7529, "complete nonzero polynomial term count")
        need(digest(poly) == expected["polynomial"][field], "whole polynomial dictionary equality")
        weighted = sum(abs(value)*(1 << (key[1]+key[3]+key[5]))
                       for key, value in poly.items() if key[1]+key[3]+key[5] >= 3)
        need(weighted == 7682848, "independent exact weighted remainder")
        need(products == 16687 and expanded == 1186624, "literal Leibniz work coverage")
        mutant = poly.copy()
        mutant[min(mutant)] += 1
        need(digest(mutant) != digest(poly), "one-coefficient mutation is rejected")
        rows.append({"order": order, "nonzero_permutation_products": products,
                     "expanded_signed_monomials": expanded, "nonzero_terms": len(poly),
                     "polynomial_sha256": digest(poly), "weighted_remainder_mass": weighted})
    print(json.dumps({
        "status": "PASS_SEPARATED_MARGIN_LEIBNIZ_REVIEW", "orders": rows,
        "negative_controls": ["one changed coefficient fails full-dictionary authentication"],
        "scope": "Independent finite algebra algorithm in same AI worker; analytic source proof remains separate."
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

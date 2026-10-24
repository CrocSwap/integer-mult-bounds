#!/usr/bin/env python3
"""Check a dyadic centre code and its complete scalar word."""

import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def product(a, b):
    bt = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, column))
             for column in bt] for row in a]


def determinant(a):
    a = [row[:] for row in a]
    answer = F(1)
    for j in range(len(a)):
        p = next(i for i in range(j, len(a)) if a[i][j])
        if p != j:
            a[j], a[p] = a[p], a[j]
            answer = -answer
        pivot = a[j][j]
        answer *= pivot
        for i in range(j + 1, len(a)):
            multiple = a[i][j] / pivot
            a[i] = [x - multiple * y for x, y in zip(a[i], a[j])]
    return answer


def butterfly(word, a, b):
    word.extend((("add", a, b, F(1)),
                 ("scale", b, None, F(-2)),
                 ("add", b, a, F(1))))


def make_word(k):
    word = []
    stride = 1
    while stride < k:
        for start in range(0, k, 2 * stride):
            for offset in range(stride):
                butterfly(word, start + offset, start + offset + stride)
        stride *= 2
    s, t, d, b = 0, k, k + 1, k + 2
    butterfly(word, t, d)
    word.extend((("add", s, b, F(-1)),
                 ("add", t, s, F(1)),
                 ("scale", t, None, F(-1)),
                 ("add", b, t, F(k, 2)),
                 ("add", b, s, F(k + 2, 4)),
                 ("scale", b, None, F(-1))))
    butterfly(word, s, b)
    return word


def inverse_word(word):
    return [(op, target, source, -c if op == "add" else 1 / c)
            for op, target, source, c in reversed(word)]


def replay(word, n):
    a = identity(n)
    price, height, peak = 0, 0, F(1)
    for op, target, source, c in word:
        numerator, denominator = abs(c.numerator), c.denominator
        require(numerator and not denominator & (denominator - 1),
                "A coefficient is not nonzero dyadic.")
        if op == "add":
            require(source != target, "An ADD uses the same field twice.")
            a[target] = [x + c * y for x, y in zip(a[target], a[source])]
            price += 2 * (1 + numerator.bit_length()
                          + numerator.bit_count() + denominator.bit_length())
        else:
            require(op == "scale" and not numerator & (numerator - 1),
                    "A scale is not a signed power of two.")
            a[target] = [c * x for x in a[target]]
            price += 2 * (abs(numerator.bit_length() - denominator.bit_length())
                          + (c < 0))
        peak = max(peak, sum(map(abs, a[target])))
        for value in a[target]:
            denominator = value.denominator
            require(not denominator & (denominator - 1),
                    "An intermediate coefficient is not dyadic.")
            height = max(height, denominator.bit_length() - 1)
    return a, {"scalar_price": price, "instructions": len(word),
               "prefix_row_one_norm": str(peak), "binary_height": height}


def closed_matrix(k):
    n = k + 4
    a = [[F(0) for _ in range(n)] for _ in range(n)]
    for i in range(1, k):
        for j in range(k):
            a[i][j] = F((-1) ** ((i & j).bit_count()))
    for j in range(k):
        a[0][j], a[k][j], a[k + 2][j] = F(k + 2, 4), F(-1), F(6 - k, 4)
    for j in (k, k + 1):
        a[0][j], a[k][j], a[k + 2][j] = F(k, 2), F(-1), F(-k, 2)
    a[0][k + 2] = F(-k - 6, 4)
    a[k][k + 2] = F(1)
    a[k + 1][k], a[k + 1][k + 1] = F(1), F(-1)
    a[k + 2][k + 2] = F(k - 2, 4)
    a[k + 3][k + 3] = F(1)
    return a


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    results = []
    for r in range(7):
        k, n = 2 ** r, 2 ** r + 4
        word = make_word(k)
        forward, forward_bill = replay(word, n + 4)
        backward, backward_bill = replay(inverse_word(word), n + 4)
        code = closed_matrix(k)
        extended = [row + [F(0)] * 4 for row in code] + identity(n + 4)[n:]
        require(forward == extended, "The literal word differs from the closed matrix.")
        eye = identity(n + 4)
        require(product(forward, backward) == product(backward, forward) == eye,
                "A complete inverse order fails.")
        metric = [F(1)] * (k + 2) + [F(-k)] * 2
        wanted_gram = [F(-2 * k)] + [F(k)] * (k - 1) + [F(2), F(2), F(2 * k), F(-k)]
        gram = product([[x * metric[j] for j, x in enumerate(row)] for row in code],
                       list(zip(*code)))
        require(gram == [[wanted_gram[i] if i == j else F(0) for j in range(n)]
                         for i in range(n)], "The diagonal metric law fails.")
        u = [F(1)] * (k + 2) + [F(k), F(0)]
        ell = [F(-1)] * (k + 2) + [F(1), F(0)]
        reflection = [[F(i == j) + u[i] * ell[j] for j in range(n)] for i in range(n)]
        require(product(reflection, reflection) == identity(n), "The response is not an involution.")
        diagonalized = [row[:] for row in code]
        diagonalized[k] = [-x for x in diagonalized[k]]
        require(code[k] == ell and product(code, reflection) == diagonalized,
                "The selected centre or ordinary invariant rows differ.")
        require(determinant(code) ** 2 == 16 * k ** k, "The determinant formula fails.")
        expected_price = 86 if r == 0 else 96 if r == 1 else 10 * k * r + 76 + 4 * r
        require(forward_bill["scalar_price"] == backward_bill["scalar_price"] == expected_price,
                "The complete scalar price differs from the formula.")
        require(F(forward_bill["prefix_row_one_norm"]) <= 4 * (k + 1) * max(k, 2)
                and F(backward_bill["prefix_row_one_norm"]) <= 2 * (k + 5),
                "A prefix norm exceeds the proved bound.")
        require(forward_bill["binary_height"] <= 2
                and backward_bill["binary_height"] <= max(r, 1) + 3,
                "A binary height exceeds the proved bound.")
        require(replay(word[1:], n + 4)[0] != extended, "The missing-gate control did not fail.")
        results.append({"k": k, "n": n, "arbitrary_complex_columns": n + 4,
                        "unchanged_borrowed_columns": 4,
                        "determinant": str(determinant(code)),
                        "forward": forward_bill, "inverse": backward_bill})
    output = {"status": "PASS_SIGNED_METRIC_DYADIC_FAMILY",
              "engine": "Independent Fraction matrices; no producer imports.",
              "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "checks": results,
              "scope": "Common-frame scalar completion. Native layout and recursive hosting are separate."}
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

"""Exact finite corroboration of the independent-four guard theorem."""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import comb
from pathlib import Path


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def field_product(a, b, q):
    if q != 4:
        return a * b % q
    value = 0
    for _ in range(2):
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return value


def field_tables(q):
    require(q in (2, 3, 4, 5, 7), "unsupported finite check field")
    add = tuple(tuple(a ^ b if q == 4 else (a + b) % q
                      for b in range(q)) for a in range(q))
    mul = tuple(tuple(field_product(a, b, q) for b in range(q))
                for a in range(q))
    neg = tuple(next(b for b in range(q) if add[a][b] == 0)
                for a in range(q))
    inv = (0,) + tuple(next(b for b in range(1, q) if mul[a][b] == 1)
                       for a in range(1, q))
    return add, mul, neg, inv


def normalize(vector, mul, inv):
    scale = inv[next(x for x in vector if x)]
    return tuple(mul[scale][x] for x in vector)


def dot(left, right, add, mul):
    value = 0
    for a, b in zip(left, right, strict=True):
        value = add[value][mul[a][b]]
    return value


def strata(q):
    add, mul, _, inv = field_tables(q)
    lines = {normalize(v + (0,), mul, inv)
             for v in product(range(q), repeat=3) if any(v)}
    planes = set()
    for v in product(range(q), repeat=4):
        if any(v) and dot(v, (1, 1, 1, 1), add, mul) == 0:
            planes.add(normalize(v, mul, inv))
    line_counts, plane_counts = Counter(), Counter()
    for v in sorted(lines):
        support = len(set(v))
        h = sum(all(add[x][mul[y][a]] for a in v)
                for x, y in product(range(q), repeat=2))
        require(h == (q - 1) * (q + 1 - support), "line full support")
        line_counts[support] += 1
    for normal in sorted(planes):
        support = sum(a != 0 for a in normal)
        h = sum(dot(normal, x, add, mul) == 0
                for x in product(range(1, q), repeat=4))
        expected = (q - 1) ** (4 - support)
        expected *= ((q - 1) ** support + (-1) ** support * (q - 1)) // q
        require(h == expected, "plane full support")
        plane_counts[support] += 1
    expected_lines = {2: 7, 3: 6 * (q - 2), 4: (q - 2) * (q - 3)}
    expected_planes = {2: 6, 3: 4 * (q - 2), 4: q * q - 3 * q + 3}
    require(dict(line_counts) == {s: n for s, n in expected_lines.items() if n},
            "projective quotient strata")
    require(dict(plane_counts) == {s: n for s, n in expected_planes.items() if n},
            "dual hyperplane strata")
    require(len(lines) == len(planes) == q * q + q + 1, "projective counts")
    return {"q": q, "lines": len(lines), "planes": len(planes)}


def formula_terms(q, d):
    require(isinstance(q, int) and q >= 2 and isinstance(d, int) and d >= 3,
            "formula domain requires integers q >= 2, d >= 3")
    a = q + (q - 1) ** 2
    line_counts = (7, 6 * (q - 2), (q - 2) * (q - 3))
    plane_counts = (6, 4 * (q - 2), q * q - 3 * q + 3)
    line_sum = plane_sum = 0
    for s, n2, n3 in zip(range(2, 5), line_counts, plane_counts, strict=True):
        h3 = (q - 1) ** (4 - s)
        h3 *= ((q - 1) ** s + (-1) ** s * (q - 1)) // q
        line_sum += n2 * (q * q + (q - 1) ** 2 * (q + 1 - s)) ** d
        plane_sum += n3 * (q ** 3 + (q - 1) * h3) ** d
    return (q ** 4 + (q - 1) ** 5) ** d, plane_sum, q * line_sum, q ** 3 * a ** d


def joint_probability(q, d):
    top, planes, lines, bottom = formula_terms(q, d)
    denominator = (q ** (d + 1) - 1) * q ** d
    for i in range(3):
        denominator *= q ** d - q ** i
    return Fraction((q - 1) * (top - planes + lines - bottom), denominator)


def marginal(q, d):
    return Fraction((q - 1) * (q * q - q + 1) ** d,
                    (q ** (d + 1) - 1) * q ** d)


def finite_tail():
    rows, comparisons = [], []
    fields = (3, 4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23)
    for q in fields:
        t = Fraction(q * q - q + 1, q * q)
        base = q * t ** 4
        require(base > 1, "tail must persist")
        first = next((d for d in range(3, 128)
                      if Fraction(3, q) * Fraction(q - 1, q) ** 4 * base ** d
                      > q * q + q + 1), None)
        require(first is not None, "bounded tail search exhausted")
        ratios = []
        for d in range(3, first):
            ratio = joint_probability(q, d) / marginal(q, d) ** 4
            require(ratio > 1, f"four-way sign at {(q, d)}")
            ratios.append(ratio)
            comparisons.append({"q": q, "d": d,
                                "ratio": [ratio.numerator, ratio.denominator]})
        rows.append({"q": q, "d0": first, "exceptions": len(ratios)})
    require(len(comparisons) == 56, "finite exception domain")
    require(Fraction(3, 4) ** 4 < Fraction(1, 2), "binary last-coordinate bound")
    # At q >= 25, 3q^2-48q > q^2+q+1. Its difference increases there.
    require(2 * 25 ** 2 - 49 * 25 - 1 > 0, "uniform tail endpoint")
    require(4 * Fraction(3, 4) ** 4 > 1, "uniform tail base")
    return rows, comparisons


def cross(left, right, add, mul, neg):
    a, b, c = left
    x, y, z = right
    return (add[mul[b][z]][neg[mul[c][y]]],
            add[mul[c][x]][neg[mul[a][z]]],
            add[mul[a][y]][neg[mul[b][x]]])


def affine_bases(q, unrestricted):
    add, mul, neg, inv = field_tables(q)
    coordinates = [range(q) if i < unrestricted else range(1, q) for i in range(3)]
    points = tuple(product(*coordinates))
    sizes, total = {}, 0
    for x, y, z in combinations(points, 3):
        left = tuple(add[b][neg[a]] for a, b in zip(x, y, strict=True))
        right = tuple(add[b][neg[a]] for a, b in zip(x, z, strict=True))
        normal = cross(left, right, add, mul, neg)
        if not any(normal):
            continue
        normal = normalize(normal, mul, inv)
        offset = dot(normal, x, add, mul)
        key = normal + (offset,)
        if key not in sizes:
            sizes[key] = sum(dot(normal, v, add, mul) == offset for v in points)
        total += len(points) - sizes[key]
    require(total >= 0, "affine basis count")
    return 6 * total


def direct_boxes():
    results = []
    for q in (2, 3, 4, 5):
        counts = [affine_bases(q, j) for j in range(4)]
        q3 = q ** 3
        require(counts[3] == q3 * (q3 - 1) * (q3 - q) * (q3 - q * q),
                "unrestricted affine basis oracle")
        numerator = sum((q - 1) * comb(3, j) * (q - 1) ** (3 - j) * counts[j]
                        for j in range(4))
        denominator = (q ** 4 - 1) * counts[3]
        actual = Fraction(numerator, denominator)
        require(actual == joint_probability(q, 3), "literal affine-box comparison")
        results.append({"q": q, "d": 3, "ordered_box_bases": counts,
                        "joint": [actual.numerator, actual.denominator]})
    return results


def controls():
    top, planes, lines, bottom = formula_terms(3, 3)
    actual = top - planes + lines - bottom
    mutants = (top + planes + lines - bottom,
               top - planes + lines // 3 - bottom,
               top - planes + lines - bottom // 3,
               top - planes + lines + bottom)
    require(all(value != actual for value in mutants), "Mobius mutation controls")
    require(joint_probability(3, 3) != marginal(3, 3) ** 4, "independence control")
    rejected = 0
    for q, d in ((1, 3), (3, 2), (3.0, 3), (3, 3.0)):
        try:
            formula_terms(q, d)
        except RuntimeError:
            rejected += 1
    require(rejected == 4, "formula boundary controls")
    return {"semantic_mutants": len(mutants) + 1, "rejected_inputs": rejected}


def main():
    rows, comparisons = finite_tail()
    result = {"claim_type": "scoped proof with exact finite corroboration",
              "tail_rows": rows, "exception_comparisons": comparisons,
              "strata": [strata(q) for q in (2, 3, 4, 5, 7)],
              "direct_boxes": direct_boxes(), "controls": controls()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["sha256"] = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                        for name in names}
    print(json.dumps(result, sort_keys=True))
    print("PASS_INDEPENDENT_FOUR_GUARD_POSITIVE")


if __name__ == "__main__":
    main()

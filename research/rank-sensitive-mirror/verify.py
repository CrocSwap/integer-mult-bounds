#!/usr/bin/env python3
"""Exact corroboration of the new rank-sensitive mirror lemma and toy profile.

Produced by Nick Petalas. Apache-2.0.
The all-rank conclusion is the written proof, not this finite enumeration.
"""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from math import isqrt, prod
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def root(rank):
    require(type(rank) is int and 1 <= rank <= 4096, "rank outside finite domain")
    value = isqrt(rank)
    require(value * value == rank, "finite oracle requires square ranks")
    return value


def validate(target, paid):
    for histogram in (target, paid):
        require(1 <= len(histogram) <= 8, "histogram size outside finite domain")
        for rank, count in histogram.items():
            root(rank)
            require(type(count) is int and 1 <= count <= 4096, "invalid count")
    m = max(target)
    require(min(target) >= 2 and max(paid) < m, "invalid target/paid ranks")


def mirror_cells(target, paid):
    validate(target, paid)
    endpoints = sorted({F(1, rank) for rank in (*target, *paid)})
    cells = []
    for lo, hi in zip(endpoints, endpoints[1:]):
        point = (lo + hi) / 2
        exit_weight = 0
        sources = Counter()
        for r, k in product(paid, target):
            weight = paid[r] * target[k] * root(r) * root(k)
            if r > k and F(1, r) < point <= F(1, k):
                exit_weight += weight
            if k > r and F(1, k) < point <= F(1, r):
                sources[r] += weight
        cells.append((lo, hi, exit_weight, dict(sources)))
    return cells


def weighted_ratio(cells, sqrt_ambient):
    require(sqrt_ambient > 0, "nonpositive ambient scale")
    ratios = []
    for _, _, exit_weight, sources in cells:
        capacity = sum((F(weight * root(r), 2) / sqrt_ambient
                        for r, weight in sources.items()), F(0))
        require(capacity > 0 or exit_weight == 0, "uncovered exit cell")
        ratios.append(F(exit_weight) / capacity if capacity else F(0))
    return max(ratios)


def profile_fixture():
    target, paid = {16: 1, 64: 2}, {1: 2, 4: 6, 36: 1}
    cells = mirror_cells(target, paid)
    require(sum(c * root(k) for k, c in target.items()) == 20, "target moment")
    require(sum(c * root(r) for r, c in paid.items()) == 20, "paid moment")
    active = [row for row in cells if row[2]]
    require(active == [(F(1, 36), F(1, 16), 24, {1: 32, 4: 192})],
            "literal offending cell")
    old_ratio = max(F(e, sum(s.values())) for _, _, e, s in cells)
    require(old_ratio == F(3, 28) > F(1, 16), "old uniform mirror rejection")
    require(weighted_ratio(cells, F(17, 2)) == F(51, 52), "new strict mirror")
    require(2 ** 19 > 3 ** 3, "positive exact tilted-mean gap")
    target_one = sum(k * c for k, c in target.items())
    paid_one = sum(r * c for r, c in paid.items())
    require((target_one, paid_one) == (144, 62), "shifted moments")
    require(F(target_one * paid_one, 20 ** 2 * 32) == F(279, 400) < 1,
            "mixed tail at a=b=1, M=1024, s=1/2")
    require(32 * F(sum(target.values()), 20) ** 2 == F(18, 25) < 1,
            "root tail at lambda=1/2")
    require(F(target_one, 20) > F(paid_one, 20), "forward ratio ordering")
    return target, paid, cells


def product_law(histogram, degree):
    require(0 <= degree <= 7, "degree outside finite domain")
    law = {1: 1}
    for _ in range(degree):
        next_law = Counter()
        for value, rank in product(law, histogram):
            next_law[value * rank] += law[value] * histogram[rank]
        law = dict(next_law)
    return law


def base_measure(target, paid, height):
    require(1 <= height <= 7, "height outside finite domain")
    measure = Counter()
    for depth in range(height):
        left = product_law(paid, depth)
        right = product_law(target, height - depth - 1)
        for a, b in product(left, right):
            measure[a * b] += left[a] * right[b]
    return dict(measure)


def literal_base(target, paid, height):
    require(1 <= height <= 7, "height outside literal domain")
    measure = Counter()
    for depth in range(height):
        for left in product(tuple(paid), repeat=depth):
            for right in product(tuple(target), repeat=height - depth - 1):
                weight = prod(paid[r] for r in left) * prod(target[k] for k in right)
                measure[prod(left) * prod(right)] += weight
    return dict(measure)


def integer_root(value):
    require(type(value) is int and value >= 0, "invalid square argument")
    result = isqrt(value)
    require(result * result == value, "expected a literal square product")
    return result


def capped_fixture(target, paid, height, sqrt_n):
    n, m = sqrt_n ** 2, max(target)
    cutoff = n // m
    require(n <= F(289, 4) * cutoff, "ambient cutoff guard")
    measure = base_measure(target, paid, height)
    require(measure == literal_base(target, paid, height), "independent base enumeration")
    inner, boundary, capacity, terms = 0, 0, F(0), 0
    for z, r, k in product(measure, paid, target):
        weight = measure[z] * paid[r] * target[k]
        rank = r * k * z
        if k * z <= cutoff < r * z:
            boundary += weight * integer_root(rank)
        if r * z <= cutoff < k * z:
            require(r * cutoff < rank <= n, "literal inner-source rank")
            lower = F(root(r) * integer_root(rank), 17)
            require(sqrt_n >= lower and (sqrt_n - lower) ** 2 >= n - rank,
                    "exact nonlinear complement dominates rank-sensitive charge")
            capacity += weight * lower
            inner += weight * integer_root(rank)
            terms += 1
    require(boundary <= F(51, 52) * capacity, "weighted mirror integrated at cap")
    require(capacity >= F(inner, 17), "minimum source capacity")
    roots = 20 * sum(c * integer_root(z) for z, c in product_law(target, height).items()
                     if z <= cutoff)
    leaves = 20 * sum(c * integer_root(z) for z, c in product_law(paid, height).items()
                      if z <= cutoff)
    require(inner + roots == boundary + leaves, "new toy flow cancellation")
    return terms


def funding_fixtures():
    eta, beta = F(1, 17), F(51, 52)
    threshold = (1 - eta) / ((1 - beta) * eta)
    require(threshold == 832, "complete leaf-funding threshold")
    count = 0
    for leaf, surplus_extra, boundary in product(range(5), range(4), range(61)):
        surplus = threshold * leaf + surplus_extra
        capacity = max(eta * (boundary + leaf + surplus), F(boundary) / beta)
        require(capacity >= boundary + leaf, "new funding implication")
        count += 1
    require(eta * (51 + 1 + 832) == 52 and beta * 52 == 51,
            "all-constraint equality fixture")
    underfunded = eta * 832 / (1 - eta * beta)
    require((1 - beta) * underfunded < 1, "one-unit underfunding control")
    return count


def rejecting_controls(cells):
    bad_cells = mirror_cells({16: 1, 64: 2}, {1: 4, 4: 5, 36: 1})
    require(weighted_ratio(bad_cells, F(17, 2)) > 1, "paid-rank distribution control")
    require(weighted_ratio(cells, F(26, 3)) == 1, "strict mirror boundary control")
    require(64 * 7 + 63 > F(289, 4) * 7, "insufficient cutoff control")
    require(64 * 8 + 63 <= F(289, 4) * 8, "first uniform cutoff control")
    rejected = 0
    for target, paid in (({1: 1}, {1: 1}), ({16: 1}, {36: 1}),
                         ({16: 0, 64: 2}, {1: 1}), ({17: 1, 64: 2}, {1: 1})):
        try:
            mirror_cells(target, paid)
        except ValueError:
            rejected += 1
    require(rejected == 4, "invalid input controls")
    uncovered = mirror_cells({4: 1, 64: 2}, {16: 1})
    try:
        weighted_ratio(uncovered, F(17, 2))
    except ValueError:
        return 9
    raise ValueError("uncovered source window accepted")


def receipt(results):
    directory = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = directory / name
        require(path.is_file() and not path.is_symlink(), "missing regular package file")
        require(path.stat().st_size <= 262144, "package file exceeds receipt bound")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return {"schema": "rank-sensitive-mirror-receipt/v1", "results": results,
            "python": sys.version.split()[0], "files_sha256": hashes}


def main():
    target, paid, cells = profile_fixture()
    terms = 0
    sizes = (24, 25, 32, 33, 48, 64, 65)
    for height, sqrt_n in product(range(1, 8), sizes):
        terms += capped_fixture(target, paid, height, sqrt_n)
    results = {"old_mirror_ratio": "3/28", "old_uniform_capacity": "1/16",
               "new_weighted_ratio": "51/52", "ambient_scale": "289/4",
               "crossing_moment": 20, "mixed_tail": "279/400", "root_tail": "18/25",
               "capped_flows": 49, "source_terms": terms,
               "funding_cases": funding_fixtures(), "controls": rejecting_controls(cells)}
    print(json.dumps(receipt(results), sort_keys=True))
    print("PASS_RANK_SENSITIVE_MIRROR " + json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()

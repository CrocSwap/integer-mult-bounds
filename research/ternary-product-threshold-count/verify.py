#!/usr/bin/env python3
"""Exact ternary threshold count; standard library, no runtime dependencies."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path


IDENTITY = (0, 1, 2, 3)
LINES = ((1, 0), (0, 1), (1, 1), (1, 2))
FULL = (1 << 16) - 1


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compose(a, b):
    return tuple(a[b[i]] for i in range(4))


def inverse(a):
    return tuple(a.index(i) for i in range(4))


def multiply(a, b):
    return tuple(sum(a[2 * i + h] * b[2 * h + j] for h in range(2)) % 3
                 for i in range(2) for j in range(2))


def action(matrix):
    result = []
    a, b, c, d = matrix
    for x, y in LINES:
        u, v = (a * x + b * y) % 3, (c * x + d * y) % 3
        require(u != 0 or v != 0, "singular projective action")
        line = (1, v * pow(u, -1, 3) % 3) if u else (0, 1)
        result.append(LINES.index(line))
    return tuple(result)


def literal_zero_mask(matrix):
    """Bit (i,j) records phi_j M t_i=0, with literal F3 arithmetic."""
    a, b, c, d = matrix
    mask = 0
    for i, (x, y) in enumerate(LINES):
        for j, (r, s) in enumerate(LINES):
            value = r * (a * x + b * y) + s * (c * x + d * y)
            if value % 3 == 0:
                mask |= 1 << (4 * i + j)
    require(mask.bit_count() == 4, "one annihilator per input line")
    return mask


def covers(support):
    require(len(support) == 4, "threshold support must have four permutations")
    return all(len({p[i] for p in support}) == 4 for i in range(4))


def normalized_groups(all_permutations):
    groups = set()
    for p in all_permutations:
        p2 = compose(p, p)
        if p2 != IDENTITY and compose(p2, p2) == IDENTITY:
            groups.add(frozenset((IDENTITY, p, p2, compose(p2, p))))
    doubles = tuple(p for p in all_permutations
                    if p != IDENTITY and compose(p, p) == IDENTITY
                    and all(p[i] != i for i in range(4)))
    require(len(doubles) == 3, "three double transpositions")
    groups.add(frozenset((IDENTITY, *doubles)))
    require(len(groups) == 4, "three cyclic groups and one Klein group")
    for group in groups:
        require(covers(group), "regular group action")
        require(all(compose(a, b) in group for a in group for b in group),
                "subgroup closure")
    return groups


def check_supports(all_permutations):
    groups = normalized_groups(all_permutations)
    supports = {frozenset(s) for s in combinations(all_permutations, 4)
                if covers(s)}
    cosets = {frozenset(compose(p, h) for h in group)
              for p in all_permutations for group in groups}
    require(len(supports) == 24 and supports == cosets, "coset classification")
    require({s for s in supports if IDENTITY in s} == groups,
            "complete normalized classification")
    kinds = Counter()
    for support in supports:
        first = min(support)
        normal = frozenset(compose(inverse(first), p) for p in support)
        require(normal in groups, "normalization lands in a classified group")
        kinds["cyclic" if any(compose(p, p) != IDENTITY for p in normal)
              else "klein"] += 1
    require(kinds == {"cyclic": 18, "klein": 6}, "coset type counts")
    return supports, kinds


def matrix_census(matrices):
    """Enumerate every ordered GL2(F3)^4 target, without projective actions."""
    masks = tuple(literal_zero_mask(m) for m in matrices)
    count, visited = 0, 0
    for a in masks:
        for b in masks:
            ab = a | b
            for c in masks:
                abc = ab | c
                for d in masks:
                    visited += 1
                    count += abc | d == FULL
    require(visited == 48 ** 4, "complete ordered matrix census")
    require(count == 9216, "literal matrix threshold count")
    return visited, count


def controls(all_permutations, matrices, supports):
    checks = 0
    for support in supports:
        for removed in support:
            remaining = tuple(p for p in support if p != removed)
            require(not covers((*remaining, remaining[0])), "duplicate control")
            checks += 1
    for matrix in matrices:
        negative = tuple(-x % 3 for x in matrix)
        require(action(matrix) == action(negative), "scalar-lift invariance")
        require(literal_zero_mask(matrix) == literal_zero_mask(negative),
                "literal scalar-lift invariance")
        checks += 1
    try:
        action((1, 0, 0, 0))
    except ValueError:
        checks += 1
    else:
        raise ValueError("singular matrix accepted")
    try:
        covers(all_permutations[:3])
    except ValueError:
        checks += 1
    else:
        raise ValueError("wrong component count accepted")
    partial = next(s for s in combinations(all_permutations, 4)
                   if all(len({p[i] for p in s}) == 4 for i in range(2))
                   and not covers(s))
    require(not covers(partial), "partial-input coverage is insufficient")
    checks += 1
    return checks


def receipt(results):
    directory = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = directory / name
        require(path.stat().st_size <= 1024 * 1024, "receipt file capacity")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    print(json.dumps({"schema": "ternary-product-threshold-count/v1",
                      "results": results, "sha256": hashes}, sort_keys=True))


def main():
    all_permutations = tuple(permutations(range(4)))
    matrices = tuple(m for m in product(range(3), repeat=4)
                     if (m[0] * m[3] - m[1] * m[2]) % 3)
    require(len(matrices) == 48, "GL2(F3) order")
    actions = Counter(action(m) for m in matrices)
    require(actions == {p: 2 for p in all_permutations}, "two lifts per S4 action")
    for a in matrices:
        for b in matrices:
            require(action(multiply(a, b)) == compose(action(a), action(b)),
                    "projective multiplication convention")
    supports, kinds = check_supports(all_permutations)
    visited, count = matrix_census(matrices)
    require(count == len(supports) * 24 * 2 ** 4, "independent count agreement")
    require(visited == count * 576, "exact probability 1/576")
    checks = controls(all_permutations, matrices, supports)
    results = {"targets": visited, "cost_three": count,
               "projective_supports": len(supports), "support_types": dict(kinds),
               "cyclic_targets": kinds["cyclic"] * 24 * 16,
               "klein_targets": kinds["klein"] * 24 * 16, "controls": checks}
    receipt(results)
    print(f"PASS_TERNARY_PRODUCT_THRESHOLD_COUNT targets={visited} "
          f"cost3={count} probability=1/576 no_new_kappa")


if __name__ == "__main__":
    main()

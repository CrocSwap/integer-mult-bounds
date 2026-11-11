#!/usr/bin/env python3
"""Exact finite minimum-order certificate for two stable two-lane passes."""

import hashlib
import itertools
import json
import math
from pathlib import Path
import sys


TARGET = (3, 2, 1, 6, 5, 4, 9, 8, 7, 0)
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
         "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def permutation(value):
    require(isinstance(value, tuple) and 1 <= len(value) <= 10,
            "permutation length must lie in 1..10")
    require(all(type(x) is int for x in value), "integer records required")
    require(sorted(value) == list(range(len(value))), "invalid record set")
    return value


def width(value):
    """Quadratic longest-decreasing-subsequence dynamic program."""
    permutation(value)
    depths = [1] * len(value)
    for j in range(len(value)):
        for i in range(j):
            if value[i] > value[j]:
                depths[j] = max(depths[j], depths[i] + 1)
    return max(depths)


def avoids_321(value):
    """Independent literal forbidden-triple predicate."""
    for i, j, k in itertools.combinations(range(len(value)), 3):
        if value[i] > value[j] > value[k]:
            return False
    return True


def catalogue(n):
    require(type(n) is int and 1 <= n <= 10, "unsupported catalogue size")
    words = [()]
    for size in range(1, n + 1):
        following = []
        for word in words:
            for cut in range(size):
                if all(word[i] < word[i + 1]
                       for i in range(cut, size - 2)):
                    following.append(word[:cut] + (size - 1,) + word[cut:])
        words = following
    require(len(words) == len(set(words)), "duplicate catalogue entry")
    require(len(words) <= 16796, "catalogue capacity exceeded")
    return words


def pass_check(before, after, lane_one):
    permutation(before)
    permutation(after)
    require(len(before) == len(after), "record count changed")
    require(isinstance(lane_one, frozenset) and lane_one <= set(before),
            "invalid lane assignment")
    for selected in (False, True):
        incoming = tuple(x for x in before if (x in lane_one) == selected)
        outgoing = tuple(x for x in after if (x in lane_one) == selected)
        require(incoming == outgoing, "lane order changed")


def upper_route():
    orders = (tuple(range(10)), (1, 2, 3, 4, 5, 6, 7, 8, 9, 0),
              (2, 1, 3, 5, 4, 6, 8, 7, 9, 0), TARGET)
    lanes = (frozenset({0}), frozenset({2, 5, 8}), frozenset({3, 6, 9}))
    for i in range(3):
        pass_check(orders[i], orders[i + 1], lanes[i])
    require(width(TARGET) == 4, "wrong obstruction width")
    return {"orders": orders, "lane_one_records": [sorted(x) for x in lanes]}


def acyclic(labels):
    """Kahn elimination on all first/second-pass order requirements."""
    positions = {x: i for i, x in enumerate(TARGET)}
    edges = [set() for _ in range(10)]
    for x in range(10):
        for y in range(x + 1, 10):
            if labels[x] // 2 == labels[y] // 2:
                edges[x].add(y)
            if labels[x] % 2 == labels[y] % 2:
                a, b = (x, y) if positions[x] < positions[y] else (y, x)
                edges[a].add(b)
    remaining = set(range(10))
    for _ in range(10):
        roots = [x for x in remaining
                 if all(x not in edges[y] for y in remaining)]
        if not roots:
            return False
        remaining.difference_update(roots)
        if not remaining:
            return True
    raise ValueError("topological capacity exhausted")


def cycle_certificate():
    positions = {x: i for i, x in enumerate(TARGET)}
    inversions = [(x, y) for x in range(10) for y in range(x + 1, 10)
                  if positions[x] > positions[y]]
    admissible = 0
    for tail in itertools.product(range(4), repeat=9):
        labels = (0,) + tail
        if any(labels[x] == labels[y] for x, y in inversions):
            continue
        admissible += 1
        a = next(x for x in (1, 2, 3) if labels[x] == 1)
        c = next(x for x in (4, 5, 6) if labels[x] == 3)
        b = next(x for x in (7, 8, 9) if labels[x] == 2)
        require(labels[0] // 2 == labels[a] // 2 and 0 < a,
                "first cycle edge missing")
        require(labels[a] % 2 == labels[c] % 2
                and positions[a] < positions[c], "second cycle edge missing")
        require(labels[c] // 2 == labels[b] // 2 and c < b,
                "third cycle edge missing")
        require(labels[b] % 2 == labels[0] % 2
                and positions[b] < positions[0], "fourth cycle edge missing")
        require(not acyclic(labels), "an acyclic intermediate order exists")
    require(admissible == math.factorial(3) ** 3, "incomplete type census")
    return {"normalized_assignments": 4 ** 9, "forced_cycles": admissible}


def factor_exclusion():
    counts = {}
    factors = catalogue(10)
    require(len(factors) == 16796, "wrong ten-record catalogue size")
    for first in factors:
        require(avoids_321(first), "invalid first factor")
        inverse = [0] * 10
        for i, x in enumerate(first):
            inverse[x] = i
        second = tuple(inverse[x] for x in TARGET)
        require(tuple(first[x] for x in second) == TARGET,
                "factor reconstruction failed")
        value = width(second)
        require(value > 2, "two-pass factorization found")
        counts[value] = counts.get(value, 0) + 1
    return {"first_factors": len(factors), "second_width_counts": counts}


def minimal_order():
    factors = catalogue(9)
    require(len(factors) == 4862, "wrong nine-record catalogue size")
    direct_factors = set()
    possible = set()
    visited = 0
    for word in itertools.permutations(range(9)):
        visited += 1
        if avoids_321(word):
            direct_factors.add(word)
        if width(word) <= 4:
            possible.add(bytes(word))
    require(visited == math.factorial(9), "incomplete permutation scan")
    require(set(factors) == direct_factors, "independent catalogues disagree")
    reached = {bytes(first[x] for x in second)
               for first in factors for second in factors}
    require(reached == possible, "nine-record inverse completeness failed")
    require(len(reached) == 261808, "unexpected nine-record product class")
    for removed in range(10):
        raw = [x for x in TARGET if x != removed]
        reduced = bytes(x - (x > removed) for x in raw)
        require(reduced in reached, "a deletion remains obstructed")
    digest = hashlib.sha256(b"".join(sorted(reached))).hexdigest()
    return {"permutations": visited, "one_pass_factors": len(factors),
            "factor_pairs": len(factors) ** 2, "two_pass_layouts": len(reached),
            "deletions": 10, "sorted_layouts_sha256": digest}


def expect_invalid(before, after, lanes):
    try:
        pass_check(before, after, lanes)
    except ValueError:
        return
    raise ValueError("invalid routing control was accepted")


def controls():
    expect_invalid((0, 1), (1, 0), frozenset())
    expect_invalid((0, 1), (0, 0), frozenset({0}))
    expect_invalid((0, 1), (0,), frozenset({0}))
    expect_invalid((0, 1), (0, 1), frozenset({2}))
    expect_invalid((0, 1, 2), (2, 1, 0), frozenset({0}))
    expect_invalid(tuple(range(10)), TARGET, frozenset({0}))
    pass_check((0, 1, 2, 3), (1, 0, 3, 2), frozenset({1, 3}))
    pass_check((1, 0, 3, 2), (3, 2, 1, 0), frozenset({2, 3}))
    require(width((3, 2, 1, 0)) == 4, "width-four boundary changed")
    return {"invalid_routes_rejected": 6, "width_four_two_pass_control": True}


def main():
    require(len(sys.argv) == 1, "this verifier takes no arguments")
    result = {"route": upper_route(), "cycle": cycle_certificate(),
              "exclusion": factor_exclusion(), "minimal_order": minimal_order(),
              "controls": controls()}
    directory = Path(__file__).resolve().parent
    sources = {}
    for name in FILES:
        payload = (directory / name).read_bytes()
        require(len(payload) <= 1048576, "package source capacity exceeded")
        sources[name] = hashlib.sha256(payload).hexdigest()
    receipt = {"status": "PASS_TWO_PASS_WIDTH_OBSTRUCTION", "result": result,
               "python": sys.version.split()[0], "package_sha256": sources}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

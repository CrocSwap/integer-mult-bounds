#!/usr/bin/env python3
"""Exact finite corroboration of the one-edge equality obstruction.

Produced by Nick Petalas. Apache-2.0.
The unbounded statement is the written proof, using the credited quotient lemma.
"""

import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_rank(vectors):
    """All callers supply at most eight vectors with at most six bits."""
    require(len(vectors) <= 8, "too many vectors")
    pivots = [0] * 6
    for original in vectors:
        require(0 <= original < 64, "vector outside finite domain")
        value = original
        for bit in range(5, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(value != 0 for value in pivots)


def outer(x, y, width):
    return sum(y << (width * row) for row in range(width) if x >> row & 1)


def pattern_pool(width):
    require(width in (5, 6), "only the declared finite widths are supported")
    diagonal = sum(1 << (i * width + i) for i in range(width))
    lifts = {}
    for x in range(1, 1 << width):
        for y in range(1, 1 << width):
            if (x & y).bit_count() % 2:
                pattern = outer(x, y, width) & ~diagonal
                if pattern:
                    lifts.setdefault(pattern, []).append((x, y))
    require(len(lifts) <= 2010, "finite pool capacity exceeded")
    return lifts


def span_three(generators):
    require(len(generators) == 3, "three generators required")
    a, b, c = generators
    return {0, a, b, c, a ^ b, a ^ c, b ^ c, a ^ b ^ c}


def invariant_edge(pool, edge):
    return all(not (y & edge) or not (x & ~edge) for x, y in pool)


def check_fixture(generators, width, claimed_pool=None):
    lifts = pattern_pool(width)
    patterns = span_three(generators)
    require(len(patterns) == 8, "pattern dimension is not three")
    diagonal = sum(1 << (i * width + i) for i in range(width))
    require(all(0 <= p < 1 << (width * width) and not p & diagonal
                for p in patterns), "invalid off-diagonal matrix")
    edges = [p for p in patterns if p.bit_count() == 1]
    require(len(edges) == 1, "the space must have exactly one edge")
    position = edges[0].bit_length() - 1
    row, column = divmod(position, width)
    edge = (1 << row) | (1 << column)
    pool = tuple(sorted(pair for p in patterns for pair in lifts.get(p, ())))
    if claimed_pool is not None:
        require(tuple(sorted(claimed_pool)) == pool, "incomplete or extra pool")
    require(binary_rank(tuple(x for x, _ in pool)) == 5, "joint image is not five")
    require(invariant_edge(pool, edge), "edge space is not invariant")
    return pool


def enumerate_equalities(width):
    """Enumerate all relevant spaces at this width with fixed edge E01.

    Equality needs all three nonzero quotient cosets to be realized. Each
    such space therefore occurs as an XOR triple of realized quotient keys.
    Permuting coordinates takes any directed edge to E01.
    """
    lifts = pattern_pool(width)
    edge_pattern = 2
    groups = {}
    for pattern, pool in lifts.items():
        key = pattern & ~edge_pattern
        if key:
            groups.setdefault(key, []).extend(pool)
    keys = sorted(groups)
    triples = one_edge_spaces = equalities = 0
    for q, r in itertools.combinations(keys, 2):
        s = q ^ r
        if s <= r or s not in groups:
            continue
        triples += 1
        patterns = span_three((edge_pattern, q, r))
        if sum(p.bit_count() == 1 for p in patterns) != 1:
            continue
        one_edge_spaces += 1
        pool = lifts[edge_pattern] + groups[q] + groups[r] + groups[s]
        dimension = binary_rank(tuple(x for x, _ in pool))
        require(dimension <= 5, "unexpected larger joint image")
        if dimension == 5:
            require(invariant_edge(pool, 3), "five-dimensional counterexample")
            equalities += 1
    return {"width": width, "realized_quotient_triples": triples,
            "one_edge_spaces_with_three_realized_cosets": one_edge_spaces,
            "five_dimensional_spaces": equalities,
            "five_dimensional_spaces_preserving_edge": equalities}


def rejects(action, expected):
    try:
        action()
    except ValueError as error:
        require(expected in str(error), "rejection for an unexpected reason")
        return
    raise ValueError("negative control was accepted")


def fixture_and_controls():
    # E01 and two weight-two columns into coordinate 2 on six coordinates.
    p = 2
    q = (1 << (3 * 6 + 2)) | (1 << (4 * 6 + 2))
    r = (1 << (4 * 6 + 2)) | (1 << (5 * 6 + 2))
    generators = (p, q, r)
    expected = ((1, 3), (3, 2), (28, 4), (44, 4), (52, 4))
    pool = check_fixture(generators, 6, expected)
    rejects(lambda: check_fixture((p, q, q), 6), "dimension")
    rejects(lambda: check_fixture((p, q, 1 << 8), 6), "exactly one edge")
    rejects(lambda: check_fixture(generators, 6, pool[:-1]), "incomplete")
    rejects(lambda: check_fixture(generators, 6, pool + ((1, 1),)), "extra pool")
    rejects(lambda: pattern_pool(7), "finite widths")
    require(not invariant_edge(((5, 1),), 3), "leaking idempotent accepted")
    require(not invariant_edge(pool + ((5, 1),), 3), "extra pattern ignored")
    return {"width": 6, "generators": generators, "pool_xy_masks": pool,
            "joint_image_dimension": 5, "invariant_edge_basis": (1, 2),
            "negative_controls": 7}


def source_hashes():
    package = Path(__file__).resolve().parent
    files = sorted(p for p in package.iterdir() if p.is_file())
    require(len(files) <= 16, "unexpected package inventory")
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def main():
    fixture = fixture_and_controls()
    censuses = [enumerate_equalities(width) for width in (5, 6)]
    require(censuses[1]["five_dimensional_spaces"] > 0, "equality was not exercised")
    print("PASS_ONE_EDGE_PATTERN_REDUCIBILITY")
    print(json.dumps({"claim_type": "scoped proof with finite corroboration",
                      "fixture": fixture, "finite_censuses": censuses,
                      "sha256": source_hashes()}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

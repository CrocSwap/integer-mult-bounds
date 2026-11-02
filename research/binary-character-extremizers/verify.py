#!/usr/bin/env python3
"""Exact new equality checks; no predecessor imports or spectrum tables."""

import hashlib
import itertools
import json
import platform
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(rows):
    require(type(rows) is tuple and 2 <= len(rows) <= 12, "matrix size")
    k = len(rows)
    require(all(type(row) is int and 0 <= row < 1 << k for row in rows),
            "binary row masks")
    require(all(not (rows[i] >> i & 1) for i in range(k)), "zero diagonal")
    return k


def from_mask(k, mask):
    require(type(k) is int and 2 <= k <= 6, "mask dimension")
    require(type(mask) is int and 0 <= mask < 1 << (k * (k - 1)),
            "edge mask")
    rows = [0] * k
    bit = 0
    for i in range(k):
        for j in range(k):
            if i != j:
                rows[i] |= (mask >> bit & 1) << j
                bit += 1
    return tuple(rows)


def literal(rows, field=0):
    k = validate(rows)
    require(k <= 6, "literal capacity")
    require(type(field) is int and 0 <= field < 1 << (2 * k), "field")
    total = 0
    for state in itertools.product(range(3), repeat=k):
        ones = sum(1 << i for i in range(k) if state[i] == 1)
        twos = sum(1 << i for i in range(k) if state[i] == 2)
        parity = 0
        for i in range(k):
            if ones >> i & 1:
                parity ^= (rows[i] & twos).bit_count() & 1
            if state[i]:
                parity ^= field >> (2 * i + state[i] - 1) & 1
        total += 1 - 2 * parity
    return total


def subset_sum(rows):
    k = validate(rows)
    total = 0
    for sources in range(1 << k):
        parity_row = 0
        for i in range(k):
            if sources >> i & 1:
                parity_row ^= rows[i]
        if parity_row & ((1 << k) - 1 - sources) == 0:
            total += 1 << (k - sources.bit_count())
    return total


def is_star(rows):
    k = validate(rows)
    edges = [(i, j) for i in range(k) for j in range(k) if rows[i] >> j & 1]
    return len(edges) == 2 and (edges[0][0] == edges[1][0]
                               or edges[0][1] == edges[1][1])


def local_equality():
    cases = 0
    equality = []
    edge_counts = {}
    for mask in range(64):
        if mask.bit_count() < 2:
            continue
        rows = from_mask(3, mask)
        for field in range(64):
            value = literal(rows, field)
            expected = is_star(rows) and field == 0
            require(abs(value) <= 19, "local bound")
            require((abs(value) == 19) == expected, "local equality")
            if expected:
                require(value == 19, "local positive sign")
                equality.append([mask, field, value])
            cases += 1
            count = mask.bit_count()
            edge_counts[count] = max(edge_counts.get(count, 0), abs(value))
    require(cases == 3648 and len(equality) == 6, "local coverage")
    return {"cases": cases, "equality_rows": equality,
            "max_absolute_by_edge_count": edge_counts}


def full_small():
    counts = {}
    compared = 0
    classified = 0
    for k in (3, 4):
        attained = 0
        bound = 19 * 3 ** (k - 3)
        for mask in range(1 << (k * (k - 1))):
            if mask.bit_count() < 2:
                continue
            rows = from_mask(k, mask)
            value = subset_sum(rows)
            require((value == bound) == is_star(rows), "full equality")
            require(value <= bound, "full upper bound")
            attained += value == bound
            classified += 1
            if k == 3:
                require(value == literal(rows), "independent local character")
                compared += 1
        require(attained == k * (k - 1) * (k - 2), "labelled multiplicity")
        counts[k] = attained
    return {"classified": classified, "literal_comparisons": compared,
            "attainers": counts}


def outside_extensions():
    # Fix the attaining core 0->1,0->2. Enumerate every remaining edge.
    k = 5
    extra = [(i, j) for i in range(k) for j in range(k)
             if i != j and (i >= 3 or j >= 3)]
    require(len(extra) == 14, "outside edge coverage")
    attained = 0
    for mask in range(1 << len(extra)):
        rows = [6, 0, 0, 0, 0]
        for bit, (i, j) in enumerate(extra):
            rows[i] |= (mask >> bit & 1) << j
        value = subset_sum(tuple(rows))
        require((value == 171) == (mask == 0), "outside rigidity")
        attained += value == 171
    return {"extensions": 1 << len(extra), "attainers": attained}


def labelled_families():
    counts = {}
    probes = 0
    for k in range(3, 9):
        family = set()
        for center in range(k):
            others = [i for i in range(k) if i != center]
            for a, b in itertools.combinations(others, 2):
                for orientation in range(2):
                    rows = [0] * k
                    if orientation == 0:
                        rows[center] = (1 << a) | (1 << b)
                    else:
                        rows[a] = rows[b] = 1 << center
                    rows = tuple(rows)
                    require(rows not in family, "distinct labelled stars")
                    require(subset_sum(rows) == 19 * 3 ** (k - 3),
                            "attaining extension")
                    require(is_star(rows), "structural recognizer")
                    family.add(rows)
                    probes += 1
        require(len(family) == k * (k - 1) * (k - 2), "family cardinality")
        counts[k] = len(family)
    return {"probes": probes, "counts": counts}


def controls():
    invalid = [(), (0,), (0, 0, 0) * 5, [0, 0, 0], (True, 0, 0),
               (-1, 0, 0), (8, 0, 0), (1, 0, 0)]
    rejected = 0
    for rows in invalid:
        try:
            validate(rows)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid-domain control admitted")
    star = (6, 0, 0)
    require(literal(star) == 19 and literal(star, 1) != 19,
            "omitted unary field must change equality")
    require(not is_star((2, 4, 0)), "a directed path is not a star")
    require(subset_sum((2, 4, 0)) < 19, "directed-path false equality")
    require(subset_sum((2, 1, 0)) < 19, "reciprocal false equality")
    require(subset_sum((6, 0, 0, 16, 0)) == 133 < 171,
            "outside constant-sign cancellation")
    require(subset_sum((14, 0, 0, 0)) == 55 < 57,
            "three-arrow star false equality")
    for field in range(1, 64):
        require(abs(literal(star, field)) < 19, "outside attachment control")
    return {"invalid_rejections": rejected, "semantic_checks": 6,
            "nonzero_field_rejections": 63}


def main():
    result = {"marker": "PASS_BINARY_CHARACTER_EXTREMIZERS",
              "claim_type": "scoped proof with exact finite equality lemma",
              "local": local_equality(), "small": full_small(),
              "outside": outside_extensions(), "families": labelled_families(),
              "controls": controls(), "python": platform.python_version()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (package / name).open("rb") as source:
            data = source.read((1 << 20) + 1)
        require(len(data) <= 1 << 20, "package-file capacity")
        hashes[name] = hashlib.sha256(data).hexdigest()
    result["sha256"] = hashes
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

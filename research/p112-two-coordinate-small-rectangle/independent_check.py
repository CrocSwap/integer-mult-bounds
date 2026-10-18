#!/usr/bin/env python3
"""Recheck finite premises from doubled Euclidean roots, without primary imports.

Apache-2.0. Prepared for commdata2338 with substantial OpenAI Codex assistance.
This separate implementation is not independent human review.
"""
import argparse
from collections import Counter
from copy import deepcopy
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def basis(rows):
    """Eliminate from the least significant end, unlike the primary checker."""
    pivots = {}
    for original in rows:
        value = original
        while value:
            bit = value & -value
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return list(pivots.values())


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def geometric_model():
    root_set = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2*sign
            root_set.add(tuple(row))
    for tail in product((-1, 1), repeat=7):
        row = (1,)+tail
        if sum(x == -1 for x in row) % 2 == 0:
            root_set.add(row)
    frame = []
    for i in (0, 2, 4, 6):
        for sign in (1, -1):
            row = [0] * 8
            row[i], row[i+1] = 2, 2*sign
            frame.append(tuple(row))
    require(len(root_set) == 120 and set(frame) <= root_set, "E8 roots and frame")
    roots = sorted(root_set.difference(frame))
    require(len(roots) == 112, "puncture size")
    x = [[dot(r, f)//4 for f in frame] for r in roots]
    b = [sum(((dot(r, s)//4+1) % 2) << j for j, s in enumerate(roots)) for r in roots]
    require(all(dot(x[i], x[j]) == dot(roots[i], roots[j])//2
                for i in range(112) for j in range(112)), "all-entry coordinate identity")
    generators = basis(b)
    require(len(generators) == 9, "binary ambient rank")
    characters = [0]
    for row in generators:
        characters += [old ^ row for old in characters]
    require(len(set(characters)) == 512, "complete binary dual evaluation space")
    return roots, x, b, characters[1:]


def check(receipt, model):
    roots, x, b, characters = model
    require(receipt["schema_version"] == 1, "schema")
    require(receipt["roots"] == [list(r) for r in roots], "root binding")
    expected_pairs = [list(pair) for pair in combinations(range(8), 2)]
    require([row["pair"] for row in receipt["pairs"]] == expected_pairs, "pair coverage")
    dims, distances, pair_ranks, free_distances = Counter(), Counter(), Counter(), Counter()
    count = 0
    names = ["x", "y", "plus", "minus", "generic"]
    all_supports = {}
    for entry in receipt["pairs"]:
        k, l = entry["pair"]
        require([r["name"] for r in entry["strata"]] == names, "stratum coverage")
        # Generic complex ratios cancel no nonzero row: use the union directly.
        predicates = [lambda a, c: a != 0, lambda a, c: c != 0,
                      lambda a, c: a+c != 0, lambda a, c: a-c != 0,
                      lambda a, c: a != 0 or c != 0]
        supports = []
        for record, predicate in zip(entry["strata"], predicates):
            support = [i for i in range(112) if predicate(x[i][k], x[i][l])]
            require(record["support"] == support, "exact support")
            mask = sum(1 << i for i in support)
            spectrum = Counter((row & mask).bit_count() for row in characters)
            distance = min(weight for weight in spectrum if weight)
            dimension = len(basis(b[i] for i in support))
            free_spectrum = Counter()
            for character in characters:
                deleted = mask & character
                if deleted:
                    forbidden = 0
                    for i in range(112):
                        if deleted >> i & 1:
                            forbidden |= b[i]
                    if forbidden != (1 << 112)-1:
                        free_spectrum[deleted.bit_count()] += 1
            free_distance = min(free_spectrum)
            require(record["free_distance"] == free_distance and free_distance >= 24,
                    "free-compatible distance")
            require(record["free_weight_spectrum"] == {str(w): n for w, n in free_spectrum.items()},
                    "free-compatible spectrum")
            free_distances[free_distance] += 1
            require(record["span"] == dimension, "span dimension")
            require(record["distance"] == distance and distance >= 12, "erasure distance")
            require(record["weight_spectrum"] == {str(w): n for w, n in spectrum.items()},
                    "complete weight spectrum")
            require(spectrum.get(0, 0) == 2**(9-dimension)-1, "annihilator count")
            dims[dimension] += 1
            distances[distance] += 1
            count += len(characters)
            supports.append(support)
            all_supports[(k, l, record["name"])] = support
        matrix = []
        for left in supports:
            row = []
            for right in supports:
                mask = sum(1 << i for i in right)
                rho = len(basis(b[i] & mask for i in left))
                require(rho >= 8, "pairing floor")
                row.append(rho)
                pair_ranks[rho] += 1
            matrix.append(row)
        require(entry["pairing_ranks"] == matrix, "pairing matrix")
    boundary = receipt["boundary"]
    key = (*boundary["pair"], boundary["stratum"])
    support = all_supports[key]
    deleted = boundary["deleted"]
    require(len(deleted) == len(set(deleted)) == 12 and set(deleted) <= set(support),
            "twelve distinct boundary deletions")
    before = len(basis(b[i] for i in support))
    after = len(basis(b[i] for i in support if i not in deleted))
    require(before == boundary["span_before"] and after == boundary["span_after"]
            and after < before, "boundary span loss")
    odd_neighbors = [j for j in range(112) if all(not (b[i] >> j & 1) for i in deleted)]
    require(boundary["common_odd_neighbors"] == odd_neighbors == [], "twelve-row nonfree boundary")
    fb = receipt["free_boundary"]
    support = all_supports[(*fb["pair"], fb["stratum"])]
    erased = fb["deleted"]
    require(len(erased) == len(set(erased)) == 24 and set(erased) <= set(support),
            "twenty-four distinct boundary deletions")
    odd_neighbors = [j for j in range(112) if all(not (b[i] >> j & 1) for i in erased)]
    require(odd_neighbors == fb["common_odd_neighbors"] and bool(odd_neighbors),
            "free boundary odd neighbors")
    before = len(basis(b[i] for i in support))
    after = len(basis(b[i] for i in support if i not in erased))
    require(before == fb["span_before"] and after == fb["span_after"] and after < before,
            "free boundary span loss")
    summary = {"coordinate_pairs": 28, "support_strata": 140,
               "nonzero_functionals_per_stratum": 511, "functional_evaluations": count,
               "pairings": 700, "span_counts": {str(k): v for k, v in dims.items()},
               "distance_counts": {str(k): v for k, v in distances.items()},
               "pairing_rank_counts": {str(k): v for k, v in pair_ranks.items()},
               "free_distance_counts": {str(k): v for k, v in free_distances.items()},
               "max_deleted_per_side": 11, "max_nonzero_free_deleted_per_side": 23,
               "coordinate_costs": [8]*8,
               "whole_copy_floor": 64}
    require(receipt["summary"] == summary, "summary")


def controls(receipt, model):
    mutations = []
    r = deepcopy(receipt); r["pairs"].pop(); mutations.append((r, "pair coverage"))
    r = deepcopy(receipt); r["pairs"][0]["strata"][0]["support"].pop()
    mutations.append((r, "exact support"))
    r = deepcopy(receipt); r["pairs"][0]["strata"][2]["distance"] = 13
    mutations.append((r, "erasure distance"))
    r = deepcopy(receipt); r["pairs"][0]["pairing_ranks"][0][0] = 7
    mutations.append((r, "pairing matrix"))
    r = deepcopy(receipt); r["boundary"]["deleted"][0] = r["boundary"]["deleted"][1]
    mutations.append((r, "twelve distinct boundary deletions"))
    r = deepcopy(receipt); r["roots"][0][0] += 1; mutations.append((r, "root binding"))
    r = deepcopy(receipt); r["summary"]["whole_copy_floor"] = 65
    mutations.append((r, "summary"))
    r = deepcopy(receipt); r["pairs"][0]["strata"][0]["free_distance"] = 25
    mutations.append((r, "free-compatible distance"))
    r = deepcopy(receipt); r["free_boundary"]["common_odd_neighbors"] = []
    mutations.append((r, "free boundary odd neighbors"))
    for mutated, message in mutations:
        try:
            check(mutated, model)
        except ValueError as exc:
            require(message in str(exc), "unexpected rejection reason: " + str(exc))
        else:
            raise ValueError("accepted corrupted premise: " + message)
    return len(mutations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    model = geometric_model()
    check(receipt, model)
    n = controls(receipt, model)
    print(f"PASS_P112_SMALL_RECTANGLE_INDEPENDENT strata=140 characters=71540 "
          f"pairings=700 boundaries=12,24 controls={n}")


if __name__ == "__main__":
    main()

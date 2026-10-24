#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite lemmas for the specified A7+A1 P112 COPY optimum."""

from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(rows, width=9):
    """Internal binary elimination; callers use at most 120 rows."""
    require(0 < width <= 120 and len(rows) <= 120, "elimination capacity")
    pivots = [0] * width
    for row in rows:
        require(type(row) is int and 0 <= row < 1 << width, "binary row")
        value = row
        for column in range(width - 1, -1, -1):
            if value >> column & 1:
                if pivots[column]:
                    value ^= pivots[column]
                else:
                    pivots[column] = value
                    break
    return tuple(value for value in pivots if value)


def dot(left, right):
    require(len(left) == len(right) <= 9, "dot-product shape")
    return sum(a * b for a, b in zip(left, right))


def roots_and_puncture():
    roots = set()
    puncture = set()
    for i, j in combinations(range(8), 2):
        for sign in (-2, 2):
            row = tuple(2 if k == i else sign if k == j else 0 for k in range(8))
            roots.add(row)
            if i % 2 == 0 and j == i + 1:
                puncture.add(row)
    for row in product((-1, 1), repeat=8):
        if sum(x < 0 for x in row) % 2 == 0:
            roots.add(row if row[0] > 0 else tuple(-x for x in row))
    require(len(roots) == 120 and len(puncture) == 8, "E8 line inventory")
    deleted = tuple(sorted(puncture))
    require(all(dot(x, y) == 0 for x, y in combinations(deleted, 2)),
            "orthogonal puncture")
    return tuple(sorted(roots - puncture, reverse=True))


def model():
    roots = roots_and_puncture()
    require(len(roots) == 112 and all(dot(x, x) == 8 for x in roots), "live roots")
    pairing = tuple(sum(((dot(x, y) // 4 + 1) % 2) << j
                        for j, y in enumerate(roots)) for x in roots)
    require(all(dot(x, y) % 4 == 0 for x in roots for y in roots), "integral Gram")
    require(all(row >> i & 1 for i, row in enumerate(pairing)), "pairing diagonal")
    row_basis = basis(pairing, 112)
    require(len(row_basis) == 9, "binary pairing rank")
    labels = tuple(sum(((row >> i) & 1) << k for k, row in enumerate(row_basis))
                   for i in range(112))
    require(len(basis(labels)) == 9 and len(set(labels)) == 112, "faithful labels")
    words = tuple(sum(((w & label).bit_count() % 2) << i
                      for i, label in enumerate(labels)) for w in range(512))
    readers = tuple(tuple(8 * x[k] - sum(x) for k in range(8)) + (4 * sum(x),)
                    for x in roots)
    supports = tuple(tuple(i for i in range(112) if readers[i][k]) for k in range(9))
    require(all(len(basis(tuple(labels[i] for i in support))) == 9
                for support in supports), "all reader spans have rank nine")
    fixed = tuple(i for i, x in enumerate(roots) if sum(x))
    require(len(basis(tuple(labels[i] for i in fixed))) == 9, "forced A1 rank nine")
    return roots, pairing, labels, words, readers, supports


def compatibility(roots, labels, words):
    tables = []
    conflicts = []
    reverse_histograms = []
    exceptional_labels = []
    for k in range(1, 8):
        indices = tuple(i for i, x in enumerate(roots) if x[0] != x[k])
        mask = sum(1 << i for i in indices)
        conflicts.append(indices)
        table = tuple(sum(1 << v for v in range(512)
                          if words[u] & words[v] & mask == 0) for u in range(512))
        tables.append(table)
        ranks = []
        one_labels = []
        for z in range(1, 512):
            space = basis(tuple(labels[i] for i in indices if words[z] >> i & 1))
            ranks.append(len(space))
            if len(space) == 1:
                one_labels.append(space[0])
        histogram = dict(sorted(Counter(ranks).items()))
        reverse_histograms.append(histogram)
        if k == 1:
            require(histogram == {0: 1, 7: 508, 8: 2}, "paired reverse ranks")
        else:
            require(histogram == {1: 1, 7: 254, 8: 255, 9: 1}, "other reverse ranks")
            root = tuple(2 if j == 0 else -2 if j == k else 0 for j in range(8))
            expected = labels[roots.index(root)]
            require(one_labels == [expected], "rank-one space is the named root label")
            exceptional_labels.append(expected)
    require(len(basis(tuple(exceptional_labels))) == 6, "six independent exceptions")
    return tuple(tables), tuple(conflicts), reverse_histograms


def plane_lemma(labels, words, tables, conflicts):
    planes = 0
    two_dimensional = 0
    histogram = Counter()
    for u in range(1, 512):
        for v in range(u + 1, 512):
            if v >= u ^ v:
                continue
            planes += 1
            dimensions = []
            for k in range(7):
                partner_mask = tables[k][u] & tables[k][v]
                size = partner_mask.bit_count()
                require(size > 0 and size & (size - 1) == 0, "partner is a subspace")
                dimension = size.bit_length() - 1
                forbidden = words[u] | words[v]
                rows = tuple(labels[i] for i in conflicts[k] if forbidden >> i & 1)
                require(dimension == 9 - len(basis(rows)), "independent annihilator check")
                require(dimension <= (2 if k == 0 else 1), "punctured plane lemma")
                dimensions.append(dimension)
            two_dimensional += dimensions[0] == 2
            histogram[tuple(sorted(dimensions))] += 1
    require(planes == 43435 and two_dimensional == 254, "complete plane coverage")
    return {"planes": planes, "annihilator_checks": 7 * planes,
            "planes_with_paired_dimension_two": two_dimensional,
            "partner_dimension_histogram": {str(k): v for k, v in sorted(histogram.items())}}


def symmetry(roots, pairing, readers):
    permutations = ((1, 0, 2, 3, 4, 5, 6, 7), (2, 3, 4, 5, 6, 7, 0, 1))
    for permutation in permutations:
        transformed = []
        for row in roots:
            vector = tuple(row[j] for j in permutation)
            if next(x for x in vector if x) < 0:
                vector = tuple(-x for x in vector)
            transformed.append(roots.index(vector))
        require(len(set(transformed)) == 112, "puncture symmetry")
        for i in range(112):
            for j in range(112):
                require((pairing[i] >> j & 1) ==
                        (pairing[transformed[i]] >> transformed[j] & 1), "pairing covariance")
        require(all(sum(row[:8]) == 0 for row in readers), "eight-way dependency")
    orbit = {0}
    for _ in range(8):
        orbit |= {p[j] for p in permutations for j in tuple(orbit)}
    require(orbit == set(range(8)), "all anchor columns covered")


def endpoint(roots, readers, shifts, keep_a1=True):
    """Shifts are exact Gaussian-integer pairs; matrices are scaled by four."""
    require(len(shifts) == 112, "one shift per live line")
    for i, x in enumerate(roots):
        real, imaginary = shifts[i]
        d4 = tuple(4 * (x[k] + real) for k in range(8)) + ((sum(x) if keep_a1 else 0),)
        for j, y in enumerate(roots):
            if dot(d4, readers[j]) != 32 * dot(x, y):
                return False
            if imaginary * sum(readers[j][:8]) != 0:
                return False
    return True


def witnesses_and_controls(roots, pairing, labels, readers, supports, tables):
    shifts = tuple((-row[0], 0) for row in roots)
    require(endpoint(roots, readers, shifts), "rational attaining all-pairs identity")
    row_supports = tuple(tuple(i for i, x in enumerate(roots)
                              if (x[k] != x[0] if k < 8 else sum(x) != 0))
                         for k in range(9))
    ranks = []
    for k in range(9):
        mask = sum(1 << i for i in supports[k])
        actual = len(basis(tuple(pairing[i] & mask for i in row_supports[k]), 112))
        require(actual == len(basis(tuple(labels[i] for i in row_supports[k]))),
                "actual support-pair rank agrees with label rank")
        ranks.append(actual)
    require(ranks == [0, 8, 9, 9, 9, 9, 9, 9, 9] and sum(ranks) == 71, "sharp COPY71")
    require(not endpoint(roots, readers, shifts, keep_a1=False), "missing A1 rejected")
    d4 = tuple(4 * (x - roots[0][0]) for x in roots[0]) + (sum(roots[0]),)
    corrupted = (d4[0] + 1,) + d4[1:]
    require(any(dot(corrupted, readers[j]) != 32 * dot(roots[0], y)
                for j, y in enumerate(roots)), "one bad coefficient rejected")
    changed = ((shifts[0][0] + 1, 0),) + shifts[1:]
    require(endpoint(roots, readers, changed), "independent row shift remains legal")
    generic = tuple((0, 1) for _ in roots)
    require(endpoint(roots, readers, generic), "genuinely complex shifts")
    require(any((tables[0][u] & tables[0][v]).bit_count() == 4
                for u in range(1, 512) for v in range(u + 1, 512) if v < u ^ v),
            "dimension-one transfer fails after puncturing")
    return {"minimum_copy": 71, "attaining_ranks": ranks,
            "all_pairs_per_successful_endpoint": 112 * 112,
            "successful_endpoint_fixtures": 3,
            "control_names": ["deleted A1", "corrupted coefficient", "false dimension-one lemma",
                              "valid changed row", "nonreal shifts"]}


def main():
    roots, pairing, labels, words, readers, supports = model()
    symmetry(roots, pairing, readers)
    tables, conflicts, reverse_histograms = compatibility(roots, labels, words)
    result = plane_lemma(labels, words, tables, conflicts)
    result.update(witnesses_and_controls(roots, pairing, labels, readers, supports, tables))
    result["reverse_rank_histograms"] = reverse_histograms
    here = Path(__file__).resolve().parent
    files = tuple(sorted(path for path in here.iterdir() if path.is_file()))
    require(len(files) <= 8, "package file capacity")
    result["sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    print(json.dumps(result, sort_keys=True))
    print("PASS_A7_A1_P112_COPY71 planes=43435 annihilator_checks=304045 cost=71")


if __name__ == "__main__":
    main()

"""Exact basis tariff for one root-low E8 quotient, produced by Nick Petalas.

Apache-2.0. The A8 root/label model credits conorholds PR3755/4052 and
the retained E8 decoder lineage. No predecessor executable is imported.
"""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys


WIDTH = 10
PACKAGE_FILES = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
                 "VERIFY.json", "verify.py")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    need(len(left) == len(right), "dot-product shape")
    return sum(x * y for x, y in zip(left, right))


def row_basis(rows, width):
    """Forward rational elimination; at most 120 input rows of width ten."""
    need(0 <= width <= WIDTH and len(rows) <= 120, "rational matrix capacity")
    need(all(len(row) == width for row in rows), "rational matrix shape")
    pivots = {}
    for initial in rows:
        row = [Fraction(x) for x in initial]
        for column, old in sorted(pivots.items()):
            factor = row[column]
            row = [x - factor * y for x, y in zip(row, old)]
        column = next((j for j in range(width) if row[j]), None)
        if column is not None:
            scale = row[column]
            pivots[column] = tuple(x / scale for x in row)
    return pivots


def nullspace(rows):
    pivots = row_basis(rows, WIDTH)
    result = []
    for free in range(WIDTH):
        if free in pivots:
            continue
        vector = [Fraction(j == free) for j in range(WIDTH)]
        for column, row in sorted(pivots.items(), reverse=True):
            vector[column] = -sum(row[j] * vector[j]
                                  for j in range(column + 1, WIDTH))
        result.append(tuple(vector))
    need(len(result) + len(pivots) == WIDTH, "rank-nullity")
    need(all(dot(row, vector) == 0 for row in rows for vector in result),
         "computed kernel is not annihilated")
    return result


def modular_rank(rows):
    """Separate column elimination modulo 101 supplies a rational rank lower bound."""
    need(len(rows) <= 120 and all(len(row) == WIDTH for row in rows),
         "modular matrix capacity")
    work = [[int(x) % 101 for x in row] for row in rows]
    rank = 0
    for column in range(WIDTH):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, 101)
        work[rank] = [x * inverse % 101 for x in work[rank]]
        for i in range(rank + 1, len(work)):
            factor = work[i][column]
            for j in range(column, WIDTH):
                work[i][j] = (work[i][j] - factor * work[rank][j]) % 101
        rank += 1
    return rank


def binary_rank(values):
    need(len(values) <= 120 and all(type(x) is int and 0 <= x < 512
                                  for x in values), "binary input capacity")
    pivots = [0] * 9
    for initial in values:
        value = initial
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return sum(bool(x) for x in pivots)


def model():
    roots, labels = [], []
    for i, j in combinations(range(9), 2):
        row = [0] * 9
        row[i], row[j] = 3, -3
        roots.append(tuple(row))
        labels.append(511 ^ (1 << i) ^ (1 << j))
    for subset in combinations(range(9), 3):
        roots.append(tuple(2 if i in subset else -1 for i in range(9)))
        labels.append(sum(1 << i for i in subset))
    need(len(roots) == len(set(roots)) == len(set(labels)) == 120, "root inventory")
    need(all(sum(row) == 0 and dot(row, row) == 18 for row in roots), "root norms")
    need((labels[0], labels[1]) == (508, 506), "distinguished root labels")
    evaluation = [dot(row, roots[1]) // 9 for row in roots]
    need(all(dot(row, roots[1]) % 9 == 0 for row in roots), "root evaluation scale")
    correction = [x if (label & labels[0]).bit_count() % 2 == 0 else 0
                  for label, x in zip(labels, evaluation)]
    matrix = [row[:8] + (int(i == 1), correction[i])
              for i, row in enumerate(roots)]
    need(len(row_basis(matrix, WIDTH)) == WIDTH, "actual quotient dimension")
    return matrix, labels


def special_vectors():
    unit = tuple(int(j == 8) for j in range(WIDTH))
    neighbor = tuple(-2 if j == 8 else int(j == 9) for j in range(WIDTH))
    outside = (1, 0, -1, 0, 0, 0, 0, 0, 0, -3)  # Three times E_a-d.
    return unit, neighbor, outside


def expected_kernel(character, vectors):
    unit, neighbor, outside = vectors
    if character == 508:
        return "eg", [unit, neighbor]
    if character == 506:
        return "gf", [neighbor, outside]
    if character == 505:
        return "ef", [unit, outside]
    if character == 6:
        return "g", [neighbor]
    if character == 3:
        return "f", [outside]
    if (character & 506).bit_count() % 2 == 0:
        return "e", [unit]
    return "zero", []


def validate_kernel(rows, claimed):
    need(len(claimed) <= 2, "claimed kernel capacity")
    need(len(row_basis(claimed, WIDTH)) == len(claimed), "claimed kernel dependence")
    need(all(dot(row, vector) == 0 for row in rows for vector in claimed),
         "claimed kernel annihilation")
    need(modular_rank(rows) == WIDTH - len(claimed), "modular rank certificate")


def kernel_census(matrix, labels, vectors):
    counts, records = Counter(), []
    for character in range(1, 512):
        rows = [row for row, label in zip(matrix, labels)
                if (character & label).bit_count() % 2]
        tag, expected = expected_kernel(character, vectors)
        actual = nullspace(rows)
        need(len(actual) == len(expected), "rational kernel dimension")
        need(len(row_basis(actual + expected, WIDTH)) == len(expected),
             "rational kernel subspace")
        validate_kernel(rows, expected)
        counts[tag] += 1
        records.append([character, tag, len(rows), WIDTH - len(actual)])
    need(dict(counts) == {"zero": 253, "e": 253, "f": 1, "g": 1,
                         "ef": 1, "gf": 1, "eg": 1}, "character census")
    return dict(sorted(counts.items())), records


def support(matrix, vector):
    return [i for i, row in enumerate(matrix) if dot(row, vector)]


def weight(matrix, labels, vector):
    return binary_rank([labels[i] for i in support(matrix, vector)])


def support_certificate(matrix, labels, vectors):
    sets = [set(support(matrix, vector)) for vector in vectors]
    need([len(part) for part in sets] == [1, 28, 28], "disjoint support sizes")
    need(all(not sets[i] & sets[j] for i, j in combinations(range(3), 2)),
         "special supports intersect")
    ranks = {}
    for mask in range(1, 8):
        union = set().union(*(sets[j] for j in range(3) if mask & (1 << j)))
        ranks[str(mask)] = binary_rank([labels[i] for i in sorted(union)])
    need(ranks == {"1": 1, "2": 7, "3": 8, "4": 7,
                   "5": 8, "6": 8, "7": 9}, "support-union ranks")
    return ranks


def attaining_basis(matrix, labels, vectors):
    # Retain seven coordinate evaluation columns complementary to E_a.
    result = list(vectors)
    result.extend(tuple(int(j == i) for j in range(WIDTH))
                  for i in (0, 1, 3, 4, 5, 6, 7))
    need(len(row_basis(result, WIDTH)) == WIDTH, "attaining basis dependence")
    weights = [weight(matrix, labels, vector) for vector in result]
    need(weights == [1, 7, 7] + [9] * 7, "attaining basis weights")
    return weights


def controls(matrix, labels, vectors):
    count = 0
    rows = [row for row, label in zip(matrix, labels) if (508 & label).bit_count() % 2]
    broken = list(vectors[1])
    broken[0] += 1
    trials = ([vectors[0]], [vectors[0], tuple(broken)],
              [vectors[0], vectors[1], vectors[2]])
    for claimed in trials:
        try:
            validate_kernel(rows, claimed)
        except ValueError:
            count += 1
        else:
            raise ValueError("false kernel was accepted")
    need(weight(matrix, labels, tuple(x + y for x, y in zip(vectors[1], vectors[2]))) == 8,
         "two weight-seven directions were incorrectly closed under addition")
    count += 1
    need(weight(matrix, labels, tuple(sum(xs) for xs in zip(*vectors))) == 9,
         "the span of deficient words was mistaken for the deficient locus")
    count += 1
    need(weight(matrix, labels, tuple(int(j == 9) for j in range(WIDTH))) == 8,
         "the unpunctured correction was incorrectly priced seven")
    count += 1
    need(sum(attaining_basis(matrix, labels, vectors)) != 77, "false tariff 77 accepted")
    return count + 1


def verify():
    matrix, labels = model()
    vectors = special_vectors()
    counts, records = kernel_census(matrix, labels, vectors)
    unions = support_certificate(matrix, labels, vectors)
    weights = attaining_basis(matrix, labels, vectors)
    dimensions = [len(row_basis([vector for vector in vectors
                                if weight(matrix, labels, vector) <= cutoff], WIDTH))
                  for cutoff in range(1, 9)]
    need(dimensions == [1] * 6 + [3, 3], "weight-filtration dimensions")
    need(9 * WIDTH - sum(dimensions) == sum(weights) == 78, "filtration tariff identity")
    directory = Path(__file__).resolve().parent
    hashes = {name: sha256((directory / name).read_bytes()).hexdigest()
              for name in PACKAGE_FILES}
    return {"status": "PASS_E8_ROOT_LOW_PLANE", "claim_type": "scoped proof with finite certificate",
            "characters": len(records), "kernel_types": counts,
            "character_records_sha256": sha256(json.dumps(records, separators=(",", ":")).encode()).hexdigest(),
            "support_union_ranks": unions, "filtration_dimensions": dimensions,
            "minimum_basis_profile": weights, "minimum_basis_bill": sum(weights),
            "conditional_copy_lower_bound": 77, "controls": controls(matrix, labels, vectors),
            "package_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new hash-bound JSON receipt")
    arguments = parser.parse_args()
    result = verify()
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.receipt is not None:
        with arguments.receipt.open("x", encoding="utf-8") as stream:
            need(stream.write(output) == len(output), "short receipt write")
    sys.stdout.write(output)


if __name__ == "__main__":
    main()

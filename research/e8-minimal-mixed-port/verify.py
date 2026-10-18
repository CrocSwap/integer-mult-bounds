#!/usr/bin/env python3
"""Exact census of the sharp 14-puncture E8 mixed-port equality case.

Prepared by thakrarsagar with substantial OpenAI Codex assistance. Apache-2.0.
Uses a row basis of the binary Gram matrix, not an orthonormal label factor.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path

SEED = 40


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def parity(x):
    return bin(x).count("1") % 2


def primitive(v):
    den = 1
    for x in v:
        den = den * x.denominator // gcd(den, x.denominator)
    w = [int(x * den) for x in v]
    content = 0
    for x in w:
        content = gcd(content, x)
    require(content != 0, "zero normal")
    w = [x // content for x in w]
    if next(x for x in w if x) < 0:
        w = [-x for x in w]
    return tuple(w)


def echelon(rows):
    basis = []
    for row in rows:
        row = list(row)
        for pivot, b in basis:
            if row[pivot]:
                a, c = row[pivot], b[pivot]
                row = [c * x - a * y for x, y in zip(row, b)]
                content = 0
                for x in row:
                    content = gcd(content, x)
                if content:
                    row = [x // content for x in row]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            basis.append((pivot, row))
    return basis


def normal(rows):
    basis = echelon(rows)
    require(len(basis) == 7, "normal requires rank seven")
    pivots = {i for i, _ in basis}
    free = next(i for i in range(8) if i not in pivots)
    v = [Fraction(int(i == free)) for i in range(8)]
    for pivot, row in reversed(basis):
        v[pivot] = -sum(row[j] * v[j] for j in range(8) if j != pivot) / row[pivot]
    out = primitive(v)
    require(all(dot(out, row) == 0 for row in rows), "incorrect normal")
    return out


def binary_basis(rows):
    basis = {}
    chosen = []
    for i, row in enumerate(rows):
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                chosen.append(i)
                break
            row ^= basis[pivot]
    return chosen


def roots():
    out = []
    for i, j in combinations(range(8), 2):
        for sign in (1, -1):
            v = [0] * 8
            v[i], v[j] = 2, 2 * sign
            out.append(tuple(v))
    out.extend((1,) + s for s in product((1, -1), repeat=7) if s.count(-1) % 2 == 0)
    require(len(out) == 120 and len(set(out)) == 120, "root count")
    require(all(dot(v, v) == 8 for v in out), "root norm")
    require(all(dot(v, w) in (-4, 0, 4) for i, v in enumerate(out) for w in out[i + 1:]), "root pairing")
    return out


def simple_system():
    out = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    for j in range(6):
        v = [0] * 8
        v[j], v[j + 1] = -2, 2
        out.append(tuple(v))
    return out


def check_simple_coordinates(lines, simple):
    # Invert the simple-root column matrix to certify the positive-root premise.
    a = [[Fraction(simple[j][i]) for j in range(8)] + [Fraction(i == j) for j in range(8)] for i in range(8)]
    for j in range(8):
        pivot = next(i for i in range(j, 8) if a[i][j])
        a[j], a[pivot] = a[pivot], a[j]
        c = a[j][j]
        a[j] = [x / c for x in a[j]]
        for i in range(8):
            if i != j:
                c = a[i][j]
                a[i] = [x - c * y for x, y in zip(a[i], a[j])]
    inverse = [row[8:] for row in a]
    for line in lines:
        coords = [dot(row, line) for row in inverse]
        require(all(x.denominator == 1 for x in coords), "nonintegral simple coordinate")
        require(all(x >= 0 for x in coords) or all(x <= 0 for x in coords), "mixed-sign simple coordinates")


def census():
    lines = roots()
    gram = [sum(((1 + dot(v, w) // 4) % 2) << j for j, w in enumerate(lines)) for v in lines]
    basis_order = list(range(SEED, 120)) + list(range(SEED))
    indices = [basis_order[i] for i in binary_basis([gram[j] for j in basis_order])]
    require(len(indices) == 9, "binary Gram rank")
    generators = [gram[i] for i in indices]
    words = [0]
    for g in generators:
        words += [w ^ g for w in words]
    require(len(set(words)) == 512, "reader word independence")
    labels = [words.index(g) for g in gram]

    def pairing(a, b):
        return sum(((a >> i) & 1) * parity(words[b] & (1 << indices[i])) for i in range(9)) % 2

    require(all(pairing(a, a) == 1 for a in labels), "odd root labels")

    def compatible(geometry, lab):
        require(all(pairing(a, a) == 1 for a in lab), "even port label")
        require(all(not dot(v, w) or not pairing(lab[i], lab[j])
                    for i, v in enumerate(geometry) for j, w in enumerate(geometry) if i < j), "incompatible port pair")

    compatible(lines, labels)
    simple = simple_system()
    check_simple_coordinates(lines, simple)
    root_directions = {primitive(v): i for i, v in enumerate(lines)}
    for root in simple:
        permutation = [root_directions[primitive(tuple(x - dot(v, root) // 4 * y for x, y in zip(v, root)))] for v in lines]
        require(len(set(permutation)) == 120, "simple reflection is not a permutation")
        require(all(((gram[i] >> j) & 1) == ((gram[permutation[i]] >> permutation[j]) & 1)
                    for i in range(120) for j in range(120)), "reflection changes binary Gram form")
    flat_receipts = []
    equality = None
    for omitted in range(8):
        n = normal([v for j, v in enumerate(simple) if j != omitted])
        outside = sum((dot(v, n) != 0) << j for j, v in enumerate(lines))
        counts = [bin(w & outside).count("1") for w in words[1:]]
        minimum = min(counts)
        minimizers = [a for a in range(1, 512) if counts[a - 1] == minimum]
        require((n in root_directions) == (minimum == 1), "root-normal exception is not the E7 flat")
        flat_receipts.append({"omitted_simple_root": omitted, "normal": n,
                              "root_lines": 120 - bin(outside).count("1"),
                              "minimum_deletions": minimum, "minimizer_count": len(minimizers),
                              "odd_minimizer_count": sum(pairing(a, a) for a in minimizers)})
        if minimum == 14:
            require(equality is None and len(minimizers) == 1, "nonunique D7 equality")
            z = minimizers[0]
            puncture = words[z] & outside
            equality = n, z, puncture
    require(sorted(x["minimum_deletions"] for x in flat_receipts) == [1, 14, 27, 28, 33, 35, 40, 43], "hyperplane thresholds")
    n, z, puncture = equality
    live = [i for i in range(120) if not (puncture >> i) & 1]
    geometry = [lines[i] for i in live]
    lab = [labels[i] for i in live]
    require(len(live) == 106 and len(binary_basis(lab)) == 9, "live label rank")

    def reader_data(geometry, lab):
        spans = [[v for v, u in zip(geometry, lab) if pairing(a, u)] for a in range(1, 512)]
        ranks = [len(echelon(rows)) for rows in spans]
        order = sorted(range(1, 512), key=lambda a: (ranks[a - 1], a))
        chosen = [order[j] for j in binary_basis(order)]
        return spans, ranks, chosen, sum(ranks[a - 1] for a in chosen)

    spans, ranks, chosen, cost = reader_data(geometry, lab)
    cheap = []
    nonroot = []
    for a, rank in enumerate(ranks, 1):
        if rank < 8:
            require(rank == 7, "reader below rank seven")
            direction = normal(spans[a - 1])
            record = {"functional": a, "odd": bool(pairing(a, a)), "normal": direction,
                      "root_normal": direction in root_directions}
            cheap.append(record)
            if not record["root_normal"]:
                nonroot.append(record)
    require(len(nonroot) == 1 and nonroot[0]["functional"] == z and nonroot[0]["normal"] == n, "nonroot candidate classification")
    compatible(geometry + [n], lab + [z])
    _, mixed_ranks, mixed_chosen, mixed_cost = reader_data(geometry + [n], lab + [z])
    require(set(mixed_ranks) == {8} and mixed_cost == 72, "augmented reader ranks")
    require(pairing(z, z) == 1 and dot(n, n) != 0, "duplicate-port obstruction")

    def rejects(action):
        try:
            action()
        except ValueError:
            return True
        raise ValueError("negative control was accepted")

    deleted = [i for i in range(120) if (puncture >> i) & 1]
    controls = {
        "duplicate_nonroot_port": rejects(lambda: compatible(geometry + [n, n], lab + [z, z])),
        "even_added_label": rejects(lambda: compatible(geometry + [n], lab + [0])),
        "restored_deleted_root": all(rejects(lambda i=i: compatible(geometry + [lines[i], n], lab + [labels[i], z])) for i in deleted),
        "rank_eight_has_no_normal": rejects(lambda: normal(lines)),
        "corrupt_simple_system": rejects(lambda: check_simple_coordinates(lines, simple[:-1] + [(0, 0, 0, 0, 0, -2, 0, 2)])),
    }
    return {
        "base_commit": "66849e1475c930fd7732b1a0067ffee7e1e95f60", "assignment_seed": SEED,
        "binary_gram_basis_root_indices": indices,
        "root_lines": 120, "label_dimension": 9, "nonzero_readers": 511,
        "simple_reflections_checked": 8,
        "reader_weight_histogram": dict(sorted(Counter(bin(w).count("1") for w in words[1:]).items())),
        "maximal_parabolic_flats": flat_receipts,
        "equality_puncture": deleted, "added_normal": n, "added_label_coefficients": z,
        "cheap_readers": cheap,
        "root_only": {"ports": 106, "rank_histogram": dict(sorted(Counter(ranks).items())), "star_basis": chosen, "star_cost": cost},
        "one_added_port": {"ports": 107, "rank_histogram": dict(sorted(Counter(mixed_ranks).items())), "star_basis": mixed_chosen, "star_cost": mixed_cost,
                           "ratio": str(Fraction(mixed_cost, 107)), "comparison_ratio": "21/37",
                           "ratio_strictly_worse": Fraction(mixed_cost, 107) > Fraction(63, 111)},
        "negative_controls": controls,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--print-receipt", action="store_true")
    args = parser.parse_args()
    result = census()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    expected = Path(__file__).with_name("results.json")
    require(encoded == expected.read_text(), "receipt mismatch")
    if args.print_receipt:
        print(encoded, end="")
    else:
        print("PASS: 8 maximal flats; 511 readers before and after augmentation; one non-root candidate; 5 negative-control categories")
        print("star costs:", result["root_only"]["star_cost"], "on 106 ports;", result["one_added_port"]["star_cost"], "on 107 ports")


if __name__ == "__main__":
    main()

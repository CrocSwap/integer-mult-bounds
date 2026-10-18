#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate finite checker: Weyl orbit, column elimination, maximal cliques.

No imports from verify.py or predecessor packages. This is implementation
independence within one AI-assisted contribution, not independent human review.
"""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(a, b):
    return sum(x * y for x, y in zip(a, b))


def weyl_lines():
    simple = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(6):
        root = [0] * 8
        root[i], root[i + 1] = -2, 2
        simple.append(tuple(root))
    found = {simple[0]}
    pending = [simple[0]]
    while pending:
        r = pending.pop()
        for a in simple:
            pairing = scalar(r, a)
            ensure(pairing % 4 == 0, "reflection integrality")
            reflected = tuple(x - (pairing // 4) * y for x, y in zip(r, a))
            ensure(scalar(reflected, reflected) == 8, "reflection norm")
            if reflected not in found:
                found.add(reflected)
                pending.append(reflected)
    ensure(len(found) == 240, "Weyl orbit size")
    return sorted(r for r in found if next(x for x in r if x) > 0)


def binary_column_rank(columns):
    # Lowest-pivot column elimination, instead of the primary row-echelon routine.
    columns = set(columns) - {0}
    dimension = 0
    while columns:
        pivot = min(columns)
        columns.remove(pivot)
        low = pivot & -pivot
        columns = {v ^ pivot if v & low else v for v in columns} - {0}
        dimension += 1
    return dimension


def maximal_cliques(neighbors, order):
    """Bron-Kerbosch with excluded vertices and a maximum-neighbor pivot."""
    position = {v: i for i, v in enumerate(order)}
    result = []

    def extend(chosen, possible, excluded):
        if not possible and not excluded:
            result.append(tuple(sorted(chosen)))
            return
        pivot = max(possible | excluded,
                    key=lambda v: (len(possible & neighbors[v]), -position[v]))
        for v in sorted(possible - neighbors[pivot], key=position.get):
            extend(chosen + [v], possible & neighbors[v], excluded & neighbors[v])
            possible.remove(v)
            excluded.add(v)

    extend([], set(order), set())
    return sorted(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path,
                        default=Path(__file__).with_name("CERTIFICATE.json"))
    args = parser.parse_args()
    try:
        receipt = json.loads(args.certificate.read_text())
        roots = weyl_lines()
        ensure(len(roots) == 120, "root-line count")
        gram = [[scalar(a, b) // 4 for b in roots] for a in roots]
        puncture = []
        for i, r in enumerate(roots):
            support = [j for j, x in enumerate(r) if x]
            if len(support) == 2 and support[0] % 2 == 0 and support[1] == support[0] + 1:
                puncture.append(i)
        ensure(puncture == receipt["puncture"] and len(puncture) == 8, "puncture")
        live = set(range(120)) - set(puncture)
        order = sorted(live)
        # Seed 36 diversifies the vertex order, not the mathematical domain.
        order = order[36:] + order[:36]
        orth = {i: {j for j in live if i != j and gram[i][j] == 0} for i in live}
        nonorth = {i: live - orth[i] - {i} for i in live}
        orth_maximal = maximal_cliques(orth, order)
        frames = [f for f in orth_maximal if len(f) == 8]
        ensure(len(frames) == receipt["frames"] == 1260, "independent frame census")
        ensure(max(map(len, orth_maximal)) == 8, "orthogonal rank bound")
        membership = {i: {k for k, f in enumerate(frames) if i in f} for i in live}
        ensure({len(x) for x in membership.values()} == {90}, "normal/frame coverage")
        extension_counts = []
        for i, j in combinations(sorted(live), 2):
            common = membership[i] & membership[j]
            ensure(bool(common) == (gram[i][j] == 0), "pair/frame extension")
            if common:
                extension_counts.append(len(common))
        ensure({str(k): v for k, v in Counter(extension_counts).items()}
               == receipt["orthogonal_pair_extension_histogram"], "extension histogram")

        columns = [sum(((gram[i][j] + 1) % 2) << i for i in range(120))
                   for j in range(120)]
        supports = []
        for a in range(120):
            full = {i for i in live if gram[i][a] != 0}
            for trimmed in (False, True):
                s = full - {a} if trimmed else full
                supports.append((a, trimmed, s))
                missing = {k for k, f in enumerate(frames) if not s.intersection(f)}
                ensure(missing == (membership.get(a, set()) if trimmed else set()),
                       "independent star/frame identity")
        rank_histogram = Counter()
        rank_cache = {}
        for a, ta, s in supports:
            row_mask = sum(1 << i for i in s)
            for b, tb, t in supports:
                col_mask = sum(1 << j for j in t)
                key = (row_mask, col_mask)
                if key not in rank_cache:
                    rank_cache[key] = binary_column_rank(columns[j] & row_mask for j in t)
                beta = rank_cache[key]
                rank_histogram[beta] += 1
                classified = (gram[a][b] in (-1, 1) and (ta or a not in live)
                              and (tb or b not in live))
                ensure((beta == 7) == classified, "independent rank-seven classification")
        ensure(dict(rank_histogram) == {7: 7616, 8: 37440, 9: 12544}, "independent atom floor")
        ensure({str(k): v for k, v in rank_histogram.items()} == receipt["rank_histogram"],
               "rank receipt mismatch")

        maximal = maximal_cliques(nonorth, order)
        histogram = Counter(map(len, maximal))
        ensure(max(histogram) == receipt["maximum_nonorthogonal_clique"] == 8,
               "independent nine-normal exclusion")
        witness = receipt["maximum_clique_witness"]
        ensure(len(set(witness)) == 8 and set(witness) <= live
               and all(gram[i][j] != 0 for i, j in combinations(witness, 2)), "clique witness")
        complete9 = {i: set(range(9)) - {i} for i in range(9)}
        ensure(maximal_cliques(complete9, list(range(9))) == [tuple(range(9))],
               "synthetic nine-clique control")
        ensure(binary_column_rank([0, 1, 2, 3]) == 2
               and binary_column_rank([0, 1, 2, 3, 4]) == 3, "rank mutation control")

        # Independently check the attaining 8-term construction and every charged support.
        for i in live:
            for j in live:
                ensure(sum(gram[i][f] * gram[j][f] for f in puncture) == 2 * gram[i][j],
                       "independent coordinate identity")
        for f in puncture:
            s = {i for i in live if gram[i][f]}
            mask = sum(1 << i for i in s)
            ensure(binary_column_rank(columns[j] & mask for j in s) == 8,
                   "independent coordinate price")
        ensure(receipt["cost_floor"] == 64, "claimed cost floor")
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"FAIL_INDEPENDENT_MASKED_STAR: {error}", file=sys.stderr)
        return 1
    print("PASS_INDEPENDENT_MASKED_STAR weyl_roots=240 atoms=57600 frames=1260 "
          f"maximal_cliques={dict(sorted(histogram.items()))} cost_floor=64")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

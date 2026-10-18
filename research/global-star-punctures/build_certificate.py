#!/usr/bin/env python3
"""Construct a finite F2 certificate; the separate verifier imports none of this.

Copyright 2026 Alishan Ladhani. SPDX-License-Identifier: Apache-2.0
Prepared with substantial OpenAI Codex assistance.
"""
import argparse
from itertools import combinations, product
import json
from pathlib import Path


def ports(p, k):
    return [sum(1 << (2 * pair + sign) for pair, sign in zip(pairs, signs))
            for pairs in combinations(range(p), k)
            for signs in product((0, 1), repeat=k)]


def coordinates(mask):
    return [i for i in range(12) if mask >> i & 1]


def build():
    family = ports(6, 4)
    stars = [s for degree in (1, 2, 3) for s in ports(6, degree)]
    generators = [sum(1 << i for i, s in enumerate(family) if s & l == l)
                  for l in stars]
    basis, independent = {}, []
    for index, vector in enumerate(generators):
        while vector:
            pivot = vector.bit_length() - 1
            if pivot in basis:
                vector ^= basis[pivot]
            else:
                basis[pivot] = vector
                independent.append(index)
                break

    def remainder(vector):
        for pivot in sorted(basis, reverse=True):
            if vector >> pivot & 1:
                vector ^= basis[pivot]
        return vector

    remainders = [remainder(1 << i) for i in range(240)]
    free = [i for i in range(240) if i not in basis]
    checks = [sum(1 << i for i, r in enumerate(remainders) if r >> f & 1)
              for f in free]
    syndromes = [sum(1 << j for j, h in enumerate(checks) if h >> i & 1)
                 for i in range(240)]
    target = 42
    other = [i for i in range(240) if i != target]
    pair_map = {}
    for a, b in combinations(other, 2):
        key = syndromes[a] ^ syndromes[b]
        if key in pair_map:
            raise ValueError("pair syndromes are not unique")
        pair_map[key] = (a, b)
    short = {0} | {syndromes[i] for i in other} | set(pair_map)
    intersections = len(short & {syndromes[target] ^ v for v in short})
    solutions, hits, triples = set(), 0, 0
    for a, b, c in combinations(other, 3):
        triples += 1
        pair = pair_map.get(syndromes[target] ^ syndromes[a] ^ syndromes[b] ^ syndromes[c])
        if pair is not None:
            deleted = tuple(sorted(set(pair) ^ {a, b, c}))
            if len(deleted) != 5:
                raise ValueError("unexpected smaller support")
            solutions.add(deleted)
            hits += 1
    witnesses = []
    for deleted in sorted(solutions):
        support = sum(1 << i for i in (target,) + deleted)
        matches = [i for i, g in enumerate(generators) if g == support]
        if len(matches) != 1:
            raise ValueError("minimum support is not a unique proper star")
        witnesses.append({"deleted_indices": list(deleted),
                          "star_coordinates": coordinates(stars[matches[0]])})
    return {
        "format": "global-star-punctures-v1",
        "assignment_seed": 42,
        "instance": {"p": 6, "k": 4, "target_index": target,
                     "target_coordinates": coordinates(family[target]),
                     "port_order": "pair combinations lexicographic, then sign tuples lexicographic; coordinate 2*pair+sign"},
        "code": {"ports": 240, "proper_stars": 232, "overlap_corrections": 3,
                 "rank": len(basis), "dual_rank": len(checks),
                 "independent_star_indices": independent,
                 "information_set": sorted(basis),
                 "parity_checks_hex": [format(h, '060x') for h in checks],
                 "empty_star_in_span": remainder((1 << 240) - 1) == 0},
        "enumeration": {"other_ports": len(other), "pairs": len(pair_map),
                        "zero_single_pair_syndromes": len(short),
                        "translated_intersections": intersections,
                        "triples": triples, "triple_pair_hits": hits,
                        "optimal_deletion_sets": len(solutions),
                        "minimum_deletions": 5},
        "optimal_deletions": witnesses,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(build(), indent=2) + '\n', encoding='utf-8')
    print('WROTE_GLOBAL_STAR_PUNCTURES', args.output)

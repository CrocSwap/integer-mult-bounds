#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the full P104 family with a separate partition census."""
import argparse
from collections import Counter
from itertools import combinations, product
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise ValueError(message)


def root_lines():
    rows = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            rows.add(tuple(row))
    for tail in product((-1, 1), repeat=7):
        row = (1,) + tail
        if row.count(-1) % 2 == 0:
            rows.add(row)
    check(len(rows) == 120, 'root line count')
    return sorted(rows)


def members(mask):
    return [i for i in range(8) if mask & (1 << i)]


def exact_census():
    roots = root_lines()
    gram = [[sum(x * y for x, y in zip(a, b)) // 4 for b in roots] for a in roots]
    frame = []
    for i in range(0, 8, 2):
        for sign in (-1, 1):
            row = tuple(2 if j == i else 2 * sign if j == i + 1 else 0 for j in range(8))
            frame.append(roots.index(row))
    pool = set(range(120)) - set(frame)
    neighbours = [{j for j in pool if i != j and gram[i][j] == 0} for i in range(120)]
    frames = []

    def extend(chosen, available):
        if len(chosen) == 8:
            frames.append(chosen)
            return
        if len(chosen) + len(available) < 8:
            return
        for vertex in sorted(available):
            extend(chosen + (vertex,), {j for j in available & neighbours[vertex] if j > vertex})

    extend((), pool)
    check(len(frames) == 1260, 'disjoint frame count')
    masks = {k: [sum(1 << i for i in subset) for subset in combinations(range(8), k)]
             for k in range(9)}
    support_families = Counter()
    census = Counter()
    for other in frames:
        live = sorted(pool - set(other))
        incidence = [sum(1 << i for i, a in enumerate(frame) if gram[a][b]) for b in other]
        found = 0
        # Every eight-element row basis is a partition of the two frames.
        for left in range(256):
            size = left.bit_count()
            eligible = sum(1 << j for j in range(8) if (incidence[j] & left).bit_count() == 1)
            for right_columns in masks[size]:
                if right_columns & ~eligible:
                    continue
                left_rows = [incidence[j] & left for j in members(right_columns)]
                if len(set(left_rows)) != size:
                    continue
                right_rows = 255 ^ right_columns
                partners = []
                valid = True
                for i in members(255 ^ left):
                    options = [j for j in members(right_rows) if incidence[j] >> i & 1]
                    if len(options) != 1:
                        valid = False
                        break
                    partners.append(options[0])
                if not valid or len(set(partners)) != 8 - size:
                    continue
                row_normals = [frame[i] for i in members(left)] + [other[j] for j in members(right_rows)]
                supports = tuple(sorted(sum(1 << k for k, a in enumerate(row_normals) if gram[t][a])
                                        for t in live))
                check(len(set(supports)) == 104, 'distinct supports')
                support_families[supports] += 1
                found += 1
        census[found] += 1
    check(census == Counter({0: 364, 8: 896}), 'partition census')
    check(sum(support_families.values()) == 7168, 'decoder count')
    return support_families


def cube_transport(supports):
    adjacency = [set() for _ in range(8)]
    for support in supports:
        if support.bit_count() == 2:
            a, b = members(support)
            adjacency[a].add(b)
            adjacency[b].add(a)
    check(all(len(row) == 3 for row in adjacency), 'cube degrees')
    target = [{j for j in range(8) if (i ^ j).bit_count() == 1} for i in range(8)]
    answer = None

    def extend(mapping, available):
        nonlocal answer
        if len(mapping) == 8:
            answer = mapping
            return True
        vertex = len(mapping)
        for candidate in sorted(available):
            if all((old in target[vertex]) == (mapping[old] in adjacency[candidate])
                   for old in range(vertex)):
                if extend(mapping + [candidate], available - {candidate}):
                    return True
        return False

    check(extend([], set(range(8))), 'cube graph isomorphism')
    return {sum(1 << j for j, old in enumerate(answer) if support >> old & 1) for support in supports}


def check_certificate(certificate):
    supports = set(certificate['cube_supports'])
    for retained_text, witness in certificate['projections'].items():
        retained = int(retained_text)
        universe = {frozenset(members(x & retained)) for x in supports} - {frozenset()}
        antichain = [frozenset(members(x)) for x in witness['antichain']]
        chains = [[frozenset(members(x)) for x in chain] for chain in witness['chains']]
        check(len(antichain) == len(set(antichain)), 'distinct antichain')
        check(set(antichain) <= universe, 'antichain domain')
        check(all(not a <= b and not b <= a for a, b in combinations(antichain, 2)), 'antichain order')
        flattened = [x for chain in chains for x in chain]
        check(set(flattened) == universe and len(flattened) == len(universe), 'chain partition')
        check(all(chain and all(a < b for a, b in zip(chain, chain[1:])) for chain in chains), 'chain order')
        expected = 32 if retained == 255 else 26
        check(witness['width'] == len(antichain) == len(chains) == expected, 'exact width')
    check(set(certificate['projections']) == {'255'} | {str(255 ^ (1 << k)) for k in range(8)},
          'projection coverage')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, digest in pins['files'].items():
        check(hashlib.sha256((args.repo / path).read_bytes()).hexdigest() == digest, 'source pin: ' + path)
    for path, record in pins['vendored'].items():
        check(hashlib.sha256((HERE / path).read_bytes()).hexdigest() == record['sha256'],
              'vendored source pin: ' + path)
    certificate = json.loads((HERE / 'CERTIFICATE.json').read_text())
    check_certificate(certificate)
    families = exact_census()
    for family in families:
        check(cube_transport(family) == set(certificate['cube_supports']), 'transported support family')
    print('PASS_P104_INDEPENDENT partition_census=7168 graph_isomorphisms=' + str(len(families)) +
          ' antichains=9 chain_covers=9')


if __name__ == '__main__':
    main()

# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the fixed P104 endpoint sets and actual two-plane covers."""

from collections import Counter
from itertools import combinations, product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(a, b):
    return (a & b).bit_count() % 2


def span(basis):
    require(len(basis) <= 9, 'frame dimension')
    points = {0}
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512 and vector not in points,
                'independent binary basis')
        points |= {point ^ vector for point in tuple(points)}
    return frozenset(points)


def reconstruct(witness, fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    roots |= {(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0}
    puncture = fixture['section4_explicit_P104']
    ports = sorted(roots - {tuple(v) for v in puncture['F0'] + puncture['C']})
    require(len(roots) == 120 and len(ports) == 104, 'ordered P104 roots')
    names = [f'{kind}{i}' for kind in 'XY' for i in range(104)]
    paths = {name: [span(witness['initial_frames'][name])] for name in names}
    paid = Counter()
    require(len(witness['program']) == 4058, 'frozen word length')
    for event in witness['program']:
        if event[0] != 'transport':
            continue
        _, name, before, after, rank = event
        paid[rank] += 1
        if name in paths:
            old, new = span(before), span(after)
            require(paths[name][-1] == old < new and rank == len(after) - len(before),
                    'chronological monotone data frames')
            paths[name].append(new)
    for name in names:
        require(paths[name][-1] == span(witness['final_frames'][name]), 'final frame')
    return ports, paths, dict(paid)


def residuals(ports, paths):
    sources = [paths[f'X{s}'] for s in range(104)]
    targets = [paths[f'Y{t}'] for t in range(104)]
    require(all(len(p[0]) == 2 and len(p[-1]) == 512 for p in sources), 'X endpoints')
    require(all(p[0] == {0} and len(p[-1]) == 256 for p in targets), 'Y endpoints')
    labels = [next(iter(p[0] - {0})) for p in sources]
    normals = []
    for path in targets:
        dual = [n for n in range(1, 512) if all(not parity(n, v) for v in path[-1])]
        require(len(dual) == 1, 'target normal')
        normals.append(dual[0])
    require(len(set(labels)) == len(set(normals)) == 104, 'distinct endpoints')
    arrival, departure = [set() for _ in range(104)], [set() for _ in range(104)]
    demands = 0
    for t, left in enumerate(ports):
        for s, right in enumerate(ports):
            gram = sum(a * b for a, b in zip(left, right, strict=True))
            require((labels[s] in targets[t][-1]) == (gram % 8 == 4), 'Gram/frame binding')
            if gram == 8 * int(t == s):
                continue
            demands += 1
            require(targets[t][-1] not in sources[s] and sources[s][0] not in targets[t],
                    'no direct endpoint bypass')
            if not any(labels[s] in v for v in targets[t][:-1]):
                arrival[t].add(labels[s])
            if not any(len(v) > 2 and v <= targets[t][-1] for v in sources[s]):
                departure[s].add(normals[t])
    require(demands == 4992, 'correction support')
    return {'arrival': (arrival, normals), 'departure': (departure, labels)}


def plane_cover(points, normal):
    """Return an explicit maximum plane and its affine complement."""
    require(0 < len(points) <= 48 and 0 not in points, 'residual domain')
    require(all(not parity(v, normal) for v in points), 'endpoint containment')
    odd = [q for q in range(1, 512) if all(parity(v, q) for v in points)]
    require(bool(odd), 'odd affine section')
    candidates = [f for f in range(1, 512) if f != normal]
    f = max(candidates, key=lambda a: sum(not parity(a, v) for v in points))
    q, g = odd[0], f ^ odd[0]
    require(g not in (0, normal), 'complement proper')
    endpoint = {v for v in range(512) if not parity(v, normal)}
    first = {v for v in endpoint if not parity(v, f)}
    second = {v for v in endpoint if not parity(v, g)}
    require(len(first) == len(second) == 128, 'two dimension-seven subspaces')
    left, right = points & first, points & second
    require(not left & right and left | right == points, 'disjoint exact cover')
    require(0 < len(left) < len(points), 'residual spans endpoint')
    return {'demand': len(points), 'capacity': len(left), 'q': q, 'f': f, 'g': g}


def pair_oracle(points, normal):
    """Enumerate distinct restricted planes, without the affine construction."""
    ordered = sorted(points)
    masks = {sum(1 << i for i, v in enumerate(ordered) if not parity(v, f))
             for f in range(1, 512) if f != normal}
    maximum = max(mask.bit_count() for mask in masks)
    union = max((a | b).bit_count() for a in masks for b in masks)
    return maximum, union

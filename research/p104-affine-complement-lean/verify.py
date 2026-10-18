#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Reconstruct the finite P104 hypotheses of the separate Lean geometry lemma."""

import argparse
import hashlib
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUT = 'research/p104-native-channel/inputs/'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), 'duplicate JSON key')
    return result


def load(path):
    require(path.stat().st_size <= 2_000_000, 'JSON size bound')
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def inputs():
    manifest = load(PACKAGE / 'SOURCES.json')
    rows = [row for row in manifest['files'] if row['usage'] == 'input']
    require({row['path'] for row in rows} ==
            {INPUT + 'LOWRANK-WITNESS.json', INPUT + 'P104-FIXTURE.json',
             'formal/lean/lake-manifest.json', 'formal/lean/lakefile.toml',
             'formal/lean/lean-toolchain'}, 'input paths')
    require(len(rows) == 5, 'five input pins')
    result = {}
    for row in rows:
        path = ROOT / row['path']
        require(path.stat().st_size <= 2_000_000, 'source size bound')
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source hash')
        if row['path'].startswith(INPUT):
            result[path.name] = json.loads(data, object_pairs_hook=unique)
    return result['LOWRANK-WITNESS.json'], result['P104-FIXTURE.json']


def span(basis):
    require(len(basis) <= 9, 'basis size bound')
    result = {0}
    for value in basis:
        require(type(value) is int and 0 < value < 512 and value not in result,
                'independent binary basis')
        result |= {value ^ old for old in tuple(result)}
    return frozenset(result)


def parity(a, b):
    return (a & b).bit_count() % 2


def rank(points):
    require(len(points) <= 48 and all(type(v) is int and 0 < v < 512 for v in points),
            'point count and bit-width bounds')
    basis = [0] * 9
    for point in points:
        for bit in range(8, -1, -1):
            if point & (1 << bit):
                if basis[bit]:
                    point ^= basis[bit]
                else:
                    basis[bit] = point
                    break
    return sum(bool(v) for v in basis)


def geometry(witness, fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    roots |= {(1, *s) for s in product((-1, 1), repeat=7) if s.count(-1) % 2 == 0}
    puncture = fixture['section4_explicit_P104']
    ports = sorted(roots - {tuple(v) for v in puncture['F0'] + puncture['C']})
    require(len(roots) == 120 and len(ports) == 104, 'ordered P104 ports')
    paths = {f'{k}{i}': [span(witness['initial_frames'][f'{k}{i}'])]
             for k in 'XY' for i in range(104)}
    require(len(witness['program']) == 4058, 'frozen event count')
    for event in witness['program']:
        if event[0] == 'transport' and event[1] in paths:
            _, name, before, after, jump = event
            require(paths[name][-1] == span(before) < span(after), 'monotone data path')
            require(jump == len(after) - len(before), 'rank-gap binding')
            paths[name].append(span(after))
    for name in paths:
        require(paths[name][-1] == span(witness['final_frames'][name]), 'final frame')
    x, y = [paths[f'X{i}'] for i in range(104)], [paths[f'Y{i}'] for i in range(104)]
    require(all(len(p[0]) == 2 and len(p[-1]) == 512 for p in x), 'source endpoints')
    require(all(p[0] == {0} and len(p[-1]) == 256 for p in y), 'target endpoints')
    labels = [next(iter(p[0] - {0})) for p in x]
    normals = []
    for p in y:
        dual = [n for n in range(1, 512) if all(parity(n, v) == 0 for v in p[-1])]
        require(len(dual) == 1, 'unique target normal')
        normals.append(dual[0])
    require(len(set(labels)) == len(set(normals)) == 104, 'distinct endpoints')
    return ports, x, y, labels, normals


def residuals(geo):
    ports, x, y, labels, normals = geo
    arrival, departure = [set() for _ in ports], [set() for _ in ports]
    count = 0
    for t in range(104):
        for s in range(104):
            gram = sum(a * b for a, b in zip(ports[t], ports[s], strict=True))
            require((labels[s] in y[t][-1]) == (gram % 8 == 4), 'Gram/frame binding')
            if gram == 8 * int(t == s):
                continue
            count += 1
            require(y[t][-1] not in x[s] and x[s][0] not in y[t], 'no endpoint bypass')
            if not any(labels[s] in frame for frame in y[t][:-1]):
                arrival[t].add(labels[s])
            if not any(len(frame) > 2 and frame <= y[t][-1] for frame in x[s]):
                departure[s].add(normals[t])
    require(count == 4992, 'correction demand count')
    return [('arrival', arrival, normals), ('departure', departure, labels)]


def check_cover(points, normal, q, f):
    require(0 < normal < 512 and 0 < q < 512 and 0 < f < 512, 'form bounds')
    require(len(points) <= 48 and rank(points) == 8, 'spanning demand set')
    require(all(parity(v, normal) == 0 and parity(v, q) == 1 for v in points),
            'endpoint and odd-section hypotheses')
    endpoint = {v for v in range(512) if parity(v, normal) == 0}
    left = {v for v in endpoint if parity(v, f) == 0}
    right = {v for v in endpoint if parity(v, f ^ q) == 0}
    require(0 < len(points & left) < len(points), 'nontrivial split')
    require(len(left) == len(right) == 128, 'dimension-seven kernels')
    require(not points & left & right and points <= left | right, 'exact disjoint cover')
    return len(points & left), len(points & right)


def calculate():
    witness, fixture = inputs()
    geo = geometry(witness, fixture)
    covers, census = [], Counter()
    for direction, rows, normals in residuals(geo):
        require(sum(map(len, rows)) == 4656, 'residual total per orientation')
        for i, (points, normal) in enumerate(zip(rows, normals, strict=True)):
            odd = [q for q in range(1, 512) if all(parity(v, q) == 1 for v in points)]
            require(bool(odd), 'odd section exists')
            f = max((f for f in range(1, 512) if f != normal),
                    key=lambda f: sum(parity(v, f) == 0 for v in points))
            left, right = check_cover(points, normal, odd[0], f)
            census[len(points), left, right] += 1
            covers.append([direction, i, normal, odd[0], f, left, right])
    require(len(covers) == 208, 'all endpoint hypotheses checked')
    return {'endpoints': 208, 'residuals_per_orientation': 4656,
            'census': [list(key) + [value] for key, value in sorted(census.items())],
            'covers_sha256': hashlib.sha256(json.dumps(covers).encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if not args.emit:
        require(json.dumps(result, sort_keys=True) ==
                json.dumps(load(PACKAGE / 'RESULT.json'), sort_keys=True), 'typed receipt')
    print(json.dumps(result, sort_keys=True, indent=2))
    print('PASS_P104_AFFINE_PREMISES endpoints=208 no_circuit_or_cost_claim')


if __name__ == '__main__':
    main()

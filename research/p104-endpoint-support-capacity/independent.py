#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent bitset/Fourier census, with no primary or predecessor imports."""

import hashlib
import json
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    require(path.stat().st_size <= 2_000_000, 'JSON capacity')
    return json.loads(path.read_bytes())


def source(name):
    manifest = read_json(PACKAGE / 'SOURCES.json')
    require(len(manifest['files']) <= 10, 'manifest capacity')
    path = 'research/p104-native-channel/inputs/' + name
    rows = [r for r in manifest['files'] if r['path'] == path and r['usage'] == 'input']
    require(len(rows) == 1, 'input pin')
    require((ROOT / path).stat().st_size <= 2_000_000, 'input capacity')
    data = (ROOT / path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == rows[0]['sha256'],
            'independent source hash')
    return json.loads(data)


def frame(basis):
    require(len(basis) <= 9, 'binary dimension')
    vectors = [0]
    for vector in basis:
        require(type(vector) is int and 0 < vector < 512, 'binary basis element')
        vectors += [v ^ vector for v in vectors]
    require(len(set(vectors)) == len(vectors), 'independent basis')
    return sum(1 << v for v in vectors)


def parity_kernel(normal):
    return sum(1 << v for v in range(512) if (v & normal).bit_count() % 2 == 0)


def model():
    witness, fixture = source('LOWRANK-WITNESS.json'), source('P104-FIXTURE.json')
    require(len(witness['program']) == 4058, 'source word length')
    paths = [[frame(witness['initial_frames'][f'{kind}{i}'])]
             for kind in 'XY' for i in range(104)]
    for event in witness['program']:
        if event[0] == 'transport' and event[1][0] in 'XY':
            index = int(event[1][1:]) + (104 if event[1][0] == 'Y' else 0)
            require(paths[index][-1] == frame(event[2]), 'chronological path')
            after = frame(event[3])
            require(paths[index][-1] & after == paths[index][-1], 'nested path')
            paths[index].append(after)
    require(all(len(p) <= 10 for p in paths), 'bounded data paths')
    require(all(paths[i][0].bit_count() == 2 for i in range(104)), 'source lines')
    labels = [(paths[i][0] ^ 1).bit_length() - 1 for i in range(104)]
    kernels = {parity_kernel(n): n for n in range(1, 512)}
    normals = [kernels[paths[104 + t][-1]] for t in range(104)]
    roots = []
    for axes in combinations(range(8), 2):
        for sign in [-1, 1]:
            roots.append(tuple(2 if i == axes[0] else 2 * sign if i == axes[1] else 0
                               for i in range(8)))
    roots += [(1, *s) for s in product([-1, 1], repeat=7) if sum(s) % 4 == 3]
    removed = fixture['section4_explicit_P104']
    ports = sorted(set(roots) - set(map(tuple, removed['F0'] + removed['C'])))
    require(len(roots) == 120 and len(ports) == 104, 'independent root order')
    required = [[sum(ports[t][i] * ports[s][i] for i in range(8)) != 8 * (s == t)
                 for s in range(104)] for t in range(104)]
    require(sum(map(sum, required)) == 4992, 'independent demand count')
    return paths, labels, normals, required


def fourier_cap(points, normal):
    require(len(set(points)) == len(points) <= 48, 'residual alphabet')
    spectrum = [0] * 512
    for point in points:
        spectrum[point] = 1
    # Nine bounded Walsh-Hadamard stages, computing all character sums.
    for bit in range(9):
        stride = 1 << bit
        for block in range(0, 512, 2 * stride):
            for j in range(block, block + stride):
                a, b = spectrum[j], spectrum[j + stride]
                spectrum[j], spectrum[j + stride] = a + b, a - b
    require(spectrum[0] == spectrum[normal] == len(points), 'ambient annihilator')
    value, witness = max((spectrum[a], a) for a in range(1, 512) if a != normal)
    require((len(points) + value) % 2 == 0, 'integer intersection count')
    return {'residual': len(points), 'proper_max': (len(points) + value) // 2,
            'witness': witness}


def calculate():
    paths, labels, normals, required = model()
    arrival, departure = [], []
    for t in range(104):
        earlier = 0
        for mask in paths[104 + t][:-1]:
            earlier |= mask
        points = [labels[s] for s in range(104) if required[t][s]
                  and not earlier & (1 << labels[s])
                  and paths[104 + t][-1] not in paths[s]]
        arrival.append(fourier_cap(points, normals[t]))
    for s in range(104):
        targets = []
        for t in range(104):
            if not required[t][s]:
                continue
            endpoint = paths[104 + t][-1]
            if not any(mask.bit_count() > 2 and mask & endpoint == mask for mask in paths[s]):
                targets.append(normals[t])
        departure.append(fourier_cap(targets, labels[s]))
    return arrival, departure


def main():
    arrival, departure = calculate()
    expected = read_json(PACKAGE / 'RESULT.json')
    require(arrival == expected['arrival_endpoints'], 'independent arrival receipt')
    require(departure == expected['departure_endpoints'], 'independent departure receipt')
    require(sum(r['residual'] for r in arrival) == 4656
            and sum(r['residual'] for r in departure) == 4656, 'both residual totals')
    require(max(r['proper_max'] for r in arrival + departure) == 30, 'capacity maximum')
    require(fourier_cap([1 << i for i in range(8)], 256)
            == {'residual': 8, 'proper_max': 7, 'witness': 384},
            'proper rather than ambient hyperplane control')
    print('PASS_INDEPENDENT_ENDPOINT_SUPPORT orientations=2 endpoints=208 required=4656 cap=30')


if __name__ == '__main__':
    main()

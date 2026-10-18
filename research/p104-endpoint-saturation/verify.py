#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify the demand-saturated endpoint allocation relaxation using integers."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from geometry import census, endpoint_data, paths, ports, require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def read_json(path):
    require(path.stat().st_size <= 2_000_000, 'input byte bound')
    return json.loads(path.read_bytes())


def authenticated_inputs():
    manifest = read_json(PACKAGE / 'SOURCES.json')
    require(len(manifest['files']) <= 10, 'manifest record bound')
    inputs = {}
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        require(row['path'] in {
            'research/p104-native-channel/inputs/LOWRANK-WITNESS.json',
            'research/p104-native-channel/inputs/P104-FIXTURE.json'}, 'input path')
        path = ROOT / row['path']
        require(path.stat().st_size <= 2_000_000, 'source byte bound')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                'source SHA256 mismatch')
        inputs[path.name] = read_json(path)
    require(len(inputs) == 2, 'two original geometric inputs')
    snapshot = PACKAGE / 'predecessor/RESULT.json'
    require(snapshot.stat().st_size <= 2_000_000, 'predecessor byte bound')
    require(hashlib.sha256(snapshot.read_bytes()).hexdigest()
            == manifest['predecessor']['sha256'], 'predecessor snapshot SHA256')
    return inputs, read_json(snapshot)


def marginal_certificate(endpoints):
    require(0 < len(endpoints) <= 104, 'endpoint count')
    gains = []
    for index, (demand, capacity) in enumerate(endpoints):
        require(type(demand) is int and type(capacity) is int
                and 0 < capacity < demand <= 2 * capacity <= 60, 'endpoint bounds')
        gains.extend([(capacity, index, 0), (demand - capacity, index, 1)])
    gains.sort(key=lambda row: (-row[0], row[1], row[2]))
    require(all(gains.index((c, i, 0)) < gains.index((d - c, i, 1))
                for i, (d, c) in enumerate(endpoints)),
            'prefix-feasible marginal order')
    coverage = [0]
    for gain, _, _ in gains:
        coverage.append(coverage[-1] + gain)
    require(coverage[-1] == sum(d for d, _ in endpoints), 'complete coverage')
    return gains, coverage


def dynamic_minimum_cheap(endpoints):
    """Independent allocation DP: no marginal sorting or primary curve input."""
    require(0 < len(endpoints) <= 104, 'DP endpoint count')
    limit = 2 * len(endpoints)
    unreachable = 1 + sum(d for d, _ in endpoints)
    costs = [0] + [unreachable] * limit
    for index, (demand, capacity) in enumerate(endpoints):
        require(0 < capacity < demand <= 2 * capacity <= 60, 'DP endpoint bounds')
        updated = [unreachable] * (limit + 1)
        for used in range(2 * index + 1):
            for added in range(3):
                value = costs[used] + max(0, demand - added * capacity)
                updated[used + added] = min(updated[used + added], value)
        costs = updated
    require(costs[0] == sum(d for d, _ in endpoints) and costs[-1] == 0,
            'DP endpoint cases')
    return costs


def allocation(gains, units, endpoints):
    require(0 <= units <= len(gains) == 2 * len(endpoints), 'allocation size')
    assigned = [0] * len(endpoints)
    for _, index, _ in gains[:units]:
        assigned[index] += 1
    return [[u, max(0, demand - capacity * u)]
            for u, (demand, capacity) in zip(assigned, endpoints, strict=True)]


def calculate():
    inputs, predecessor = authenticated_inputs()
    data = endpoint_data(paths(inputs['LOWRANK-WITNESS.json']),
                         ports(inputs['P104-FIXTURE.json']))
    result = {}
    for orientation, pair in zip(('arrival', 'departure'), data, strict=True):
        endpoints = census(*pair)
        old = predecessor[orientation + '_endpoints']
        require(endpoints == [(x['residual'], x['proper_max']) for x in old],
                'original word agrees with every predecessor endpoint')
        gains, coverage = marginal_certificate(endpoints)
        costs = dynamic_minimum_cheap(endpoints)
        require(costs == [4656 - c for c in coverage], 'all 209 DP and greedy values')
        minimum = min(u for u, cheap in enumerate(costs) if u + cheap <= 400)
        require(minimum == 192 and costs[147] == 937 and coverage[147] == 3719,
                'literal rejection and threshold')
        require(253 + 30 * 147 == 4663 and 3719 + 253 == 3972 < 4656,
                'aggregate passes while saturation fails')
        result[orientation] = {
            'endpoint_types': [list(k) + [v]
                               for k, v in sorted(Counter(endpoints).items())],
            'minimum_cheap_by_units': costs,
            'profile_253_147': {'maximum_coverage': 3972, 'deficit': 684},
            'minimum_units_at_400': minimum,
            'relaxed_assignment_at_threshold': allocation(gains, minimum, endpoints),
            'threshold_cheap': costs[minimum],
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(json.dumps(result, sort_keys=True) == json.dumps(
            read_json(PACKAGE / 'RESULT.json'), sort_keys=True),
                'typed receipt equality')
        print('PASS_P104_ENDPOINT_SATURATION deficit=684 minimum_units_at_400=192')


if __name__ == '__main__':
    main()

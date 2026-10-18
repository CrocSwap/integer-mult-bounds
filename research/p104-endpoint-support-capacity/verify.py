#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check finite endpoint-support premises; see README.md for the network proof."""

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, pairwise, product
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
INPUT_ROOT = 'research/p104-native-channel/inputs/'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique(pairs):
    result = dict(pairs)
    need(len(result) == len(pairs), 'duplicate JSON key')
    return result


def read_json(path):
    need(path.stat().st_size <= 2_000_000, 'JSON capacity')
    data = path.read_bytes()
    return json.loads(data, object_pairs_hook=unique)


def inputs():
    manifest = read_json(PACKAGE / 'SOURCES.json')
    need(len(manifest['files']) <= 10, 'manifest capacity')
    result = {}
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        need(row['path'] in {INPUT_ROOT + 'LOWRANK-WITNESS.json',
                             INPUT_ROOT + 'P104-FIXTURE.json',
                             'research/complex-local-word-ceiling/ceiling.py',
                             'research/community-frontier1094-audit/ASSEMBLY.json'}, 'declared input')
        path = ROOT / row['path']
        need(path.stat().st_size <= 2_000_000, 'source capacity')
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source hash')
        result[Path(row['path']).name] = data
    need(len(result) == 4, 'four authenticated inputs')
    return result


def span(basis):
    need(len(basis) <= 9, 'frame dimension')
    result = {0}
    for vector in basis:
        need(type(vector) is int and 0 < vector < 512, 'binary vector')
        result |= {x ^ vector for x in tuple(result)}
    need(len(result) == 1 << len(basis), 'independent frame basis')
    return frozenset(result)


def data_paths(witness):
    need(len(witness['program']) == 4058, '4058 frozen events')
    paid = Counter()
    paths = {f'{kind}{i}': [span(witness['initial_frames'][f'{kind}{i}'])]
             for kind in 'XY' for i in range(104)}
    for event in witness['program']:
        op, dst = event[:2]
        need(op in {'add', 'copy', 'zero', 'erase', 'transport'}, 'known event')
        if op in {'add', 'copy'}:
            need(not dst.startswith('X') and not event[2].startswith('Y'),
                 'immutable X and unread Y')
        if op in {'zero', 'erase'}:
            need(not dst.startswith(('X', 'Y')), 'no data lifetime reset')
        if op == 'transport':
            paid[event[4]] += 1
        if op == 'transport' and dst in paths:
            before, after = span(event[2]), span(event[3])
            need(paths[dst][-1] == before < after, 'nested data path')
            need(event[4] == len(event[3]) - len(event[2]), 'transport rank')
            paths[dst].append(after)
    for name, frames in paths.items():
        need(len(frames) <= 10, 'at most nine data jumps')
        need(frames[-1] == span(witness['final_frames'][name]), 'final data frame')
    need(paid == {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8},
         'original channel transport profile')
    return paths


def root_ports(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    removed = fixture['section4_explicit_P104']
    ports = sorted(roots - {tuple(v) for v in removed['F0'] + removed['C']})
    need(len(roots) == 120 and len(ports) == 104, 'P104 port order')
    return ports


def geometry(witness, fixture):
    paths, ports = data_paths(witness), root_ports(fixture)
    lines = [paths[f'X{s}'][0] for s in range(104)]
    hyper = [paths[f'Y{t}'][-1] for t in range(104)]
    need(all(len(v) == 2 for v in lines) and all(len(v) == 256 for v in hyper),
         'line and hyperplane endpoints')
    need(len(set(lines)) == len(set(hyper)) == 104, 'distinct endpoints')
    need(all(len(paths[f'X{s}'][-1]) == 512 for s in range(104))
         and all(paths[f'Y{t}'][0] == {0} for t in range(104)), 'FULL and ZERO')
    labels = [next(v for v in line if v) for line in lines]
    normals = []
    for frame in hyper:
        choices = [a for a in range(1, 512)
                   if all((v & a).bit_count() % 2 == 0 for v in frame)]
        need(len(choices) == 1, 'unique hyperplane normal')
        normals.append(choices[0])
    for alphabet in (labels, normals):
        need(any(all((q & a).bit_count() % 2 for q in alphabet)
                 for a in range(1, 512)), 'affine odd alphabet')
    demands = set()
    for t, left in enumerate(ports):
        for s, right in enumerate(ports):
            gram4 = sum(a * b for a, b in zip(left, right, strict=True))
            need(gram4 % 4 == 0, 'integral Gram entry')
            need((labels[s] in hyper[t]) == (gram4 % 8 == 4), 'root/frame binding')
            if 8 * int(t == s) != gram4:
                demands.add((t, s))
    need(len(demands) == 4992, 'correction demand count')
    return paths, labels, hyper, normals, demands


def residual_sets(geo):
    paths, labels, hyper, normals, demands = geo
    arrivals, departures = [], []
    for t in range(104):
        arrivals.append([labels[s] for s in range(104) if (t, s) in demands
                         and not any(labels[s] in v for v in paths[f'Y{t}'][:-1])
                         and hyper[t] not in paths[f'X{s}']])
    for s in range(104):
        departures.append([normals[t] for t in range(104) if (t, s) in demands
                           and not any(len(v) > 2 and v <= hyper[t]
                                       for v in paths[f'X{s}'])])
    need(all(hyper[t] not in paths[f'X{s}'] for t, s in demands), 'no direct bypass')
    need(all(paths[f'X{s}'][0] not in paths[f'Y{t}']
             for t in range(104) for s in range(104)), 'no target line bypass')
    return arrivals, departures


def endpoint_census(residuals, annihilators):
    rows = []
    for points, normal in zip(residuals, annihilators, strict=True):
        need(len(points) == len(set(points)) <= 48, 'distinct residual labels')
        need(len(span_basis(points)) == 8, 'residual span has dimension eight')
        need(all((p & normal).bit_count() % 2 == 0 for p in points), 'ambient endpoint')
        candidates = [(sum((p & a).bit_count() % 2 == 0 for p in points), a)
                      for a in range(1, 512) if a != normal]
        maximum, witness = max(candidates)
        rows.append({'residual': len(points), 'proper_max': maximum, 'witness': witness})
    return rows


def span_basis(points):
    basis = {}
    for point in points:
        value = point
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if bit in basis:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return basis


def support_weight(dimension):
    return 0 if dimension == 0 else min(1 << (dimension - 1), 30)


def history_weights(jumps):
    need(0 < len(jumps) <= 9 and all(type(r) is int and r > 0 for r in jumps)
         and sum(jumps) == 9, 'positive composition of nine')
    before = arrival = departure = 0
    for jump in jumps:
        after = before + jump
        if after == 8:
            arrival = support_weight(before)
        if before == 1:
            departure = support_weight(9 - after)
        before = after
    return arrival, departure


def profiles():
    rows = []
    for cheap, unit, verdict in [(329, 71, False), (335, 71, False), (253, 147, True)]:
        support = cheap + 30 * unit
        need((support >= 4656) == verdict, 'support screen verdict')
        need(387 <= cheap + unit <= 482 and cheap + 64 * unit >= 4680,
             'old count and crossing screens')
        rows.append({'cheap': cheap, 'unit': unit, 'lifetimes': cheap + unit,
                     'span_total': cheap + 7 * unit, 'support_total': support,
                     'cut_capacity': cheap + 64 * unit,
                     'ideal_idle_mass': 4344 - 9 * (cheap + unit),
                     'support_rows_pass': verdict})
    return rows


def budget_controls(sources, profiles_to_price):
    # Run only the authenticated self-contained cost engine, never adjacent .pyc.
    cost = ModuleType('credited_cost_engine')
    engine_path = ROOT / 'research/complex-local-word-ceiling/ceiling.py'
    # Fixed SHA256-authenticated code only; this excludes source-adjacent caches.
    exec(compile(sources['ceiling.py'], str(engine_path), 'exec'), cost.__dict__)  # noqa: S102
    assembly = json.loads(sources['ASSEMBLY.json'], object_pairs_hook=unique)
    saving = Fraction(assembly['complex_lower'])
    need(saving == Fraction(67018507072324140917, 40000000000000000000000),
         'selected primitive saving')
    base = {1: 1074, 2: 58, 3: 86, 4: 104, 5: 48, 6: 24, 7: 8, 8: 8}
    for row in profiles_to_price:
        profile = Counter(base)
        profile[1] += 2 * row['cheap'] + 9 * row['unit']
        profile[7] += row['cheap']
        _, upper = cost.relax(profile, 73, 832, 9, 56, saving)
        need(upper < 1, 'favorable declared cost relaxation')
        scale = 10**15
        rounded = -((-upper.numerator * scale) // upper.denominator)
        row['moment_upper'] = f'{rounded // scale}.{rounded % scale:015d}'
    return profiles_to_price


def calculate():
    sources = inputs()
    witness = json.loads(sources['LOWRANK-WITNESS.json'], object_pairs_hook=unique)
    fixture = json.loads(sources['P104-FIXTURE.json'], object_pairs_hook=unique)
    geo = geometry(witness, fixture)
    arrivals, departures = residual_sets(geo)
    censuses = [endpoint_census(arrivals, geo[3]), endpoint_census(departures, geo[1])]
    for census in censuses:
        need(sum(row['residual'] for row in census) == 4656, 'residual demand sum')
        need(Counter(row['proper_max'] for row in census) == {24: 12, 28: 24, 29: 24, 30: 44},
             'proper-subspace capacity census')
    weights = []
    for mask in range(256):
        stops = [0] + [i for i in range(1, 9) if mask & (1 << (i - 1))] + [9]
        jumps = [b - a for a, b in pairwise(stops)]
        a, d = history_weights(jumps)
        need(history_weights(jumps[::-1]) == (d, a), 'dual history reversal')
        weights.append([a, d])
    need(history_weights([1, 7, 1]) == (1, 1), 'cheap carrier control')
    need(history_weights([1] * 9) == (30, 30), 'unit-step control')
    need(history_weights([8, 1]) == history_weights([1, 8]) == (0, 0), 'empty visits')
    need(history_weights([1, 1, 6, 1]) == (2, 30), 'asymmetric endpoint control')
    return {'arrival_endpoints': censuses[0], 'departure_endpoints': censuses[1],
            'required_per_orientation': 4656, 'proper_capacity': 30,
            'history_weights': weights, 'profiles': budget_controls(sources, profiles())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print recomputed receipt')
    args = parser.parse_args()
    result = calculate()
    if not args.emit:
        expected = read_json(PACKAGE / 'RESULT.json')
        need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
             'typed receipt equality')
    print(json.dumps(result, sort_keys=True, indent=2))
    print('PASS_P104_ENDPOINT_SUPPORT required=4656 capacity=30 rejected=406 control=400')


if __name__ == '__main__':
    main()

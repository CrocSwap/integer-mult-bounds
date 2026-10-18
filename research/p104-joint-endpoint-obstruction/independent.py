# SPDX-License-Identifier: Apache-2.0
"""Independent finite joint-endpoint audit, using only authenticated JSON."""

import argparse
import hashlib
import json
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'LOWRANK-WITNESS.json':
        '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e',
    'P104-FIXTURE.json':
        '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_input(name):
    path = ROOT / 'research/p104-native-channel/inputs' / name
    require(path.stat().st_size <= 2_000_000, 'oversized original JSON')
    raw = path.read_bytes()
    require(len(raw) <= 2_000_000, 'oversized original JSON read')
    require(hashlib.sha256(raw).hexdigest() == PINS[name], 'original input hash')
    return json.loads(raw)


def frame(basis):
    """Encode a binary span as an integer with 512 membership bits."""
    require(isinstance(basis, list) and len(basis) <= 9, 'binary basis length')
    members = [0]
    for v in basis:
        require(type(v) is int and 0 < v < 512 and v not in members,
                'independent binary basis vector')
        members += [old ^ v for old in tuple(members)]
    return sum(1 << v for v in members)


def ordered_ports(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            point = [0] * 8
            point[i], point[j] = 2, sign * 2
            roots.add(tuple(point))
    for tail in product((-1, 1), repeat=7):
        if sum(x == -1 for x in tail) % 2 == 0:
            roots.add((1, *tail))
    section = fixture['section4_explicit_P104']
    deleted = {tuple(point) for point in section['F0'] + section['C']}
    require(len(roots) == 120 and len(deleted) == 16, 'E8 puncture cardinalities')
    ports = sorted(roots - deleted)
    require(len(ports) == 104, 'P104 port cardinality')
    return ports


def data_paths(witness):
    names = [f'{kind}{i}' for kind in 'XY' for i in range(104)]
    paths = {name: [frame(witness['initial_frames'][name])] for name in names}
    require(len(witness['program']) == 4058, 'frozen program length')
    for event in witness['program']:
        if event[0] != 'transport':
            continue
        _, name, old_basis, new_basis, rank = event
        if name not in paths:
            continue
        old, new = frame(old_basis), frame(new_basis)
        require(paths[name][-1] == old and old != new and old & ~new == 0,
                'data transport inclusion and continuity')
        require(rank == len(new_basis) - len(old_basis), 'data transport rank')
        paths[name].append(new)
    for name in names:
        require(paths[name][-1] == frame(witness['final_frames'][name]),
                'frozen final data frame')
        require(len(paths[name]) <= 10, 'monotone path bound')
    return paths


def endpoint_data(paths):
    sources = [paths[f'X{s}'] for s in range(104)]
    targets = [paths[f'Y{t}'] for t in range(104)]
    require(all(p[0].bit_count() == 2 and p[-1].bit_count() == 512
                for p in sources), 'source endpoint dimensions')
    require(all(p[0] == 1 and p[-1].bit_count() == 256
                for p in targets), 'target endpoint dimensions')
    labels = [(p[0] ^ 1).bit_length() - 1 for p in sources]
    normals = []
    for path in targets:
        final = path[-1]
        perpendicular = [n for n in range(1, 512)
                         if all(not (n & v).bit_count() % 2
                                for v in range(512) if final >> v & 1)]
        require(len(perpendicular) == 1, 'unique target normal')
        normals.append(perpendicular[0])
    require(len(set(labels)) == len(set(normals)) == 104, 'distinct endpoints')
    return sources, targets, labels, normals


def demand_graph(ports, sources, targets, labels, normals):
    arrivals, departures = [0] * 104, [0] * 104
    original_demands = 0
    for s, t in product(range(104), repeat=2):
        dot = sum(ports[s][i] * ports[t][i] for i in range(8))
        require(bool(targets[t][-1] >> labels[s] & 1) == (dot % 8 == 4),
                'root incidence agrees with frame incidence')
        if dot == 8 * int(s == t):
            continue
        original_demands += 1
        require(targets[t][-1] not in sources[s] and sources[s][0] not in targets[t],
                'no direct source/target endpoint contact')
        if not any(v >> labels[s] & 1 for v in targets[t][:-1]):
            arrivals[t] |= 1 << s
        if not any(v.bit_count() > 2 and v & ~targets[t][-1] == 0
                   for v in sources[s]):
            departures[s] |= 1 << t
    require(original_demands == 4992, 'frozen correction support size')
    require(sum(v.bit_count() for v in arrivals) == 4656, 'arrival residual count')
    require(sum(v.bit_count() for v in departures) == 4656, 'departure residual count')
    return arrivals, departures


def capacity(indices, vectors, normal):
    """Count every proper section using an integer character transform."""
    points = [vectors[i] for i in range(104) if indices >> i & 1]
    require(0 < len(points) <= 48, 'residual endpoint bound')
    require(all(not (v & normal).bit_count() % 2 for v in points),
            'residual endpoint containment')
    chars = [0] * 512
    for v in points:
        chars[v] += 1
    for stage in range(9):
        width = 1 << stage
        for start in range(0, 512, 2 * width):
            for offset in range(width):
                i, j = start + offset, start + offset + width
                chars[i], chars[j] = chars[i] + chars[j], chars[i] - chars[j]
    best = max((len(points) + chars[n]) // 2
               for n in range(1, 512) if n != normal)
    require(best < len(points) <= 2 * best, 'proper capacity and two-carrier bound')
    return best


def type_groups(residual, capacities, types):
    groups = [[i for i in range(104) if (residual[i].bit_count(), capacities[i]) == t]
              for t in types]
    require([len(group) for group in groups] == [12, 8, 24, 24, 24, 12],
            'six endpoint type populations')
    return groups


def mutual_blocks(arrivals, departures, source_groups, target_groups):
    rows = [sum(1 << t for t in range(104)
                if departures[s] >> t & 1 and arrivals[t] >> s & 1)
            for s in range(104)]
    require(sum(row.bit_count() for row in rows) == 4368, 'mutual residual count')
    columns = [sum(1 << s for s in range(104) if rows[s] >> t & 1)
               for t in range(104)]
    source_masks = [sum(1 << s for s in group) for group in source_groups]
    target_masks = [sum(1 << t for t in group) for group in target_groups]
    row_max = [[max((rows[s] & mask).bit_count() for s in group)
                for mask in target_masks] for group in source_groups]
    column_max = [[max((columns[t] & mask).bit_count() for t in group)
                   for group in target_groups] for mask in source_masks]
    return row_max, column_max


def deficiency_patterns(types, populations):
    """Assign 17 missing broad contacts relative to two at every endpoint."""
    partial = [((), 0, 0)]
    for (demand, cap), population in zip(types, populations, strict=True):
        next_partial = []
        for counts, missing, price in partial:
            for zero in range(min(population, (17 - missing) // 2) + 1):
                for one in range(min(population - zero, 17 - missing - 2 * zero) + 1):
                    new_missing = missing + 2 * zero + one
                    new_price = price + demand * zero + (demand - cap) * one
                    if new_price <= 232:
                        next_partial.append((counts + (zero + one,),
                                             new_missing, new_price))
                        require(len(next_partial) <= 1_000_000,
                                'bounded deficiency state count')
        partial = next_partial
    patterns = [(counts, price) for counts, missing, price in partial if missing == 17]
    require(len(patterns) == 337, 'feasible six-type deficiency pattern count')
    return patterns


def overlap_audit(patterns, row_max, column_max):
    best, witness = None, None
    for (source, source_cost), (target, target_cost) in product(patterns, repeat=2):
        overlap = sum(min(source[i] * target[j], source[i] * row_max[i][j],
                          target[j] * column_max[i][j])
                      for i, j in product(range(6), repeat=2))
        required = source_cost + target_cost - overlap
        if best is None or required < best:
            best = required
            witness = [list(source), list(target), source_cost, target_cost, overlap]
    require(best == 300, 'conditional joint cheap union lower bound')
    return best, witness


def three_class_audit():
    states = []
    for p, q, z in product(range(13), range(9), range(9)):
        r = 17 - z - p - q
        price = 12 * p + 15 * q + 16 * r + 24 * z
        if r >= 0 and price <= 232:
            states.append((p, q, r, price))
    require(len(states) == 34, 'three-class deficiency count')
    lower = 1000
    for (p, q, r, price), (pp, qq, rr, other_price) in product(states, repeat=2):
        overlap = ((p + q + r) * rr + (pp + qq + rr) * r - r * rr
                   + 4 * min(p, pp) + 6 * (q + qq))
        lower = min(lower, price + other_price - overlap)
    require(lower == 235, 'three-class conditional union lower bound')
    return lower


def audit():
    witness, fixture = load_input('LOWRANK-WITNESS.json'), load_input('P104-FIXTURE.json')
    paths = data_paths(witness)
    sources, targets, labels, normals = endpoint_data(paths)
    arrivals, departures = demand_graph(ordered_ports(fixture), sources, targets,
                                       labels, normals)
    ac = [capacity(arrivals[t], labels, normals[t]) for t in range(104)]
    dc = [capacity(departures[s], normals, labels[s]) for s in range(104)]
    types = [(36, 24), (45, 30), (44, 28), (46, 29), (47, 30), (48, 30)]
    ag, dg = type_groups(arrivals, ac, types), type_groups(departures, dc, types)
    row_max, column_max = mutual_blocks(arrivals, departures, dg, ag)
    require(row_max[0][0] == column_max[0][0] == 4
            and row_max[1][1] == 0 and row_max[1][0] == column_max[0][1] == 6,
            'three-class graph premises')
    patterns = deficiency_patterns(types, [len(group) for group in ag])
    lower, attaining = overlap_audit(patterns, row_max, column_max)
    return {'patterns': len(patterns), 'lower': lower, 'attaining': attaining,
            'row_max': row_max, 'column_max': column_max,
            'three_class_patterns': 34, 'three_class_lower': three_class_audit()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print a recomputed JSON receipt')
    args = parser.parse_args()
    result = audit()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print('PASS_P104_JOINT_ENDPOINT_INDEPENDENT patterns=337 lower=300')


if __name__ == '__main__':
    main()

# SPDX-License-Identifier: Apache-2.0
"""Reconstruct endpoint demands without importing predecessor implementations."""

from itertools import combinations, product


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def frame(vectors):
    require(len(vectors) <= 9, 'at most nine basis vectors')
    points = [0]
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512, 'binary vector')
        require(vector not in points, 'independent frame basis')
        points += [point ^ vector for point in points]
    return sum(1 << point for point in points)


def paths(witness):
    require(len(witness['program']) == 4058, 'frozen 4058-event word')
    names = [f'{kind}{i}' for kind in 'XY' for i in range(104)]
    result = {name: [frame(witness['initial_frames'][name])] for name in names}
    for event in witness['program']:
        op, destination = event[:2]
        require(op in {'transport', 'add', 'copy', 'zero', 'erase'}, 'known event')
        if op in {'add', 'copy'}:
            require(not destination.startswith('X') and not event[2].startswith('Y'),
                    'immutable sources and unread targets')
        if op in {'zero', 'erase'}:
            require(destination not in result, 'no data reinitialization')
        if op == 'transport' and destination in result:
            before, after = frame(event[2]), frame(event[3])
            require(result[destination][-1] == before and before != after
                    and before & after == before, 'increasing chronological path')
            require(event[4] == len(event[3]) - len(event[2]), 'transport rank')
            result[destination].append(after)
    for name, chain in result.items():
        require(len(chain) <= 10 and chain[-1] == frame(witness['final_frames'][name]),
                'complete data path')
    return result


def ports(fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1, *signs) for signs in product((-1, 1), repeat=7)
              if sum(sign < 0 for sign in signs) % 2 == 0]
    removed = fixture['section4_explicit_P104']
    excluded = {tuple(row) for row in removed['F0'] + removed['C']}
    result = sorted(set(roots) - excluded)
    require(len(roots) == 120 and len(result) == 104, 'ordered P104 roots')
    return result


def endpoint_data(chain, roots):
    source = [chain[f'X{i}'] for i in range(104)]
    target = [chain[f'Y{i}'] for i in range(104)]
    require(all(c[0].bit_count() == 2 and c[-1].bit_count() == 512 for c in source)
            and all(c[0] == 1 and c[-1].bit_count() == 256 for c in target),
            'line-to-FULL and ZERO-to-hyperplane endpoints')
    labels = [c[0].bit_length() - 1 for c in source]
    normals = []
    for c in target:
        candidates = [a for a in range(1, 512)
                      if all(not (q & a).bit_count() % 2 for q in range(512)
                             if c[-1] >> q & 1)]
        require(len(candidates) == 1, 'unique endpoint normal')
        normals.append(candidates[0])
    require(len(set(labels)) == len(set(normals)) == 104, 'distinct endpoints')
    arrivals, departures = [[] for _ in range(104)], [[] for _ in range(104)]
    demands = 0
    for t, left in enumerate(roots):
        for s, right in enumerate(roots):
            gram = sum(a * b for a, b in zip(left, right, strict=True))
            require(bool(target[t][-1] >> labels[s] & 1) == (gram % 8 == 4),
                    'root-to-frame binding')
            if gram == 8 * int(t == s):
                continue
            demands += 1
            require(target[t][-1] not in source[s], 'no direct endpoint bypass')
            require(source[s][0] not in target[t], 'no target visits source line')
            if not any(c >> labels[s] & 1 for c in target[t][:-1]):
                arrivals[t].append(labels[s])
            if not any(c.bit_count() > 2 and c & target[t][-1] == c for c in source[s]):
                departures[s].append(normals[t])
    require(demands == 4992, '4992 correction coefficients')
    return (arrivals, normals), (departures, labels)


def census(residuals, annihilators):
    result = []
    for points, normal in zip(residuals, annihilators, strict=True):
        require(0 < len(points) == len(set(points)) <= 48, 'residual size')
        require(all(not (point & normal).bit_count() % 2 for point in points),
                'residual belongs to endpoint')
        maximum = max(sum(not (point & a).bit_count() % 2 for point in points)
                      for a in range(1, 512) if a != normal)
        require(maximum < len(points), 'residual spans endpoint')
        result.append((len(points), maximum))
    require(sum(d for d, _ in result) == 4656, '4656 residual demands')
    return result

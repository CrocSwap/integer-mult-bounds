#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the P104 support census and the asynchronous carrier bound."""
import argparse
from collections import Counter, deque
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def check_sources(repo):
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, expected in pins['files'].items():
        require(hashlib.sha256((repo / path).read_bytes()).hexdigest() == expected,
                'source hash: ' + path)
    for path, record in pins['vendored'].items():
        require(hashlib.sha256((HERE / path).read_bytes()).hexdigest() == record['sha256'],
                'vendored source hash: ' + path)
    return pins


def bits(mask):
    return [i for i in range(8) if mask >> i & 1]


def cube_family(adjacency):
    result = []
    for support in range(1, 255):
        small = support if support.bit_count() <= 5 else 255 ^ support
        vertices = bits(small)
        if not 2 <= len(vertices) <= 5:
            continue
        edges = sum((adjacency[v] & small).bit_count() for v in vertices) // 2
        reached = {vertices[0]}
        frontier = list(reached)
        while frontier:
            vertex = frontier.pop()
            for other in bits(adjacency[vertex] & small):
                if other not in reached:
                    reached.add(other)
                    frontier.append(other)
        if edges == len(vertices) - 1 and len(reached) == len(vertices):
            result.append(support)
    return tuple(result)


def cube_chart(supports):
    adjacency = [0] * 8
    for support in supports:
        if support.bit_count() == 2:
            a, b = bits(support)
            adjacency[a] |= 1 << b
            adjacency[b] |= 1 << a
    require(all(row.bit_count() == 3 for row in adjacency), 'cube degree')
    a, b, c = bits(adjacency[0])
    common = []
    for x, y in ((a, b), (a, c), (b, c)):
        values = bits(adjacency[x] & adjacency[y] & ~1)
        require(len(values) == 1, 'cube square')
        common.append(values[0])
    ab, ac, bc = common
    opposite = bits(adjacency[ab] & adjacency[ac] & adjacency[bc])
    require(len(opposite) == 1, 'cube opposite')
    order = [0, a, b, ab, c, ac, bc, opposite[0]]
    require(len(set(order)) == 8, 'cube vertices')
    require(all(bool(adjacency[order[i]] >> order[j] & 1) ==
                ((i ^ j).bit_count() == 1) for i in range(8) for j in range(8)),
            'cube edges')
    require(tuple(sorted(supports)) == cube_family(adjacency), 'cube support family')
    return order


def poset_certificate(supports):
    values = sorted(set(supports) - {0})
    edges = [[j for j, y in enumerate(values) if x != y and x & y == x]
             for x in values]
    match = [-1] * len(values)

    def augment(left, seen):
        for right in edges[left]:
            if right not in seen:
                seen.add(right)
                if match[right] < 0 or augment(match[right], seen):
                    match[right] = left
                    return True
        return False

    for left in range(len(values)):
        augment(left, set())
    successor = {left: right for right, left in enumerate(match) if left >= 0}
    chains = []
    for start in range(len(values)):
        if match[start] < 0:
            chain = [start]
            while chain[-1] in successor:
                chain.append(successor[chain[-1]])
            chains.append([values[i] for i in chain])
    left_seen = set(range(len(values))) - set(successor)
    right_seen = set()
    queue = deque(left_seen)
    while queue:
        left = queue.popleft()
        for right in edges[left]:
            if successor.get(left) != right and right not in right_seen:
                right_seen.add(right)
                if match[right] >= 0 and match[right] not in left_seen:
                    left_seen.add(match[right])
                    queue.append(match[right])
    antichain = [values[i] for i in sorted(left_seen - right_seen)]
    result = dict(width=len(antichain), antichain=antichain, chains=chains)
    check_poset_certificate(values, result)
    return result


def check_poset_certificate(supports, certificate):
    values = set(supports) - {0}
    antichain = certificate['antichain']
    chains = certificate['chains']
    require(len(antichain) == len(set(antichain)), 'antichain duplicate')
    require(set(antichain) <= values, 'antichain member')
    require(all(a & b not in (a, b) for a, b in itertools.combinations(antichain, 2)),
            'antichain comparison')
    flattened = [x for chain in chains for x in chain]
    require(len(flattened) == len(set(flattened)) and set(flattened) == values,
            'chain cover')
    require(all(chain and all(a != b and a & b == a for a, b in zip(chain, chain[1:]))
                for chain in chains), 'chain comparison')
    require(certificate['width'] == len(antichain) == len(chains), 'matching bounds')


def census(repo):
    # Pairwise-era PR968 model bytes; production verify.py ships the neighborhood enumerator.
    source = module(repo / 'research/frame-pair-enumeration-production/baseline.py', 'pr968')
    require(source.f2_rank(source.NROW) == 9, 'label pairing rank')
    frames = source.frames_in(range(120))
    f0 = tuple(source.FRAME0)
    disjoint = [frame for frame in frames if not set(frame) & set(f0)]
    require(len(frames) == 2025 and len(disjoint) == 1260, 'frame census')
    index = {tuple(row): i for i, row in enumerate(source.LINES)}
    index.update({tuple(-x for x in row): i for i, row in enumerate(source.LINES)})
    reflections = []
    for alpha in source.SIMPLE:
        permutation = []
        for row in source.LINES:
            ip = sum(x * y for x, y in zip(row, alpha)) // 4
            permutation.append(index[tuple(x - ip * y for x, y in zip(row, alpha))])
        require(len(set(permutation)) == 120, 'reflection permutation')
        require(all(abs(source.IP[permutation[i]][permutation[j]]) == abs(source.IP[i][j])
                    for i in range(120) for j in range(120)), 'reflection form')
        reflections.append(permutation)
    orbit = {tuple(sorted(f0))}
    queue = list(orbit)
    while queue:
        frame = queue.pop()
        for reflection in reflections:
            image = tuple(sorted(reflection[i] for i in frame))
            if image not in orbit:
                orbit.add(image)
                queue.append(image)
    require(orbit == set(frames), 'all frame orbit')
    signatures = Counter()
    solutions = Counter()
    for f1 in disjoint:
        pairs_list = source.frame_pair_solutions(f0, f1)
        solutions[len(pairs_list)] += 1
        live = [i for i in range(120) if i not in f0 and i not in f1]
        for pairs in pairs_list:
            require(len(pairs) == 8, 'term count')
            require(all((source.IP[a][b] in (-1, 1)) if k == j else source.IP[a][b] == 0
                        for k, (a, _) in enumerate(pairs)
                        for j, (_, b) in enumerate(pairs)), 'dual root bases')
            require(source.f2_rank([source.NROW[a] for a, _ in pairs]) == 8,
                    'independent survivor labels')
            for a, b in pairs:
                readers = [i for i in live if source.IP[i][a]]
                sources = [i for i in live if source.IP[i][b]]
                require(source.span_dim(readers) == source.span_dim(sources) == 8,
                        'support hyperplanes')
                require(source.pair_rank(readers, sources) == 7, 'copy rank')
                require(all(((source.IP[t][a] + 1) & 1) == 0 for t in readers),
                        'reader survivor incidence')
            supports = tuple(sorted(sum(1 << k for k, (a, _) in enumerate(pairs)
                                        if source.IP[t][a]) for t in live))
            require(len(set(supports)) == 104, 'distinct target supports')
            signatures[supports] += 1
    require(solutions == Counter({8: 896, 0: 364}), 'admissible frame census')
    require(sum(signatures.values()) == 7168, 'decoder census')
    for supports in signatures:
        cube_chart(supports)
    return dict(frames=2025, frame_orbit=2025, disjoint_frames=1260,
                admissible_frames=896, decoders=7168, ordered_support_families=len(signatures),
                family_multiplicities={str(k): v for k, v in sorted(Counter(signatures.values()).items())})


def price_case(repo, selected, assembly, replicas):
    folder = repo / 'research/complex-k492-owner-repair/vendor/multicold/engines'
    first = module(folder / 'moment.py', 'mercator')
    second = module(folder / 'base_two_moment.py', 'atanh')
    baseline = Counter({int(k): v for k, v in assembly['complex_profile'].items()})
    b = Q(assembly['complex_lower'])
    m, calls, width = 73, 9 * replicas, 896 * replicas
    require(m * width - sum(r * n for r, n in baseline.items()) == 320 * replicas,
            'selected deficit')
    gate = Q(first.certify(baseline, m, width, False)['lower'])
    require(gate == b, 'selected exponent')
    profile = baseline.copy()
    profile[8] -= 8 * calls
    profile[7] += 8 * calls
    for rank in (1, 1, 1, 5, 1, 1, 4, 1, 1):
        profile[rank] -= 8 * calls
    profile[48] -= 8 * 9 * replicas
    profile = Counter({r: n for r, n in profile.items() if n})
    width -= 8 * replicas * 8
    require(all(n > 0 for n in profile.values()), 'P104 profile counts')
    require(m * width - sum(r * n for r, n in profile.items()) == 328 * replicas,
            'P104 deficit')
    intervals = [first.moment(profile, m, width, b, False),
                 second.moment(m, width, sorted(profile.items()), b)]
    require(max(x[0] for x in intervals) <= min(x[1] for x in intervals),
            'independent moment overlap')
    screen = {}
    for added_mass in (0, 1, 2):
        rows = [[lo + Q(added_mass * calls, m * width) - 1,
                 hi + Q(added_mass * calls, m * width) - 1] for lo, hi in intervals]
        require(all(hi < 0 for lo, hi in rows) if added_mass < 2
                else all(lo > 0 for lo, hi in rows), 'added mass screen')
        screen[str(added_mass)] = [[str(x) for x in row] for row in rows]
    changed = profile.copy()
    changed[1] += 2 * calls
    return dict(selected_b=str(b), selected_kappa=selected['kappa'],
                selected_bit_c=assembly['bit_lower'], m=m, replicas=replicas, calls=calls,
                baseline_W=896 * replicas, baseline_deficit=320 * replicas,
                P104_deficit=328 * replicas, P104_W=width, P104_profile={str(k): v for k, v in sorted(profile.items())},
                P104_b=str(Q(first.certify(profile, m, width, False)['lower'])),
                P104_plus_two_H1_b=str(Q(first.certify(changed, m, width, False)['lower'])),
                residual_intervals=screen,
                screen_contract='Keep the PR968 P104 profile. Add rank at price at least one per rank unit. No other savings are credited.')


def pricing(repo):
    selected = json.loads((HERE / 'inputs/selected942.json').read_text())
    assembly = json.loads((repo / selected['certificate']).read_text())
    latest = json.loads((HERE / 'inputs/selected1042.json').read_text())
    latest_bytes = (HERE / 'inputs/assembly1042.json').read_bytes()
    require(hashlib.sha256(latest_bytes).hexdigest() == latest['certificate_sha256'],
            'live selected assembly binding')
    return dict(base_T37=price_case(repo, selected, assembly, 37),
                refreshed_T16=price_case(repo, latest, json.loads(latest_bytes), 16))


def controls(supports, projections):
    import copy
    checks = []
    comparable = next(x for x in supports
                      if x not in projections['255']['antichain'] and
                      x & projections['255']['antichain'][1] in (x, projections['255']['antichain'][1]))
    for name, reason, change in (
        ('duplicate_antichain', 'antichain duplicate',
         lambda c: c['antichain'].__setitem__(0, c['antichain'][1])),
        ('missing_chain_member', 'chain cover', lambda c: c['chains'][0].pop()),
        ('comparable_antichain', 'antichain comparison',
         lambda c: c['antichain'].__setitem__(0, comparable)),
        ('false_width', 'matching bounds', lambda c: c.__setitem__('width', c['width'] - 1)),
    ):
        bad = copy.deepcopy(projections['255'])
        change(bad)
        try:
            check_poset_certificate(supports, bad)
        except ValueError as error:
            require(str(error) == reason, 'negative control reason: ' + name)
            checks.append(name)
        else:
            raise ValueError('negative control accepted: ' + name)
    broken = list(supports)
    broken[0] = 1
    try:
        cube_chart(broken)
    except ValueError as error:
        require(str(error) == 'cube degree', 'changed support control reason')
        checks.append('changed_target_support')
    else:
        raise ValueError('changed target support accepted')
    require(poset_certificate([1, 3, 7])['width'] == 1, 'chain positive control')
    require(poset_certificate([3, 5, 6])['width'] == 3, 'triangle positive control')
    return checks + ['chain_sharpness', 'triangle_sharpness']


def build(repo):
    check_sources(repo)
    geometry = census(repo)
    adjacency = [sum(1 << j for j in range(8) if (i ^ j).bit_count() == 1) for i in range(8)]
    supports = cube_family(adjacency)
    require(Counter(x.bit_count() for x in supports) == Counter({2: 12, 3: 24, 4: 32, 5: 24, 6: 12}),
            'cube support sizes')
    projections = {}
    for retained in [255] + [255 ^ (1 << k) for k in range(8)]:
        projected = {support & retained for support in supports} - {0}
        certificate = poset_certificate(projected)
        require(certificate['width'] == (32 if retained == 255 else 26), 'projection width')
        projections[str(retained)] = certificate
    return dict(schema='p104-asynchronous-carrier-bound/1', census=geometry,
                cube_supports=list(supports), projections=projections,
                price=pricing(repo), controls=controls(supports, projections))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=HERE.parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = build(args.repo.resolve())
    certificate = HERE / 'CERTIFICATE.json'
    if args.write:
        certificate.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(json.loads(certificate.read_text()) == result, 'committed certificate')
    print('PASS_P104_ASYNCHRONOUS_BOUND decoders=7168 cube_families=1 widths=32,26 controls=7 two_rank_budget=FAIL_T37_T16')


if __name__ == '__main__':
    main()

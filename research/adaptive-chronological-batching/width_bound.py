#!/usr/bin/env python3
"""Exact finite witnesses for WIDTH.md's symbolic adaptive width theorem.

Reuses this package's cut census; does not claim a second independent compiler.
The source profile and #4483 census comparisons are authenticated by verify.py.
Prepared for codyw912 with substantial OpenAI assistance; the integer level-run
proof was supplied by an independent Anthropic mathematical challenge.
Apache-2.0.
"""
from bisect import bisect_right
from collections import defaultdict
from math import lcm, prod
from pathlib import Path
import argparse
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import batching as B
import verify as V

require = B.require


def prime_support(generators):
    primes = set()
    for value in generators:
        p = 2
        while p * p <= value:
            while value % p == 0:
                primes.add(p)
                value //= p
            p += 1
        if value > 1:
            primes.add(value)
    return sorted(primes)


def semigroup(generators, cap):
    generators = sorted(set(k for k in generators if k > 1))
    seen, todo = {1}, [1]
    while todo:
        value = todo.pop()
        for k in generators:
            if k > cap // value:
                break
            following = value * k
            if following not in seen:
                seen.add(following)
                todo.append(following)
    return sorted(seen)


def signature(flow):
    histograms = ('roots', 'inner', 'sources', 'boundary', 'leaves', 'exits', 'columns')
    return (flow['height'], tuple(tuple(sorted(flow[k].items())) for k in histograms),
            tuple(flow['cuts']), flow['units'], flow['column_mass'], flow['matched'])


def level_limits(m, k0, M, g, maximum, cutoff):
    result = []
    for level in range(B.floor_log(maximum // m, M) + 1):
        low = max(cutoff, m * M ** level)
        high = min(maximum, m * M ** (level + 1) - 1)
        decrement = min(M ** level, k0 ** (g * level + 1))
        visits = 0 if low > high else 1 + (high - low) // decrement
        result.append({'level': level, 'low': low, 'high': high,
                       'decrement': decrement, 'visit_bound': visits})
    return result


def check_edges(flow, targets, paid, n, M, g):
    B.check_ledger(flow, targets, paid, n)
    k0, m = min(targets), max(targets)
    level = B.floor_log(n // m, M)
    require(flow['height'] == g * level, 'adaptive height at the exact cutoff')
    root_floor = k0 ** (g * level + 1)
    require(all(s >= root_floor for s in flow['roots']), 'root target-word lower bound')
    decrement = min(n // m, root_floor)
    rows = B.batch_rows(flow, n)
    require(all(0 <= j < n and n - j >= decrement for j, _ in rows),
            'every actual recursive edge has the integer decrement')
    W, P = sum(targets.values()), sum(paid.values())
    source_count = sum(flow['sources'].values())
    require(1 <= source_count <= W * (W + P) ** flow['height'],
            'positive source count and arbitrary-height demand-slot bound')
    return rows


def clear_source_caches(module):
    for method in (module.BaseFlow.column, module.BaseFlow.points,
                   module.BaseFlow.units, module.BaseFlow.demand):
        method.cache_clear()


def finite_case(name, targets, paid, M, g, maximum, source_module, cutoff=None):
    m, k0 = max(targets), min(targets)
    cutoff = m if cutoff is None else cutoff
    require(paid.get(1, 0) > 0 and maximum >= cutoff >= m, 'nonempty rule and ordinary base')
    cap = maximum // m
    generators = set(targets) | set(paid) | {M}
    primes = prime_support(generators)
    starts = semigroup(generators, cap)
    starts_set = set(starts)
    box = prod(1 + B.floor_log(cap, p) for p in primes)
    require(len(starts) <= box, 'prime-exponent box bounds plateau count')
    flows, counts = {}, {}
    previous = None
    changes = []
    for c in range(1, cap + 1):
        G = g * B.floor_log(c, M)
        flow = B.census(targets, paid, c, G)
        check_edges(flow, targets, paid, m * c, M, g)
        source = source_module.Flow(targets, paid, m * c, G).merged()
        V.same_as_source(flow, source)
        clear_source_caches(source_module)
        current = signature(flow)
        if current != previous:
            require(c in starts_set, 'every census change is a semigroup threshold')
            changes.append(c)
        flows[c] = flow
        if c in starts_set:
            counts[c] = sum(flow['sources'].values())
        plateau = starts[bisect_right(starts, c) - 1]
        require(counts[plateau] == sum(flow['sources'].values()), 'constant plateau source count')
        previous = current

    limits = level_limits(m, k0, M, g, maximum, cutoff)
    level_lcms = [1] * len(limits)
    level_counts = [0] * len(limits)
    for c in starts:
        level = B.floor_log(c, M)
        level_lcms[level] = lcm(level_lcms[level], counts[c])
        level_counts[level] += 1
    divisor = prod(value ** row['visit_bound'] for value, row in zip(level_lcms, limits))
    W, P = sum(targets.values()), sum(paid.values())
    ceil_log_W = (W - 1).bit_length()
    ceil_log_WP = (W + P - 1).bit_length()
    bit_bound = sum(row['visit_bound'] * level_counts[level]
                    * (ceil_log_W + g * level * ceil_log_WP)
                    for level, row in enumerate(limits))
    require(divisor <= 1 << bit_bound, 'exact integer bit envelope')

    widths = [1] * cutoff
    depths = [0] * cutoff
    visits = [{} for _ in range(cutoff)]
    maximum_visits = defaultdict(int)
    constraints = 0
    for n in range(cutoff, maximum + 1):
        flow = flows[n // m]
        rows = check_edges(flow, targets, paid, n, M, g)
        children = set(j for j, _ in rows)
        replication = B.multiplier(widths, rows)
        B.check_rows(widths, rows, replication)
        width = replication * sum(flow['sources'].values())
        require(divisor % width == 0, 'all-prime level-run divisor at every rank')
        widths.append(width)
        depth = 1 + max((depths[j] for j in children), default=0)
        require(depth <= sum(row['visit_bound'] for row in limits), 'chain-depth upper bound')
        depths.append(depth)
        level = B.floor_log(n // m, M)
        visit = {}
        for j in children:
            for ell, number in visits[j].items():
                visit[ell] = max(visit.get(ell, 0), number)
        visit[level] = visit.get(level, 0) + 1
        for ell, number in visit.items():
            require(number <= limits[ell]['visit_bound'], 'per-level chain visit bound')
            maximum_visits[ell] = max(maximum_visits[ell], number)
        visits.append(visit)
        constraints += len(rows)
    return {'name': name, 'targets': targets, 'paid': paid, 'M': M, 'g': g,
            'maximum': maximum, 'ordinary_cutoff': cutoff,
            'regime': 'quasipolynomial' if k0 ** g >= M else 'subexponential',
            'rank_and_height_primes': primes, 'plateaus': len(starts),
            'observed_census_changes': len(changes), 'prime_box': box,
            'constraints': constraints, 'maximum_chain_depth': max(depths),
            'levels': [{**row, 'observed_visits': maximum_visits[row['level']],
                        'plateaus': level_counts[row['level']]} for row in limits],
            'final_width': V.integer_record(widths[-1]),
            'divisor': V.integer_record(divisor), 'bit_envelope': bit_bound,
            'all_rank_integer_divisibility': True}


def profile_boundaries(sources, source_module):
    benchmarks = json.loads(V.authenticated('research/rank-convergence/BENCHMARKS.json', sources))
    expected = {'p7': (121, 5, 256, 2, 7688, 55998),
                'native4453': (153, 4, 1024, 2, 11560, 69273),
                'p16': (145, 4, 1024, 2, 10928, 64620)}
    reports = []
    for case in benchmarks['cases']:
        if case['name'] not in expected:
            continue
        raw = json.loads(V.authenticated(case['source'], sources))
        raw = raw[case['profile_key']] if case['profile_key'] else raw
        targets = {int(k): v for k, v in raw['targets'].items()}
        paid = {int(k): v for k, v in raw['paid'].items()}
        witness = case['witness']
        M, g = witness['height_base'], witness['a'] + witness['b']
        m, k0 = max(targets), min(targets)
        require((m, k0, M, g, sum(targets.values()), sum(paid.values())) == expected[case['name']],
                'source-bound profile and unchanged adaptive geometry')
        require(paid.get(1, 0) > 0, 'paid rank one supplies nonempty forests')
        if case['name'] != 'p7':
            require(M ** 2 == k0 ** (5 * g), 'exact three-fifths width exponent')
        rows = []
        for cap in sorted({1, 2, k0, M - 1, M, M + 1, 2 * M, M * M - 1, M * M}):
            G = g * B.floor_log(cap, M)
            flow = B.census(targets, paid, cap, G)
            source = source_module.Flow(targets, paid, m * cap, G).merged()
            V.same_as_source(flow, source)
            clear_source_caches(source_module)
            # Both ends of a floor(n/m) block matter; n=m*C alone is insufficient.
            constraints = sum(len(check_edges(flow, targets, paid, n, M, g))
                              for n in (m * cap, m * (cap + 1) - 1))
            if flow['roots']:
                require(min(flow['roots']) == k0 ** (G + 1), 'sharp root-word minimum')
            rows.append({'cap': cap, 'height': G, 'source_types': len(flow['sources']),
                         'sources': sum(flow['sources'].values()),
                         'root_minimum': min(flow['roots'], default=None),
                         'checked_batch_rows': constraints})
        reports.append({'profile': case['name'], 'M': M, 'g': g, 'k0': k0, 'm': m,
                        'exponent': '1-log_256(25)' if case['name'] == 'p7' else '3/5',
                        'boundary_probes': rows})
    require({row['profile'] for row in reports} == set(expected), 'all three pinned applications')
    return reports


def controls():
    targets, paid = {2: 1, 5: 1}, {1: 2, 4: 1}
    before = B.census(targets, paid, 3, 0)
    after = B.census(targets, paid, 3, 1)
    require(signature(before) != signature(after), 'height jump changes actual census')
    require(3 not in semigroup(set(targets) | set(paid), 3), 'omitted M loses a real threshold')
    flow = B.census(targets, paid, 10, 1)
    require(min(flow['roots']) == 4 and 5 * min(flow['roots']) <= 50,
            'adaptive root contradicts the default all-source contraction')
    return ['omitted_height_generator', 'false_default_root_contraction']


def run():
    sources = V.source_rows()
    source_module, _, _ = V.load_predecessors(sources)
    cases = [
        ('new-height-prime', {2: 1, 5: 1}, {1: 2, 4: 1}, 3, 1, 300, None),
        ('quasipolynomial-boundary', {2: 1, 5: 1}, {1: 2, 4: 1}, 4, 2, 300, None),
        ('empty-root-components', {2: 1, 5: 1}, {1: 2, 4: 1}, 2, 3, 150, None),
        ('collisions-and-larger-base', {2: 1, 4: 1, 8: 1}, {1: 1, 5: 1}, 7, 2, 300, 56),
    ]
    reports = [finite_case(*case[:-1], source_module, cutoff=case[-1]) for case in cases]
    return {'schema': 'adaptive-width-bound/v1', 'no_new_kappa': True,
            'claim': 'Symbolic all-rank theorem in WIDTH.md; finite integer witnesses here',
            'source_sha256': {p: r['sha256'] for p, r in sorted(sources.items())},
            'finite_compilations': reports,
            'profile_applications': profile_boundaries(sources, source_module),
            'boundary_controls': controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate this package receipt')
    args = parser.parse_args()
    result = run()
    path = HERE / 'WIDTH-RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(json.loads(path.read_text()) == json.loads(json.dumps(result)), 'width receipt equality')
    print('PASS_ADAPTIVE_WIDTH_BOUND', json.dumps({
        'compilations': len(result['finite_compilations']),
        'constraints': sum(row['constraints'] for row in result['finite_compilations']),
        'profiles': len(result['profile_applications']),
        'controls': len(result['boundary_controls']), 'no_new_kappa': True}, sort_keys=True))


if __name__ == '__main__':
    main()

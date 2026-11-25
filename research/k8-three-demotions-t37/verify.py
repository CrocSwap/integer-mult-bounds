#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the fixed R480 owner bound with exact rational arithmetic."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_contract():
    pins = read(HERE / 'SOURCES.json')
    for relative, expected in pins['files'].items():
        path = HERE / relative[8:] if relative.startswith('package:') else ROOT / relative
        need(digest(path) == expected, 'source drift: ' + relative)
    spec, plan = read(HERE / 'inputs/SPEC.json'), read(HERE / 'inputs/PLAN.json')
    provider = spec['providers']['gauge44']
    local = {int(r): n for r, n in provider['expected_profile'].items()}
    widths = {int(w): n for w, n in provider['inventory'].items()}
    registry = plan['provider_registry']['gauge44']
    need(Counter(registry['widths']) == widths, 'source width contract')
    need({int(r): n for r, n in registry['actual_paid_profile'].items()} == local,
         'source paid profile contract')
    T = plan['T']
    need(len(plan['order']) == 9*T and set(map(tuple, plan['order'])) ==
         set(itertools.product(range(9), range(T))), 'source call coverage')
    byrep = {r: Counter() for r in range(T)}
    for key, (capacity, times) in plan['windows'].items():
        replica, child = map(int, key.split(','))
        byrep[replica][capacity] += 112
    need(all(stock == byrep[0] for stock in byrep.values()), 'replica capacity contract')
    need(plan['M'] == 73 and plan['live'] == 896*T, 'source stock contract')
    engine = ROOT / pins['engine_directory']
    modules = [load(engine / (name + '.py'), 'r480_' + name)
               for name in ('moment', 'base_two_moment', 'outer')]
    driver = load(ROOT / pins['outer_driver'], 'r480_outer_driver')
    return local, widths, byrep[0], modules, driver, pins


def enumerate_bins(widths, prices, bonuses):
    upper, patterns = {}, []
    for capacity, bonus in sorted(bonuses.items()):
        for counts in itertools.product(*(range(capacity//w+1) for w in widths)):
            used = sum(w*n for w, n in zip(widths, counts))
            if used > capacity:
                continue
            residual = capacity - used
            value = bonus + sum(p*n for p, n in zip(prices, counts))
            upper[residual] = max(upper.get(residual, -10**9), value)
            patterns.append((capacity, counts, residual, value))
    # This recurrence uses ordered fills, without a count-vector product.
    second = {}
    for capacity, bonus in sorted(bonuses.items()):
        best = {0: 0}
        for used in range(capacity+1):
            if used not in best:
                continue
            for width, price in zip(widths, prices):
                if used+width <= capacity:
                    best[used+width] = max(best.get(used+width, -10**9), best[used]+price)
        for used, value in best.items():
            r = capacity-used
            second[r] = max(second.get(r, -10**9), bonus+value)
    need(upper == second, 'independent bin recurrence')
    return upper, patterns


def phi(engine, kind, rank, endpoint):
    if kind == 'mercator':
        a, b = engine.logarithm(Q(73, rank))
        lo, hi = engine.exponential(endpoint*a, endpoint*b)
    else:
        a, b = engine.log_bounds(Q(73, rank))
        lo, hi = engine.exp_bounds(endpoint*a)[0], engine.exp_bounds(endpoint*b)[1]
    return rank*lo, rank*hi


def supporting_certificate(engine, kind, upper, lower, higher):
    # Enclose all exponents in the root interval, not only one grid point.
    values = {r: (phi(engine, kind, r, lower)[0], phi(engine, kind, r, higher)[1])
              for r in upper if r}
    cost = {r: (48*lo-r*values[48][1], 48*hi-r*values[48][0])
            for r, (lo, hi) in values.items() if r < 48}
    credit = {r: 48*upper[r]-r*upper[48] for r in cost}
    need(credit[1] > 0 and cost[1][0] > 0, 'positive rank-one multiplier')
    margins = {}
    for rank, (lo, hi) in cost.items():
        if rank == 1:
            continue
        coefficient = credit[rank]
        rhs = coefficient*cost[1][1 if coefficient >= 0 else 0]/credit[1]
        margins[rank] = lo-rhs
        need(margins[rank] > 0, 'strict rank support: ' + str(rank))
    return {'multiplier_interval': [str(x/credit[1]) for x in cost[1]],
            'strict_margins': {r: str(x) for r, x in sorted(margins.items())},
            'minimum_strict_margin': str(min(margins.values()))}


def check(certificate):
    need(not sys.flags.optimize, 'Retained outer assertions require Python without -O')
    local, inventory, stock, (M, B, A), outer, pins = source_contract()
    widths = tuple(sorted(inventory))
    need(set(certificate['width_prices']) == set(map(str, widths)), 'width price keys')
    need(all(type(n) is int for n in certificate['width_prices'].values()), 'integer width prices')
    need(all(type(n) is int for n in certificate['capacity_bonuses'].values()), 'integer capacity bonuses')
    need(set(certificate['capacity_bonuses']) == set(map(str, stock)), 'capacity price keys')
    prices = tuple(certificate['width_prices'][str(w)] for w in widths)
    bonuses = {int(c): x for c, x in certificate['capacity_bonuses'].items()}
    need(set(bonuses) == set(stock), 'capacity price coverage')
    upper, patterns = enumerate_bins(widths, prices, bonuses)
    need(upper[0] == 0 and max(upper) == 48, 'zero and maximum residual')
    mass = sum(c*n for c, n in stock.items())-9*sum(w*n for w, n in inventory.items())
    signed = sum(stock[c]*bonuses[c] for c in stock)+9*sum(inventory[w]*p for w, p in zip(widths, prices))
    credit = 48*signed-upper[48]*mass
    unit = 48*upper[1]-upper[48]
    need(credit > 0 and unit > 0, 'positive credit demand')
    formal = {1: Q(credit, unit)}
    formal[48] = (mass-formal[1])/48
    T = certificate['replicas']
    need(type(T) is int and T > 0, 'positive integral replicas')
    need(all((n*T).denominator == 1 for n in formal.values()), 'integral residual counts')
    idle = Counter({r: int(n*T) for r, n in formal.items()})
    counts, bins, actual_idle = Counter(), Counter(), Counter()
    for row in certificate['packing']:
        capacity, vector, multiplicity = row['capacity'], row['width_counts'], row['bins']
        need(type(capacity) is int, 'integer packing capacity')
        need(type(multiplicity) is int and multiplicity > 0, 'positive packing multiplicity')
        need(len(vector) == len(widths) and all(type(n) is int and n >= 0 for n in vector),
             'integer packing vector')
        used = sum(w*n for w, n in zip(widths, vector))
        need(capacity in stock and used <= capacity, 'whole-helper capacity')
        bins[capacity] += multiplicity
        counts.update({w: multiplicity*n for w, n in zip(widths, vector)})
        if capacity > used:
            actual_idle[capacity-used] += multiplicity
    need(bins == Counter({c: n*T for c, n in stock.items()}), 'complete bin stock')
    need(counts == Counter({w: 9*T*n for w, n in inventory.items()}), 'complete helper inventory')
    need(actual_idle == idle, 'attaining residual profile')
    profile = Counter({r: 9*T*n for r, n in local.items()})
    profile.update(idle)
    live = 896*T
    need(73*live-sum(r*n for r, n in profile.items()) == 320*T, 'complete rank deficit')
    need(73**2 > 2*max(profile)**2, 'proper-child halving guard')
    need(len(certificate['root_interval']) == 2 and all(type(x) is str for x in certificate['root_interval']), 'rational root strings')
    need(type(certificate['kappa_grid']) is str, 'rational kappa string')
    lower, higher = map(Q, certificate['root_interval'])
    need(higher-lower == Q(1, 10**24), 'root interval width')
    signs = {}
    for name, endpoint in [('lower', lower), ('upper', higher)]:
        first, second = M.moment(profile, 73, live, endpoint), B.moment(73, live, list(profile.items()), endpoint)
        need((first[1] < 1 and second[1] < 1) if name == 'lower' else
             (first[0] > 1 and second[0] > 1), 'two exact root signs: ' + name)
        signs[name] = {'mercator': [str(x-1) for x in first],
                       'atanh': [str(x-1) for x in second]}
    supports = {kind: supporting_certificate(engine, kind, upper, lower, higher)
                for kind, engine in [('mercator', M), ('atanh', B)]}
    result1074 = read(HERE / 'inputs/RESULT.json')
    bit_record = read(ROOT / pins['bit_expected'])
    bit = bit_record['nine']
    c = Q(bit['bit_lower'])
    need(c == Q(result1074['bit_lower']), 'unchanged bit endpoint')
    bit_histogram = {int(r): n for r, n in bit['profile'].items()}
    bit_deficit = outer.pr589_deficit(bit_record['word'], bit['bit']['live'])
    bit_checks = outer.moment_checks(M, B, bit_histogram, 64, bit['bit']['live'], c, bit_deficit, True)
    prices = {key: outer.outer47(c, b, A) for key, b in [('lower', lower), ('upper', higher)]}
    need(all(Q(p['kappa']) == Q(certificate['kappa_grid']) for p in prices.values()), 'same outer grid cell')
    minT = 1
    import math
    for n in formal.values():
        minT = math.lcm(minT, n.denominator)
    return {'status': 'PASS_R480_ALL_REPLICA_BIN_OPTIMUM',
            'scope': 'Exact owner bin relaxation. Time windows, per-call family matching, charts, local admission and finite invoices are separate.',
            'base': pins['base'], 'source_head': pins['source_head'],
            'inventory': inventory, 'local_profile': local, 'capacity_stock': stock,
            'bin_patterns': len(patterns), 'upper_price_by_residual': upper,
            'idle_mass_per_replica': mass, 'signed_price_per_replica': signed,
            'credit_per_replica': credit, 'rank_one_credit': unit,
            'normalized_idle': {r: str(n) for r, n in formal.items()},
            'minimum_equality_replicas': minT, 'packing_replicas': T,
            'packing_idle': dict(sorted(idle.items())), 'profile': dict(sorted(profile.items())),
            'live': live, 'deficit': 320*T, 'root_interval': [str(lower), str(higher)],
            'two_engine_signs': signs, 'support_over_root_interval': supports,
            'bit_moments_with_surcharge': bit_checks, 'outer': prices, 'kappa_grid_ceiling': certificate['kappa_grid'],
            'headroom_over_pr1074': str(Q(certificate['kappa_grid'])-Q(result1074['kappa'])),
            'source_sha256': pins['files']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    need(not args.out.exists(), 'Choose a new output file')
    result = check(read(args.certificate))
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'patterns='+str(result['bin_patterns']),
          'kappa_grid_ceiling='+str(Q(result['kappa_grid_ceiling'])))


if __name__ == '__main__':
    main()

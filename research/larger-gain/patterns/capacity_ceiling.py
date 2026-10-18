#!/usr/bin/env python3
"""Pattern-level optimistic ceiling; source-bound, exact dual verification.

SciPy nominates a dual. --verify checks the receipt using only Python's stdlib
and both unchanged rational moment engines. Whole-call windows and integral
provider/pattern multiplicities are relaxed, so this is an upper bound, never
an admitted construction. Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(os.environ.get('GAIN_PR564_SOURCE', ROOT / 'research/complex-allcold')).resolve()


def load_engine(name):
    spec = importlib.util.spec_from_file_location(name, SOURCE / 'engines' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def instance(extra, extra_scope='all', extra_providers=()):
    plan_path = SOURCE / 'data/PLAN.json'
    plan = json.loads(plan_path.read_text())
    capacities = Counter(v[0] for v in plan['windows'].values())
    capacities = {r: 112 * n for r, n in sorted(capacities.items())}
    providers = []
    for name, desc in sorted(plan['provider_registry'].items()):
        applied = extra if extra_scope == 'all' or name == 'rank5_eight_cold' else 0
        inventory = Counter(desc['widths'])
        inventory[8] += applied
        inventory[9] -= applied
        profile = {int(r): n for r, n in desc['actual_paid_profile'].items()}
        profile[1] += applied
        profile[2] += 2 * applied
        profile[3] -= 2 * applied
        providers.append(dict(kind='provider', provider=name, profile=profile, widths=dict(inventory)))
    for source in extra_providers:
        path = ROOT / source['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
        construction = json.loads(path.read_text())
        profile = {int(r): n for r, n in construction['profile_after'].items()}
        inventory = {int(r): n for r, n in construction['widths_after'].items()}
        assert sum(inventory.values()) == 504
        assert all(0 < r < 73 and type(n) is int and n >= 0 for r, n in profile.items())
        assert all(0 < r <= 9 and type(n) is int and n >= 0 for r, n in inventory.items())
        providers.append(dict(kind='provider', provider=source['path'], profile=profile, widths=inventory))
    widths = sorted({r for provider in providers for r in provider['widths']})
    columns = []
    descriptors = []
    for cap in capacities:
        def enumerate_patterns(index, remaining, counts):
            if index == len(widths):
                vector = [int(r == cap) for r in capacities] + counts + [0]
                columns.append(vector)
                descriptors.append(dict(kind='bin', capacity=cap, counts=counts, remainder=remaining))
                return
            width = widths[index]
            for n in range(remaining // width + 1):
                enumerate_patterns(index + 1, remaining - n * width, counts + [n])
        enumerate_patterns(0, cap, [])
    for provider in providers:
        columns.append([0] * len(capacities) + [-provider['widths'].get(r, 0) for r in widths] + [1])
        descriptors.append(provider)
    gaps = {sum(r * n for r, n in d['profile'].items()) - sum(r * n for r, n in d['widths'].items())
            for d in descriptors if d['kind'] == 'provider'}
    assert len(gaps) == 1
    assert sum(r * n for r, n in capacities.items()) + 72 * gaps.pop() == 520704
    rhs = list(capacities.values()) + [0] * len(widths) + [72]
    return columns, rhs, descriptors, hashlib.sha256(plan_path.read_bytes()).hexdigest()


def exact_costs(descriptors, rate, engine):
    ranks = sorted({d['remainder'] for d in descriptors if d['kind'] == 'bin'} |
                   {int(r) for d in descriptors if d['kind'] == 'provider' for r in d['profile']})
    result = {0: Q(0)}
    for rank in ranks:
        if rank == 0:
            continue
        if hasattr(engine, 'logarithm'):
            lower, upper = engine.logarithm(Q(73, rank))
            exp_lower = engine.exponential(rate * lower, rate * upper)[0]
        else:
            lower, _ = engine.log_bounds(Q(73, rank))
            exp_lower = engine.exp_bounds(rate * lower)[0]
        result[rank] = rank * (exp_lower - 1) / rate
    return [result[d['remainder']] if d['kind'] == 'bin' else
            sum(n * result[int(r)] for r, n in d['profile'].items()) for d in descriptors]


def verify(receipt):
    assert type(receipt['extra_rank_one_cold_relations']) is int
    assert 0 <= receipt['extra_rank_one_cold_relations'] <= 100
    assert receipt.get('extra_provider_scope', 'all') in ('all', 'eight')
    columns, rhs, descriptors, source_sha = instance(receipt['extra_rank_one_cold_relations'],
                                                    receipt.get('extra_provider_scope', 'all'),
                                                    receipt.get('extra_providers', ()))
    assert source_sha == receipt['source_plan_sha256']
    assert len(columns) == receipt['pattern_and_provider_columns']
    rate = Q(receipt['rejected_rate'])
    assert rate > 0
    assert Q(receipt['kappa_upper_bound']) == rate / (1 + rate)
    y = list(map(Q, receipt['dual']))
    assert len(y) == len(rhs)
    for name in ('moment', 'base_two_moment'):
        costs = exact_costs(descriptors, rate, load_engine(name))
        for column, cost in zip(columns, costs):
            assert sum(a * b for a, b in zip(column, y)) <= cost
    value = sum(a * b for a, b in zip(rhs, y))
    assert rate * value > 2560
    assert str(rate * value - 2560) == receipt['strict_rejection_margin']
    return dict(status='PASS_EXACT_CAPACITY_PATTERN_UPPER_BOUND', columns=len(columns),
                dual_objective=str(value), strict_rejection_margin=str(rate * value - 2560))


def solve_rational(matrix, rhs):
    rows = [list(map(Q, row)) + [Q(value)] for row, value in zip(matrix, rhs)]
    n = len(rhs)
    assert len(rows) == n and all(len(row) == n + 1 for row in rows)
    for col in range(n):
        pivot = next(i for i in range(col, n) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [x / divisor for x in rows[col]]
        for i in range(n):
            if i != col and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[col])]
    return [row[-1] for row in rows]


def nominate(extra, extra_scope, extra_providers=()):
    import math
    import numpy as np
    import scipy
    from scipy.optimize import linprog
    columns, rhs, descriptors, source_sha = instance(extra, extra_scope, extra_providers)
    matrix = np.array(columns, dtype=float).T
    def solve(rate):
        cost = lambda rank: rank * math.expm1(rate * math.log(73 / rank)) / rate if rank else 0
        costs = [cost(d['remainder']) if d['kind'] == 'bin' else
                 sum(n * cost(r) for r, n in d['profile'].items()) for d in descriptors]
        solution = linprog(costs, A_eq=matrix, b_eq=rhs, bounds=(0, None), method='highs')
        assert solution.success, solution.message
        return solution
    lo, hi = .0015, .003
    for _ in range(45):
        mid = (lo + hi) / 2
        solution = solve(mid)
        if mid * solution.fun < 2560:
            lo = mid
        else:
            hi = mid
    solution = solve(hi)
    active = [i for i, x in enumerate(solution.x) if x > 1e-7]
    assert len(active) == len(rhs), 'Expected a nonsingular basic nominee'
    primal = solve_rational([[columns[i][row] for i in active] for row in range(len(rhs))], rhs)
    assert all(x >= 0 for x in primal)
    histogram = Counter()
    for index, multiplicity in zip(active, primal):
        d = descriptors[index]
        if d['kind'] == 'bin' and d['remainder']:
            histogram[d['remainder']] += multiplicity
        elif d['kind'] == 'provider':
            for r, n in d['profile'].items():
                histogram[r] += multiplicity * n
    denominator = math.lcm(*(n.denominator for n in histogram.values()))
    integer_histogram = {r: int(n * denominator) for r, n in histogram.items()}
    assert sum(r * n for r, n in integer_histogram.items()) == 520704 * denominator
    root = load_engine('moment').certify(integer_histogram, 73, 7168 * denominator)
    rate = Q(root['upper'])
    costs_a = exact_costs(descriptors, rate, load_engine('moment'))
    costs_b = exact_costs(descriptors, rate, load_engine('base_two_moment'))
    costs = list(map(min, zip(costs_a, costs_b)))
    y = solve_rational([columns[i] for i in active], [costs[i] for i in active])
    def violation(index):
        return sum(a * b for a, b in zip(columns[index], y)) - costs[index]
    # Each bin column contains exactly one capacity coefficient. Correct its
    # dual potential downward. Provider columns have no capacity coefficient.
    for row, cap in enumerate(sorted({d['capacity'] for d in descriptors if d['kind'] == 'bin'})):
        bad = max([Q(0)] + [violation(i) for i, d in enumerate(descriptors)
                           if d['kind'] == 'bin' and d['capacity'] == cap])
        y[row] -= bad + Q(1, 10**70)
    bad = max([Q(0)] + [violation(i) for i, d in enumerate(descriptors) if d['kind'] == 'provider'])
    y[-1] -= bad + Q(1, 10**70)
    value = sum(a * b for a, b in zip(rhs, y))
    receipt = dict(
        status='EXACT_DUAL_PENDING_SELF_CHECK', source_plan_sha256=source_sha,
        extra_rank_one_cold_relations=extra, pattern_and_provider_columns=len(columns),
        extra_provider_scope=extra_scope,
        extra_providers=list(extra_providers),
        rejected_rate=str(rate), kappa_upper_bound=str(rate / (1 + rate)),
        approximate_relaxed_root=(lo + hi) / 2,
        approximate_kappa_ceiling=hi / (1 + hi), dual=list(map(str, y)),
        exact_relaxed_primal=[dict(column=i, multiplicity=str(n)) for i, n in zip(active, primal)],
        relaxed_profile={str(r): str(n) for r, n in sorted(histogram.items())},
        relaxed_profile_root=root,
        strict_rejection_margin=str(rate * value - 2560),
        optimizer=dict(name='scipy.optimize.linprog/highs', version=scipy.__version__, role='nomination only'),
        active_patterns=[dict(descriptor=d, multiplicity=float(n))
                         for d, n in zip(descriptors, solution.x) if n > 1e-7],
        scope='Optimistic fractional capacity packing with complete paid local profiles and literal '
              'bin patterns on the supplied width alphabet, capacities8/16/32/48 and72 provider calls. '
              'Ignores actual windows, owner uniqueness and integer multiplicities. Extra cold '
              'relations, when nonzero, are a hypothetical repeated local delta, not provider admission. '
              'Dual feasibility and rejected-rate sign are verified with both rational engines.')
    receipt['verification'] = verify(receipt)
    receipt['status'] = receipt['verification']['status']
    return receipt


if __name__ == '__main__':
    if sys.flags.optimize:
        raise SystemExit('Assertions required')
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--extra-cold', type=int, default=0)
    parser.add_argument('--extra-scope', choices=('all', 'eight'), default='all')
    parser.add_argument('--provider-construction', type=Path, action='append', default=[])
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.verify:
        result = verify(json.loads(args.verify.read_text()))
        print(json.dumps({k: result[k] for k in ('status', 'columns')}))
    else:
        assert args.out and not args.out.exists() and 0 <= args.extra_cold <= 100
        extra_providers = [dict(path=str(path.resolve().relative_to(ROOT)),
                                sha256=hashlib.sha256(path.read_bytes()).hexdigest())
                           for path in args.provider_construction]
        answer = nominate(args.extra_cold, args.extra_scope, extra_providers)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(answer, indent=2) + '\n')
        print(json.dumps({k: answer[k] for k in ('status', 'approximate_kappa_ceiling', 'rejected_rate')}))

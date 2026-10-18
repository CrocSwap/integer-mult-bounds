#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact partial-width bit slot optimum; no physical supplier admission."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIMIT = Q(1, 100)
CAPS = {7: 666, 14: 444, 28: 444, 42: 444}
PART = {0: None, 1: (14, 1), 2: (28, 2), 3: (28, 3), 4: (42, 4)}
PATTERNS = [(c, u) for c in CAPS for u in range(1, c // 8 + 1)]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, indent=2) + '\n'


def clean(x):
    return {r: n for r, n in sorted(x.items()) if n}


def pins():
    s = json.loads((HERE / 'SOURCES.json').read_text())
    for row in s['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'source pin: ' + row['path'])
    return s


def engine(name):
    path = ROOT / 'research/native-complex-moment552/engines' / (name + '.py')
    spec = importlib.util.spec_from_file_location('partial_' + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def context():
    record = json.loads((ROOT / 'research/e8-bit-p111-tuned/tune/EXPECTED.json').read_text())
    selection = json.loads((ROOT / 'research/e8-bit-p111-tuned/data/selection9-p111.json').read_text())
    prior = json.loads((ROOT / 'research/bit589-width-packing/RESULT.json').read_text())
    require(record['word']['R'] == 439 and record['word']['v'] == 111, 'wrong supplier')
    require(record['nine']['bit']['live'] == 28416, 'live width')
    caps = {int(k): v for k, v in prior['slot_model']['capacity_by_slot_index'].items()}
    counts, hosted, rem = Counter(), Counter(), Counter()
    for index, widths, n in selection['bit']['patterns']:
        require(all(w == 8 for w in widths), 'baseline widths')
        c = caps[index]
        require(8 * len(widths) < c, 'positive baseline remainder')
        counts[c] += n
        hosted[index] += 8 * len(widths) * n
        rem[c - 8 * len(widths)] += n
    staged = Counter()
    for index, width, stage, count in selection['bit']['stages']:
        staged[index] += width * count
    require(hosted == staged, 'selection stage accounting')
    require(dict(counts) == CAPS, 'slot multiplicities')
    require(sum(hosted.values()) == 8 * 9 * 439, 'all baseline roles')
    local = {int(r): n for r, n in record['word']['local_histogram'].items()}
    global_h = Counter({r: 288 * n for r, n in local.items()})
    global_h.update({r: 32 * n for r, n in rem.items()})
    require(clean(global_h) == {int(r): n for r, n in record['nine']['profile'].items()}, 'global profile reconstruction')
    require(sum(c * n for c, n in CAPS.items()) == 41958, 'slot capacity')
    return record, prior, local


def delta(c, u):
    out = Counter({c % 8 + 8 * u: 1})
    out[c % 8] -= 1
    return clean(out)


def policy(s):
    require(s >= 0, 'negative slack')
    q, r = divmod(s, 5)
    out = Counter({42: q, 2: -q})
    if PART[r] is not None:
        out.update(delta(*PART[r]))
    return clean(out)


def bellman_difference(s, c, u, candidate=policy):
    out = Counter(candidate(s - u))
    out.update(delta(c, u))
    out.subtract(candidate(s))
    return clean(out)


def analytic_positive(coeff, moment):
    """Lower-bound f(a)/a throughout 0<a<=LIMIT by Taylor remainder."""
    require(sum(r * n for r, n in coeff.items()) == 0, 'linear mass cancellation')
    d_lo = Q(0)
    remainder = Q(0)
    for r, n in coeff.items():
        l, h = moment.logarithm(Q(64, r))
        d_lo += n * r * (l if n > 0 else h)
        exp_hi = moment.exponential(LIMIT * l, LIMIT * h)[1]
        remainder += abs(n) * r * LIMIT * h * h * exp_hi / 2
    bound = d_lo - remainder
    require(bound > 0, 'uniform analytic inequality')
    return {'coefficients': {str(r): n for r, n in coeff.items()},
            'slope_lower': str(d_lo), 'remainder_upper': str(remainder), 'positive_margin_lower': str(bound)}


def certify_policy(moment):
    distinct, zeros = {}, 0
    for s in range(5, 10):
        for c, u in PATTERNS:
            coeff = bellman_difference(s, c, u)
            if not coeff:
                zeros += 1
                continue
            key = tuple(coeff.items())
            if key not in distinct:
                distinct[key] = analytic_positive(coeff, moment)
    require(zeros == 9 and len(distinct) == 30, 'complete Bellman coverage')
    # Residue reduction checked directly on every finite state used in the theorem.
    for s in list(range(1, 712)) + [32 * (45 + 9 * k) for k in range(75)]:
        for c, u in PATTERNS:
            if u <= s:
                same = bellman_difference(5 + s % 5, c, u)
                require(bellman_difference(s, c, u) == same, 'Bellman residue reduction')
    return {'residues': 5, 'moves': len(PATTERNS), 'exact_ties': zeros,
            'strict_inequalities': list(distinct.values()), 'range': '0 < a <= 1/100'}


def placement(k, old=False, replicas=1):
    require(0 <= k <= 74, 'conversion range')
    require(replicas in (1, 32), 'replica domain')
    q, r = divmod(replicas * (45 + 9 * k), 5)
    # Pattern keys: capacity, number of width7 roles, number of width8 roles.
    out = Counter({(7, 1, 0): replicas * 9 * k, (7, 0, 0): replicas * (666 - 9 * k),
                   (14, 0, 1): 444 * replicas, (28, 0, 3): 444 * replicas,
                   (42, 0, 5): 444 * replicas - q, (42, 0, 0): q})
    if r:
        c, u = (42, r) if old else PART[r]
        out[c, 0, c // 8] -= 1
        out[c, 0, c // 8 - u] += 1
    return {p: n for p, n in sorted(out.items()) if n}


def inspect_placement(p, k, replicas=1):
    capacities, idle = Counter(), Counter()
    seven = eight = 0
    for (c, a, b), n in p.items():
        require(n > 0 and a >= 0 and b >= 0, 'nonnegative placement counts')
        r = c - 7 * a - 8 * b
        require(r >= 0, 'slot capacity exceeded')
        capacities[c] += n
        seven += n * a
        eight += n * b
        if r:
            idle[r] += n
    require(dict(capacities) == {c: replicas * n for c, n in CAPS.items()}, 'slot multiplicities')
    require(seven == replicas * 9 * k and eight == replicas * 9 * (439 - k), 'helper inventory')
    require(sum(r * n for r, n in idle.items()) == replicas * (41958 - 8 * 3951 + 9 * k), 'idle rank mass')
    require(sum(idle.values()) == replicas * (1998 - 9 * k), 'idle child count')
    return clean(idle)


def trim(local, k, optimistic):
    out = Counter(local)
    if optimistic:
        require(out[1] >= k, 'rank-one supply')
        out[1] -= k
    else:
        left = k
        for r in sorted(local, reverse=True):
            take = min(left, local[r])
            out[r] -= take
            if r > 1:
                out[r - 1] += take
            left -= take
        require(left == 0, 'distinct local children')
    return clean(out)


def histogram(local, k, optimistic, old=False, pooled=False):
    out = Counter({r: 288 * n for r, n in trim(local, k, optimistic).items()})
    replicas = 32 if pooled else 1
    idle = inspect_placement(placement(k, old, replicas), k, replicas)
    out.update({r: (32 // replicas) * n for r, n in idle.items()})
    require(sum(r * n for r, n in out.items()) == 64 * 28416 - 10272, 'complete mass conservation')
    return clean(out)


def endpoints(h, moment, base_two):
    a = Q(moment.certify(h, 64, 28416, True)['lower'])
    require(0 < a < LIMIT, 'endpoint lies within proved range')
    margins = []
    for z, lower in ((a, True), (a + Q(1, 10**24), False)):
        lo, hi = moment.moment(h, 64, 28416, z, True)
        lo2, hi2 = base_two.moment(64, 28416, list(h.items()), z)
        f0, f1 = base_two.moment(64, 28416, [(1, 32 * 64 * 64 * sum(h.values()))], z)
        lo2 += f0 / 10**16
        hi2 += f1 / 10**16
        require(max(hi, hi2) < 1 if lower else min(lo, lo2) > 1, 'both engines with bad-residue surcharge')
        margins.append(str(1 - max(hi, hi2) if lower else min(lo, lo2) - 1))
    return {'lower': str(a), 'upper': str(a + Q(1, 10**24)), 'two_engine_strict_margins': margins}


def controls(moment):
    passed = []
    def rejected(name, fn, reason):
        try:
            fn()
        except ValueError as exc:
            require(reason in str(exc), name + ': wrong failure')
            passed.append(name)
            return
        raise ValueError(name + ': control accepted')
    p = placement(2)
    # Drop one hosted width8 role; capacity and inventory contracts detect it.
    bad = dict(p); bad[42, 0, 5] -= 1; bad[42, 0, 4] = 1
    rejected('omitted_width8_role', lambda: inspect_placement(bad, 2), 'helper inventory')
    bad = dict(p); bad[7, 1, 0] += 1
    rejected('extra_capacity7_slot', lambda: inspect_placement(bad, 2), 'slot multiplicities')
    rejected('conversion75', lambda: placement(75), 'conversion range')
    rejected('negative_slack', lambda: policy(-1), 'negative slack')
    rejected('wrong_linear_mass', lambda: analytic_positive({14: 1, 6: -1}, moment), 'linear mass')
    # The predecessor's partial-capacity42 policy is a feasible positive control,
    # but its optimality claim would fail already at s=1 (14 beats 10+6-2).
    coeff = {14: 1, 6: -1, 10: -1, 2: 1}
    rejected('old_policy_false_optimum', lambda: analytic_positive(coeff, moment), 'uniform analytic')
    return passed


def run():
    pins()
    record, prior, local = context()
    moment, base_two = engine('moment'), engine('base_two_moment')
    # Pure memoization of an unchanged exact function; no altered coverage.
    base_two.log_bounds = lru_cache(None)(base_two.log_bounds)
    cert = certify_policy(moment)
    cases, improved, pooling_improved = [], [], []
    for k in range(75):
        p = placement(k)
        idle = inspect_placement(p, k)
        old = inspect_placement(placement(k, True), k)
        require(sum(idle.values()) == sum(old.values()), 'same surcharge child count')
        coeff = Counter(old); coeff.subtract(idle); coeff = clean(coeff)
        if coeff:
            analytic_positive(coeff, moment)
            improved.append(k)
        pool_p = placement(k, replicas=32)
        pool_idle = inspect_placement(pool_p, k, replicas=32)
        pool_diff = Counter({r: 32 * n for r, n in idle.items()})
        pool_diff.subtract(pool_idle)
        if clean(pool_diff):
            analytic_positive(clean(pool_diff), moment)
            pooling_improved.append(k)
        cases.append({'k': k, 'pooled32_idle': {str(r): n for r, n in pool_idle.items()},
                      'pooled32_placement': [{'capacity': c, 'width7': a, 'width8': b, 'count': n}
                                             for (c, a, b), n in pool_p.items()],
                      'slack': 45 + 9 * k, 'idle': {str(r): n for r, n in idle.items()},
                      'strictly_beats_prior': bool(coeff),
                      'placement': [{'capacity': c, 'width7': a, 'width8': b, 'count': n}
                                    for (c, a, b), n in p.items()]})
    require(len(improved) == 45, 'improvement count')
    require(len(pooling_improved) == 60, 'pooling improvement count')
    # Price the two published partial rows which change, plus minimal k=2.
    prices = {}
    for k in (0, 1, 2, 37, 74):
        for optimistic in (True, False):
            if k == 0 and not optimistic:
                continue
            name = ('optimistic' if optimistic else 'pessimistic')
            h = histogram(local, k, optimistic)
            row = {'histogram': {str(r): n for r, n in h.items()},
                   'optimal': endpoints(h, moment, base_two)}
            old_h = histogram(local, k, optimistic, True)
            row['prior'] = row['optimal'] if old_h == h else endpoints(old_h, moment, base_two)
            pool_h = histogram(local, k, optimistic, pooled=True)
            row['pooled32_histogram'] = {str(r): n for r, n in pool_h.items()}
            row['pooled32'] = row['optimal'] if pool_h == h else endpoints(pool_h, moment, base_two)
            require(Q(row['pooled32']['lower']) >= Q(row['optimal']['lower']), 'pooling does not worsen')
            if k in (1, 37, 74):
                inherited = prior['scenarios'][f'width7_k{k}_{name}']
                require(Q(row['prior']['lower']) == Q(inherited['bit_lower']), 'published prior endpoint')
            if k == 0:
                require(Q(row['optimal']['lower']) == Q(record['nine']['bit_lower']), 'selected positive control')
            else:
                require(Q(row['optimal']['lower']) >= Q(row['prior']['lower']), 'endpoint does not worsen')
            prices[f'k{k}_{name}'] = row
    return {'status': 'PASS_BIT_PARTIAL_WIDTH7_OPTIMUM', 'assignment_seed': 3,
            'scope': 'slot relaxation only; no timing admission or new kappa',
            'bellman': cert, 'improved_k': improved, 'pooling_improved_k': pooling_improved, 'cases': cases,
            'priced_cases': prices, 'controls': controls(moment)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', type=Path, help='write fresh evidence, refusing overwrite')
    args = ap.parse_args()
    result = run()
    if args.write:
        with args.write.open('x') as f:
            f.write(canonical(result))
    else:
        require(result == json.loads((HERE / 'EXPECTED.json').read_text()), 'committed evidence mismatch')
    print('PASS_BIT_PARTIAL_WIDTH7_OPTIMUM k=0..74 local_improved=45 pooled_improved=60 bellman=45 controls=6 no_new_kappa')


if __name__ == '__main__':
    main()

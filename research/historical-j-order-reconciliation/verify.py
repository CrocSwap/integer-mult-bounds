#!/usr/bin/env python3
"""Reconcile the archived campaign's J/root order, using exact integer intervals.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
No historical evaluator is imported; physical admissibility is outside scope.
"""
from collections import defaultdict
from decimal import Decimal
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
SCALE = 1 << 192
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19)
ROOT_GRID = 10**14
KAPPA_GRID = 10**18


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ceil_div(n, d):
    return -((-n) // d)


def round_interval(lo, hi):
    return (lo.numerator * SCALE // lo.denominator,
            ceil_div(hi.numerator * SCALE, hi.denominator))


@lru_cache(None)
def log_interval(x):
    """Atanh series after binary reduction, with a positive geometric tail."""
    x = Q(x)
    require(x >= 1, 'log domain')
    k = 0
    while x >= 2:
        x /= 2
        k += 1

    def atanh_log(y):
        z = (y - 1) / (y + 1)
        require(0 <= z <= Q(1, 3), 'log reduction')
        term, total = z, Q(0)
        for j in range(80):
            total += 2 * term / (2 * j + 1)
            term *= z * z
        tail = 2 * term / (161 * (1 - z * z))
        return total, total + tail

    a, b = atanh_log(x)
    c, d = atanh_log(Q(2))
    return round_interval(a + k * c, b + k * d)


def exp_interval(lo, hi):
    """Outward integer Taylor arithmetic; arguments and outputs scaled by SCALE."""
    require(0 <= lo <= hi < SCALE // 10, 'exp domain')
    low_term = high_term = low_sum = high_sum = SCALE
    for j in range(1, 19):
        low_term = low_term * lo // (SCALE * j)
        high_term = ceil_div(high_term * hi, SCALE * j)
        low_sum += low_term
        high_sum += high_term
    # After degree 18, successive remaining ratios are at most x/20.
    tail = ceil_div(high_term * hi * 20, 19 * (20 * SCALE - hi))
    return low_sum, high_sum + tail


def power_interval(m, r, a):
    lo, hi = log_interval(Q(m, r))
    return exp_interval(lo * a.numerator // a.denominator,
                        ceil_div(hi * a.numerator, a.denominator))


def shape():
    p = 10
    h, v = 2 * p, 8 * comb(p, 3)
    return 5 * h, v, (2 * h - 2, h - 1, 2 * h + 2, 4), 12 * (4 * v - 5 * h * (h - 2))


def profile(hist):
    m, v, idle, deficit = shape()
    H = {r: 60 * n for r, n in hist}
    for r in idle:
        H[r] = H.get(r, 0) + 24 * v
    mass = sum(r * n for r, n in H.items())
    require((mass + deficit) % m == 0, 'nonintegral archived stock')
    return H, (mass + deficit) // m


def moment_interval(hist, a):
    """M(a), including the inherited 10^-16, 32*m^2 per-child fallback."""
    H, W = profile(hist)
    m = shape()[0]
    lo = hi = 0
    for r, n in H.items():
        e, f = power_interval(m, r, a)
        lo += r * n * e
        hi += r * n * f
    e, f = power_interval(m, 1, a)
    calls = sum(H.values())
    denominator = 10**16 * m * W
    return ((10**16 * lo + 32 * m * m * calls * e) // denominator,
            ceil_div(10**16 * hi + 32 * m * m * calls * f, denominator))


def j_signature(hist):
    mass = sum(r * n for r, n in hist)
    coefficients = {p: 2 * mass if p in (2, 5) else 0 for p in PRIMES}
    for r, n in hist:
        remaining = r
        for p in PRIMES:
            while remaining % p == 0:
                coefficients[p] -= r * n
                remaining //= p
        require(remaining == 1, 'uncovered prime in local rank')
    return tuple(coefficients[p] for p in PRIMES)


def j_interval(signature):
    lo = hi = 0
    for p, n in zip(PRIMES, signature):
        a, b = log_interval(Q(p))
        lo += n * (a if n >= 0 else b)
        hi += n * (b if n >= 0 else a)
    return lo, hi


def order(a, b):
    if a[1] < b[0]:
        return -1
    if b[1] < a[0]:
        return 1
    raise ValueError('unresolved interval order')


def nominal_kappa(root_endpoint):
    """Monotone historical arithmetic map; not an admission of 47 constraints."""
    c = Q((root_endpoint * KAPPA_GRID).__floor__(), KAPPA_GRID)
    b = Q(772714351296671, KAPPA_GRID)
    cap = (1 - Q(1, 10**9)) * b
    require(0 < c < cap - Q(1, KAPPA_GRID) and c < Q(1, 1000), 'bit cap or monotonicity domain')
    bit = Q(384599, 10**10)
    for _ in range(3):
        bit = (1 - c) * c + c * bit
    eta = Q(1, 10**12)
    q = bit * (1 - 2 * eta)
    limit = (1 - eta) * q / (1 + q)
    ticks = limit * KAPPA_GRID
    return Q((ticks.numerator - 1) // ticks.denominator, KAPPA_GRID)


def parse_records(raw):
    rows = json.loads(raw, parse_float=Decimal)
    require(type(rows) is list and len(rows) == 761, 'expected 761 records')
    require([r['name'] for r in rows] == [f'u{i:04}' for i in range(761)], 'record coverage or order')
    for row in rows:
        hist = row['hist']
        require(type(hist) is dict and hist, 'empty histogram')
        require(all(type(k) is str and k.isdecimal() and str(int(k)) == k and 1 <= int(k) <= 20
                    and type(n) is int and n > 0 for k, n in hist.items()), 'invalid histogram')
        row['_hist'] = tuple(sorted((int(r), n) for r, n in hist.items()))
        for key in ('mass', 'N', 'Wn'):
            require(type(row[key]) is int, 'invalid integer metadata')
        require(row['mass'] == sum(r * n for r, n in row['_hist']), 'mass mismatch')
        require(row['N'] == sum(n for _, n in row['_hist']), 'call mismatch')
        require(profile(row['_hist'])[1] == row['Wn'], 'stock mismatch')
        require(isinstance(row['a'], Decimal) and Q(0) < Q(row['a']) < Q(1, 1000), 'invalid root proposal')
    return rows


def source_data(root):
    pins = json.loads((root / 'SOURCES.json').read_text())
    require(pins['base_commit'] == '91a2094f2e022930069e8cfdc810a3ea1b81cd09', 'wrong base pin')
    expected = {entry['local'] for entry in pins['files']}
    actual = {p.relative_to(root).as_posix() for p in (root / 'sources').rglob('*') if p.is_file()}
    require(actual == expected and len(expected) == len(pins['files']), 'source inventory mismatch')
    for entry in pins['files']:
        data = (root / entry['local']).read_bytes()
        if entry.get('encoding') == 'gzip':
            data = gzip.decompress(data)
        require(sha256(data).hexdigest() == entry['sha256'], 'source digest: ' + entry['local'])
    return gzip.decompress((root / 'sources/hist_dataset.json.gz').read_bytes())


def reconcile(raw):
    rows = parse_records(raw)
    grouped = defaultdict(list)
    for row in rows:
        grouped[row['_hist']].append(row)
    groups = []
    membership = {}
    for hist, members in grouped.items():
        proposal = Q(members[0]['a'])
        tick = (proposal * ROOT_GRID).__floor__()
        a, b = Q(tick - 2, ROOT_GRID), Q(tick + 2, ROOT_GRID)
        left, right = moment_interval(hist, a), moment_interval(hist, b)
        require(left[1] < SCALE < right[0], 'root bracket failed: ' + members[0]['name'])
        kappa = nominal_kappa(a), nominal_kappa(b)
        for row in members:
            require(kappa[0] <= Q(row['kappa_re']) <= kappa[1], 'stored kappa outside independently certified range')
        signature = j_signature(hist)
        ji = j_interval(signature)
        index = len(groups)
        for row in members:
            membership[row['name']] = index
        groups.append(dict(names=[r['name'] for r in members], root_interval=[str(a), str(b)],
                           moment_left_upper_numerator=left[1], moment_right_lower_numerator=right[0],
                           j_prime_exponents=list(signature), j_interval_numerators=list(ji),
                           nominal_kappa_interval=[str(v) for v in kappa]))
    # Only independent intervals determine order; historical floating J/kappa do not.
    inversions = []
    ties = agree = 0
    pair_labels = []
    for left, right in combinations(rows, 2):
        i, j = membership[left['name']], membership[right['name']]
        a, b = groups[i], groups[j]
        if i == j:
            ties += 1
            label = 'identical-histogram'
        else:
            js = order(a['j_interval_numerators'], b['j_interval_numerators'])
            rs = order(tuple(map(Q, a['root_interval'])), tuple(map(Q, b['root_interval'])))
            ks = order(tuple(map(Q, a['nominal_kappa_interval'])), tuple(map(Q, b['nominal_kappa_interval'])))
            require(rs == ks, 'root and nominal kappa order differ')
            if js == ks:
                inversions.append(dict(left=left['name'], right=right['name'],
                                       smaller_j=left['name'] if js < 0 else right['name'],
                                       larger_nominal_kappa=right['name'] if ks < 0 else left['name']))
                label = 'reversal'
            else:
                agree += 1
                label = 'agreement'
        pair_labels.append(f"{left['name']} {right['name']} {label}\n")
    a = groups[membership['u0089']]
    b = groups[membership['u0302']]
    gap = (Q(b['j_interval_numerators'][0] - a['j_interval_numerators'][1], SCALE),
           Q(b['j_interval_numerators'][1] - a['j_interval_numerators'][0], SCALE))
    gap_lower = Q((gap[0] * 10**10).__floor__(), 10**10)
    gap_upper = Q((gap[1] * 10**10).__ceil__(), 10**10)
    require(Q(9, 10) < gap_lower < gap[0] <= gap[1] < gap_upper, 'report gap counterexample')
    return dict(status='EXACT_HISTORICAL_J_ORDER_RECONCILIATION_NO_NEW_KAPPA',
                reported_gap_bound_counterexample=dict(pair=['u0089', 'u0302'],
                    absolute_j_gap=[str(gap_lower), str(gap_upper)], rejected_bound='9/10'),
                records=len(rows), distinct_histograms=len(groups), all_pairs=comb(len(rows), 2),
                identical_histogram_pairs=ties, strictly_ordered_pairs=agree + len(inversions),
                agreements=agree, reversals=inversions,
                distinct_reversing_histogram_pairs=len({tuple(sorted((membership[p['left']], membership[p['right']])))
                                                       for p in inversions}),
                interval_denominator=SCALE,
                pair_classification_sha256=sha256(''.join(pair_labels).encode()).hexdigest(), groups=groups)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write a new result after all checks; existing paths refused.')
    parser.add_argument('--check', type=Path, default=HERE / 'RESULT.json')
    args = parser.parse_args()
    result = reconcile(source_data(HERE))
    if args.output:
        with args.output.open('x') as f:
            f.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(result == json.loads(args.check.read_text()), 'recorded result mismatch')
    print(f"PASS_HISTORICAL_J_ORDER records={result['records']} histograms={result['distinct_histograms']} "
          f"pairs={result['all_pairs']} ties={result['identical_histogram_pairs']} "
          f"agreements={result['agreements']} reversals={len(result['reversals'])} no_new_kappa")


if __name__ == '__main__':
    main()

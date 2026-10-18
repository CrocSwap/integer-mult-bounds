#!/usr/bin/env python3
"""Independent fixed-model T185 integer-face certificate. Apache-2.0.

Arham Tahir with substantial OpenAI Codex assistance. No predecessor code is
imported. Integer intervals use the positive binomial series, not log/exp.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTHS = (4, 5, 7, 8, 9)
CAPS = {8: 672, 16: 448, 32: 448, 48: 448}
INVENTORY = {4: 26, 5: 2, 7: 62, 8: 84, 9: 234}
LOW = Q('0.001720100805416885927944')
HIGH = Q('0.001720100805416885927945')
SCALE = 1 << 384
TERMS = 8192
# a,...,k in the proof; a pattern is (capacity, sorted helper widths).
TIGHT = (
    (8, (8,)), (16, (8, 8)), (16, (7, 9)),
    (32, (9, 9, 9)), (32, (8, 8, 8, 8)), (32, (7, 8, 8, 9)),
    (32, (7, 7, 9, 9)), (32, (5, 9, 9, 9)), (32, (4, 9, 9, 9)),
    (48, ()), (48, (9, 9, 9, 9, 9)),
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(raw, pin):
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256 mismatch')
    header = ('blob ' + str(len(raw)) + '\0').encode('ascii')
    require(hashlib.sha1(header + raw).hexdigest() == pin['git_blob'], 'source Git blob mismatch')
    require(len(raw) == pin['bytes'], 'source length mismatch')


def sources():
    manifest = json.loads((HERE / 'SOURCE-EXPORT.json').read_bytes())
    result = {}
    for pin in manifest['files']:
        require(pin['commit'] == '34328b1d5e5bebac62d5cabec993dfbfd7b2123f', 'predecessor head')
        raw = (HERE / pin['export']).read_bytes()
        authenticate(raw, pin)
        result[pin['export']] = raw
    return result


def ceildiv(n, d):
    return -(-n // d)


@lru_cache(None)
def power_bounds(n, alpha, terms=TERMS):
    """Enclose SCALE*n**(1-alpha) using positive binomial terms.

    z=1-1/n; 1-(1-z)**alpha=sum t_k, t_1=alpha*z,
    t_(k+1)/t_k=z*(k-alpha)/(k+1)<z. After K terms the
    omitted tail is between zero and n*t_(K+1).
    """
    require(type(n) is int and n >= 1 and 0 < alpha < 1, 'power domain')
    require(type(terms) is int and terms >= 1, 'series terms')
    if n == 1:
        return SCALE, SCALE
    num, den = alpha.numerator, alpha.denominator
    bottom = n * den
    lo = SCALE * num * (n - 1) // bottom
    hi = ceildiv(SCALE * num * (n - 1), bottom)
    sum_lo, sum_hi = lo, hi
    for k in range(1, terms):
        top, bottom = (n - 1) * (k * den - num), n * (k + 1) * den
        lo = lo * top // bottom
        hi = ceildiv(hi * top, bottom)
        sum_lo += lo
        sum_hi += hi
    top = (n - 1) * (terms * den - num)
    bottom = n * (terms + 1) * den
    next_hi = ceildiv(hi * top, bottom)
    return n * (SCALE - sum_hi - n * next_hi), n * (SCALE - sum_lo)


def patterns(capacity, prefix=(), first=0):
    """Recursively grow multisets; never use the predecessor Cartesian census."""
    yield capacity, prefix
    remaining = capacity - sum(prefix)
    for i in range(first, len(WIDTHS)):
        if WIDTHS[i] <= remaining:
            yield from patterns(capacity, prefix + (WIDTHS[i],), i)


def linear_sum(*terms):
    result = Counter()
    for coefficient, expression in terms:
        for rank, value in expression.items():
            result[rank] += coefficient * value
    return {r: c for r, c in result.items() if c}


def dual_prices():
    q = {3: Q(1, 5), 48: Q(-1, 5)}
    c = linear_sum((1, {5: Q(1)}), (-3, q))
    capacity = {8: linear_sum((Q(1, 4), c)), 16: linear_sum((Q(1, 2), c)),
                32: c, 48: {48: Q(1)}}
    helper = {4: {1: Q(1), 5: Q(-1)}, 5: {5: Q(-1)},
              7: linear_sum((Q(-1, 2), c), (-1, q)),
              8: linear_sum((Q(-1, 4), c)), 9: q}
    return capacity, helper


def interval(expression, powers):
    lo = hi = Q(0)
    for rank, value in expression.items():
        a, b = powers[rank]
        lo += value * (a if value > 0 else b)
        hi += value * (b if value > 0 else a)
    return lo, hi


def prove_tight_set(powers, capacity, helper):
    tight, total, minimum = set(), 0, None
    for cap in CAPS:
        for pattern in patterns(cap):
            total += 1
            _, items = pattern
            remainder = cap - sum(items)
            rhs = {remainder: Q(1)} if remainder else {}
            slack = linear_sum((1, rhs), (-1, capacity[cap]),
                               *((-1, helper[w]) for w in items))
            if not slack:
                tight.add(pattern)
            else:
                lo, _ = interval(slack, powers)
                require(lo > 0, 'non-tight pattern has no strict positive slack: ' + str(pattern))
                minimum = lo if minimum is None else min(minimum, lo)
    require(total == 1163, 'pattern census')
    require(tight == set(TIGHT), 'unexpected tight face')
    return total, minimum


def inventory(counts):
    bins, helpers, idle = Counter(), Counter(), Counter()
    for (cap, items), count in counts.items():
        require(count >= 0, 'negative multiplicity')
        bins[cap] += count
        for w in items:
            helpers[w] += count
        if cap > sum(items):
            idle[cap - sum(items)] += count
    return dict(bins), dict(helpers), dict(idle)


def face(t, u, v):
    require(type(t) is int and t > 0 and t % 5 == 0, 'replica divisibility/domain')
    require(type(u) is int and type(v) is int and 0 <= u <= 21*t and -u <= v <= u,
            'integer face domain')
    values = (672*t, u+v, 448*t-u-v, 120*t, 21*t-u, u-v,
              55*t+v, 18*t, 234*t, 1808*t//5, 432*t//5)
    return dict(zip(TIGHT, values, strict=True))


def validate_face(counts, t):
    require(all(type(n) is int and n >= 0 for n in counts.values()), 'whole-bin multiplicity')
    require(set(counts) == set(TIGHT), 'tight pattern domain')
    bins, helpers, idle = inventory(counts)
    require(bins == {c: n*t for c, n in CAPS.items()}, 'bin inventory')
    require(helpers == {w: 9*n*t for w, n in INVENTORY.items()}, 'helper inventory')
    require(idle == {1: 234*t, 3: Q(432*t, 5), 5: 120*t, 48: Q(1808*t, 5)},
            'fixed optimum idle profile')
    return idle


def rounded_witness(t):
    """A feasible abstract packing for every T, including T not divisible by 5.

    Only its single partially filled capacity-48 bin can be non-tight.
    This is an upper bound on an integrality gap, not integer optimality.
    """
    require(type(t) is int and t > 0, 'rounded witness domain')
    full, remainder = divmod(432*t, 5)
    values = (672*t, 0, 448*t, 120*t, 21*t, 0, 55*t, 18*t, 234*t,
              448*t-full-int(bool(remainder)), full)
    counts = dict(zip(TIGHT, values, strict=True))
    if remainder:
        counts[48, (9,)*remainder] = 1
    return counts


def rref(rows):
    """Exact Gaussian elimination, also recording the two free coordinates."""
    a = [[Q(x) for x in row] for row in rows]
    row, pivots = 0, []
    for col in range(len(a[0])-1):
        hit = next((k for k in range(row, len(a)) if a[k][col]), None)
        if hit is None:
            continue
        a[row], a[hit] = a[hit], a[row]
        d = a[row][col]
        a[row] = [x/d for x in a[row]]
        for k in range(len(a)):
            if k != row:
                d = a[k][col]
                a[k] = [x-d*y for x, y in zip(a[k], a[row], strict=True)]
        pivots.append(col)
        row += 1
        if row == len(a):
            break
    return a, pivots


def prove_elimination():
    # Order the nine dependent variables first, then b and f as free variables.
    order = (0, 2, 3, 4, 6, 7, 8, 9, 10, 1, 5)
    columns = [TIGHT[i] for i in order]
    rows = [[int(cap == c) for cap, _ in columns] + [n] for c, n in CAPS.items()]
    rows += [[items.count(w) for _, items in columns] + [9*n] for w, n in INVENTORY.items()]
    reduced, pivots = rref(rows)
    require(pivots == list(range(9)), 'unexpected inventory rank/free coordinates')
    # Rows express x = rhs*T - row[b]*b - row[f]*f.
    expected = (
        (Q(672), 0, 0), (Q(448), -1, 0), (Q(120), 0, 0),
        (Q(21), Q(-1, 2), Q(-1, 2)), (Q(55), Q(1, 2), Q(-1, 2)),
        (Q(18), 0, 0), (Q(234), 0, 0), (Q(1808, 5), 0, 0), (Q(432, 5), 0, 0),
    )
    actual = tuple((row[-1], -row[-3], -row[-2]) for row in reduced)
    require(actual == expected, 'all-T elimination certificate')
    return [[str(x) for x in row] for row in reduced]


def rejection(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise ValueError('negative control unexpectedly accepted: ' + function.__name__)


def verify():
    raw = sources()
    providers = json.loads(raw['source/data__PROVIDERS.json'])
    require(all(Counter(p['widths']) == INVENTORY for p in providers.values()), 'source width inventory')
    require(all(p == providers['extra'] for p in providers.values()), 'common provider price')
    previous = json.loads(raw['source/review__lp-final-01__RESULT.json'])
    capacity, helper = dual_prices()
    for key, prices in [('dual_capacity_prices', capacity), ('dual_helper_prices', helper)]:
        require(previous[key] == {str(w): {str(r): str(v) for r, v in expression.items()}
                                  for w, expression in prices.items()}, 'predecessor symbolic prices')
    require([Q(x) for x in previous['moment_root_bracket']] == [LOW, HIGH], 'root interval pin')
    powers = {r: (power_bounds(r, HIGH)[0], power_bounds(r, LOW)[1]) for r in range(1, 49)}
    census, minimum = prove_tight_set(powers, capacity, helper)
    require(minimum > SCALE*Q(1, 250), 'uniform non-tight gap')
    eliminated = prove_elimination()
    native = {int(r): n for r, n in providers['extra']['actual_paid_profile'].items()}
    optimal = {r: Q(9*n) for r, n in native.items()}
    for r, n in inventory(face(5, 0, 0))[2].items():
        optimal[r] = optimal.get(r, 0) + Q(n, 5)
    dual = linear_sum(*((n, capacity[c]) for c, n in CAPS.items()),
                      *((9*n, helper[w]) for w, n in INVENTORY.items()))
    require(dual == {1: Q(234), 3: Q(432, 5), 5: Q(120), 48: Q(1808, 5)},
            'symbolic primal/dual equality')
    margins = []
    for alpha, accepted in [(LOW, True), (HIGH, False)]:
        p = {r: power_bounds(r, alpha) for r in optimal}
        lo, hi = interval(optimal, p)
        lower73, upper73 = power_bounds(73, alpha)
        bounds = (lo - 896*upper73, hi - 896*lower73)
        require(bounds[1] < 0 if accepted else bounds[0] > 0, 'independent moment root sign')
        margins.append([str(x / SCALE) for x in bounds])
    actual_profile = {int(r): n for r, n in json.loads(raw['source/data__PROFILE.json']).items()}
    require(actual_profile == {r: 185*n for r, n in optimal.items()}, 'source T185 paid profile')
    # Second integer parameterization: enumerate b,f with their parity restriction.
    # Every integer point of the smallest feasible replica count is tested.
    seen = set()
    for b in range(42*5+1):
        for f in range(b % 2, 42*5-b+1, 2):
            u, v = (b+f)//2, (b-f)//2
            counts = face(5, u, v)
            validate_face(counts, 5)
            require(counts[TIGHT[1]] == b and counts[TIGHT[5]] == f, 'inverse face coordinates')
            seen.add(tuple(counts.values()))
    require(len(seen) == 106**2, 'complete T5 integer-face census')
    for t in (10, 15, 20, 185, 10**12):
        for u, v in ((0, 0), (21*t, -21*t), (21*t, 21*t), (21*t, 0)):
            validate_face(face(t, u, v), t)
    for t in range(1, 201):
        require((Q(432*t, 5).denominator == 1) == (t % 5 == 0), 'necessary congruence')
        bins, helpers, idle = inventory(rounded_witness(t))
        require(bins == {c: n*t for c, n in CAPS.items()}, 'rounded bin inventory')
        require(helpers == {w: 9*n*t for w, n in INVENTORY.items()}, 'rounded helper inventory')
        remainder = 432*t % 5
        difference = linear_sum((1, idle), (-t, dual))
        expected = ({} if not remainder else
                    {48-9*remainder: Q(1), 3: Q(-remainder, 5), 48: Q(remainder-5, 5)})
        require(difference == expected, 'rounded witness excess identity')
        if remainder:
            require(interval(difference, powers)[0] > SCALE*Q(1, 250), 'positive rounded excess')
    controls = []
    for name, args in [('wrong_replica', (37, 0, 0)), ('negative_u', (5, -1, 0)),
                       ('outside_v', (5, 1, 2)), ('excess_u', (5, 106, 0)),
                       ('noninteger_coordinate', (5, Q(1, 2), 0))]:
        rejection(face, *args)
        controls.append(name)
    bad = face(5, 0, 0)
    bad[TIGHT[10]] += 1
    rejection(validate_face, bad, 5)
    controls.append('one_extra_full48_bin')
    bad = face(5, 0, 0)
    bad[TIGHT[0]] -= 1
    rejection(validate_face, bad, 5)
    controls.append('one_missing_width8_helper')
    # A real feasible T37 pattern packing must fail exact-attainment validation.
    # Its partial bin is not among the eleven tight patterns.
    rejection(validate_face, rounded_witness(37), 37)
    controls.append('feasible_T37_is_not_exact_optimum')
    bad_capacity = dict(capacity)
    bad_capacity[8] = linear_sum((1, capacity[8]), (1, {1: Q(1)}))
    rejection(prove_tight_set, powers, bad_capacity, helper)
    controls.append('forged_dual_price')
    pin = json.loads((HERE / 'SOURCE-EXPORT.json').read_bytes())['files'][0]
    rejection(authenticate, raw[pin['export']] + b' ', pin)
    controls.append('source_corruption')
    # Squaring positive endpoints calibrates the series at alpha=1/2.
    # Short-series cases deliberately exercise the omitted-tail bound.
    for n in (2, 3, 9, 48, 73):
        for terms in (1, 4, TERMS):
            lo, hi = power_bounds(n, Q(1, 2), terms)
            require(lo <= 0 or lo*lo <= n*SCALE*SCALE, 'binomial lower calibration')
            require(hi > 0 and hi*hi >= n*SCALE*SCALE, 'binomial upper calibration')
    # Omitting the binomial tail gives the false lower bound 3/2 for sqrt(2).
    require(Q(3, 2)**2 > 2, 'missing-tail falsifier')
    controls.append('omitted_binomial_tail_falsified')
    return {'status': 'PASS_T185_INTEGER_OPTIMAL_FACE', 'patterns': census, 'tight_patterns': 11,
            'minimum_strict_slack_lower': str(minimum / SCALE),
            'root_bracket': [str(LOW), str(HIGH)], 'root_moment_margins': margins,
            'inventory_rref': eliminated, 'integral_attainment_iff': 'T > 0 and T % 5 == 0',
            'multiplicity_vector_count': '(21*T + 1)^2 when 5 divides T; zero otherwise',
            'T5_vectors_checked': len(seen), 'T185_vector_count': (21*185+1)**2,
            'nondivisible_T_unnormalized_excess_strictly_above': '1/250',
            'rounded_witness_T_checked': 200,
            'controls': controls, 'power_method': 'positive binomial; 384-bit directed integers; 8192 terms',
            'scope': 'Abstract fixed-inventory packing face only; no literal chronology, physical realization, supplier or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true', help='explicitly regenerate RESULT.json')
    args = parser.parse_args()
    result = verify()
    data = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write_result:
        (HERE / 'RESULT.json').write_text(data, encoding='utf-8', newline='\n')
    else:
        require(json.loads((HERE / 'RESULT.json').read_bytes()) == result, 'committed result mismatch')
    print(result['status'], 'patterns=1163 tight=11 T5_vectors=11236 controls=' + str(len(result['controls'])))


if __name__ == '__main__':
    main()

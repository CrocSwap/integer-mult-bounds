#!/usr/bin/env python3
"""Critical-root hypotheses for the retained p7 and p16 rank inventories.

Separate exact arithmetic and mirror enumeration; no predecessor evaluator is
imported. The inventories and native contracts remain credited source inputs.
Dillon with substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path


GRID = 1 << 128
PINS = {
    'research/higher-moment-strictification/RESULT.json':
        'ad79e3c0459e7b495a0ca34010553b12147779a007389e1695cc1336f123c156',
    'research/compact-joint-compiler/arithmetic/RESULT.json':
        'a6caaa2a6d6460a8c1ef7e48c4853bb27976be33a52b96a4216dfa90d96c9091',
    'research/joint-helper-lattice/RESULT.json':
        'c7b2388f6511c19976b337d8c8ac374610af616866a249d75dace704eb5d9e21',
    'research/rank-convergence/BENCHMARKS.json':
        '513efe2fe74af82891c1918e462ba8338b1bbd06403cbfcec284bcf3b4f8f850',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def floorq(x):
    return x.numerator // x.denominator


def ceilq(x):
    return -((-x.numerator) // x.denominator)


def outward(lo, hi):
    return floorq(lo * GRID), ceilq(hi * GRID)


@lru_cache(None)
def logarithm(n):
    """Integer endpoints in units 2^-128, using an exact atanh tail."""
    require(type(n) is int and n >= 1, 'positive integer logarithm')

    def series(y):
        z = (y - 1) / (y + 1)
        require(0 <= z <= F(1, 3), 'logarithm range reduction')
        # log(y)=2 sum z^(2j+1)/(2j+1). Every omitted denominator
        # is at least 121, so the geometric tail bounds all omitted terms.
        term, total = z, F(0)
        for j in range(60):
            total += 2 * term / (2*j + 1)
            term *= z*z
        return total, total + 2*term / (121*(1-z*z))

    exponent = n.bit_length() - 1
    a, b = series(F(n, 1 << exponent))
    c, d = series(F(2))
    return outward(a + exponent*c, b + exponent*d)


def exponential(x):
    """Outward integer endpoints for exp(exact rational x)."""
    x = F(x)
    if x == 0:
        return GRID, GRID
    if x < 0:
        lo, hi = exponential(-x)
        return GRID*GRID // hi, -((-GRID*GRID) // lo)
    squarings = 0
    while x > F(1, 2):
        x /= 2
        squarings += 1
    term_lo = term_hi = total_lo = total_hi = GRID
    for j in range(1, 65):
        term_lo = floorq(term_lo*x/j)
        term_hi = ceilq(term_hi*x/j)
        total_lo += term_lo
        total_hi += term_hi
    # The next term is x^65/65!. Subsequent ratios are <=1/132;
    # twice an upper enclosure of that term bounds the entire tail.
    total_hi += 2*ceilq(term_hi*x/65)
    for _ in range(squarings):
        total_lo = total_lo*total_lo // GRID
        total_hi = -((-total_hi*total_hi) // GRID)
    return total_lo, total_hi


@lru_cache(None)
def power(n, t):
    t = F(t)
    lo, hi = logarithm(n)
    endpoints = [F(lo, GRID)*t, F(hi, GRID)*t]
    lower = exponential(min(endpoints))[0]
    upper = exponential(max(endpoints))[1]
    return F(lower, GRID), F(upper, GRID)


def moment(histogram, t):
    lo = hi = F(0)
    for rank, count in histogram.items():
        a, b = power(rank, t)
        lo += count*a
        hi += count*b
    return lo, hi


def mean(histogram, t):
    lo = hi = F(0)
    for rank, count in histogram.items():
        a, b = power(rank, t)
        c, d = logarithm(rank)
        lo += count*a*F(c, GRID)
        hi += count*b*F(d, GRID)
    total_lo, total_hi = moment(histogram, t)
    require(total_lo > 0, 'positive tilted total')
    return lo/total_hi, hi/total_lo


def display(interval):
    # These short rational bounds are rounded outward, never floating point.
    unit = 10**6
    return [str(F(floorq(interval[0]*unit), unit)),
            str(F(ceilq(interval[1]*unit), unit))]


def histogram(raw):
    require(isinstance(raw, dict) and raw, 'nonempty histogram')
    result = {}
    for key, count in raw.items():
        rank = int(key)
        require(str(rank) == str(key) and rank >= 1,
                'canonical positive integer rank')
        require(type(count) is int and count > 0, 'positive multiplicity')
        result[rank] = count
    return result


def mirror_sides(targets, paid, x):
    sources, exits = Counter(), Counter()
    for k, w in targets.items():
        for r, count in paid.items():
            if k > r and F(1, k) < x <= F(1, r):
                sources[k*r] += w*count
            if r > k and F(1, r) < x <= F(1, k):
                exits[k*r] += w*count
    return sources, exits


def certify(profile, lo, hi, beta, derivative_floor):
    targets, paid = (histogram(profile[key]) for key in ('targets', 'paid'))
    m = max(targets)
    require(min(targets) >= 2 and max(paid) < m and paid.get(1, 0) > 0,
            'native rank interface and nonempty forests')
    require(0 < lo < hi < 1, 'critical exponent interval')
    require(sum(k*q for k, q in targets.items()) >
            sum(k*q for k, q in paid.items()), 'positive rank-one surplus')
    first_t, first_p = moment(targets, lo), moment(paid, lo)
    last_t, last_p = moment(targets, hi), moment(paid, hi)
    first = first_t[0]-first_p[1], first_t[1]-first_p[0]
    last = last_t[0]-last_p[1], last_t[1]-last_p[0]
    require(first[1] < 0 < last[0], 'root sign crossing')
    # Each tilted mean is nondecreasing: its derivative is the variance
    # of log(rank). Thus this bounds their difference on the whole interval.
    gap = mean(targets, lo)[0] - mean(paid, hi)[1]
    require(gap > derivative_floor > 0, 'positive crossing derivative')
    # t*m^(t-1) increases for t>0, since its derivative has the sign
    # of 1+t*log(m). This lower bound therefore applies at the unknown root.
    eta = lo*power(m, lo-1)[0]
    require(0 <= beta < eta, 'strict mirror capacity')
    points = sorted({F(0), *(F(1, k) for k in targets),
                     *(F(1, r) for r in paid)})
    cells, worst, worst_cell = [], F(0), None
    for left, right in zip(points, points[1:]):
        source, exit_ = mirror_sides(targets, paid, (left+right)/2)
        require((source, exit_) == mirror_sides(targets, paid, right),
                'right-closed mirror endpoint')
        ehi = moment(exit_, hi)[1]
        slo = moment(source, lo)[0]
        require(ehi <= beta*slo, 'uniform mirror inequality')
        if exit_:
            ratio = ehi/slo
            cells.append({'left': str(left), 'right': str(right),
                          'upper_ratio': display((ratio, ratio))[1]})
            if ratio > worst:
                worst, worst_cell = ratio, [str(left), str(right)]
    require(mirror_sides(targets, paid, F(0)) == (Counter(), Counter()),
            'zero mirror endpoint')
    require(mirror_sides(targets, paid, 2*points[-1]) == (Counter(), Counter()),
            'empty mirror tail')
    return {'critical_root_interval': [str(lo), str(hi)],
            'endpoint_target_minus_paid': [display(first), display(last)],
            'uniform_mean_gap_lower': display((gap, gap))[0],
            'derivative_floor': str(derivative_floor),
            'beta': str(beta), 'source_capacity_lower': display((eta, eta))[0],
            'mirror_upper': display((worst, worst))[1],
            'maximizing_cell': worst_cell, 'funded_mirror_cells': cells,
            'conclusion': 'Unique crossing on this bracket; critical-root hypotheses hold.',
            'scope': 'Rank-inventory admission criterion; native and outer obligations inherited.'}


def arithmetic_controls():
    count = 0
    for base in (1, 2, 3, 5, 16, 121, 145, 10440):
        for exponent in (F(-1, 2), F(0), F(1, 4), F(1, 2), F(1), F(2)):
            lo, hi = power(base, exponent)
            require(lo > 0 and lo**exponent.denominator <= F(base)**exponent.numerator
                    <= hi**exponent.denominator, 'exact power enclosure control')
            count += 1
    return count


def critical_guards(profile, root_lo, root_hi, witness):
    """Fund a shifted-logarithmic majorant at the isolated critical root.

    Uniform inequalities cover [root_lo, upper_exponent], a superset of
    every unknown-root interval needed in the written endpoint theorem.
    Parameters are inherited from #4483 except the explicit cover and beta.
    """
    targets, paid = (histogram(profile[key]) for key in ('targets', 'paid'))
    m = max(targets)
    top = F(witness['upper_exponent'])
    a, b, M, ell = (witness[key] for key in ('a', 'b', 'height_base', 'ell0'))
    require(all(type(v) is int and v >= 1 for v in (a, b, ell)) and
            type(M) is int and M >= 2, 'critical integer geometry')
    s, lam, p, c = (F(witness[key]) for key in ('s', 'lambda', 'p', 'c'))
    require(0 < root_lo < root_hi < top < 1 and min(s, lam, p, c) > 0,
            'critical parameter domain')
    U, V, Q, d, beta = (F(witness['guards'][key])
                       for key in ('U', 'V', 'Q', 'd', 'beta'))
    require(0 < U < 1 and 0 < V < 1 and Q >= 1 and d > 0,
            'critical uniform guard domain')
    require(c >= p/(1-root_hi), 'critical concavity')
    mean_gap = mean(targets, root_lo)[0] - mean(paid, top)[1]
    require(mean_gap >= d, 'critical mean gap')

    def forward(h, t):
        x, y = moment(h, t+s), moment(h, t)
        return x[0]/y[1], x[1]/y[0]

    # The derivative of log(M_h(t+s)/M_h(t)) is mu_h(t+s)-mu_h(t)
    # and is nonnegative, because a tilted mean has variance derivative.
    ordering = forward(targets, root_lo)[0] - forward(paid, top)[1]
    require(ordering >= 0, 'critical forward ordering')
    actual_u = power(M, -s)[1]*forward(targets, top)[1]**a*forward(paid, top)[1]**b
    actual_v = power(M, lam)[1]*(moment(targets, top-lam)[1]/moment(paid, root_lo)[0])**(a+b)
    actual_q = moment(targets, top)[1]/moment(paid, root_lo)[0]
    require(actual_u <= U, 'critical mixed tail')
    require(actual_v <= V, 'critical root tail')
    require(actual_q <= Q, 'critical moment ratio')
    eta = root_lo*power(m, root_lo-1)[0]
    require(0 <= beta < eta < 1, 'critical mirror capacity')
    points = sorted({F(0), *(F(1, k) for k in targets),
                     *(F(1, r) for r in paid)})
    mirror_upper = F(0)
    for left, right in zip(points, points[1:]):
        sources, exits = mirror_sides(targets, paid, (left+right)/2)
        numerator, denominator = moment(exits, top)[1], moment(sources, root_lo)[0]
        require(numerator <= beta*denominator, 'critical mirror window')
        if exits:
            mirror_upper = max(mirror_upper, numerator/denominator)

    def log(n):
        return tuple(F(x, GRID) for x in logarithm(n))

    logn0_lo = log(m)[0] + ell*log(M)[0]
    tau_upper = root_hi + p/(c+logn0_lo)
    require(tau_upper <= top, 'critical tangent cover')
    denominator = c + log(m)[1] + (ell+1)*log(M)[1] + log(2)[1]
    K = d*p*(a*ell+1)/denominator
    lower = (1-U**ell)*(F(exponential(K)[0], GRID)-1)-Q*power(M, lam)[1]*V**ell
    required = (1-eta)/(eta-beta)
    require(lower >= required, 'critical recurrence funding')
    return {'parameters': witness,
            'uniform_interval': [str(root_lo), str(top)],
            'uniform_mean_gap_lower': display((mean_gap, mean_gap))[0],
            'forward_ordering_margin_lower': display((ordering, ordering))[0],
            'mixed_tail_upper': display((actual_u, actual_u))[1],
            'root_tail_upper': display((actual_v, actual_v))[1],
            'moment_ratio_upper': display((actual_q, actual_q))[1],
            'mirror_upper': display((mirror_upper, mirror_upper))[1],
            'source_capacity_lower': display((eta, eta))[0],
            'tangent_exponent_upper': display((tau_upper, tau_upper))[1],
            'funding_lower': display((lower, lower))[0],
            'required_funding_upper': display((required, required))[1],
            'ordinary_base_cutoff': str(m)+'*'+str(M)+'^'+str(ell),
            'normalization': 'A=n0^(1-theta)/(c+log(n0))^p, where theta is the isolated root',
            'conclusion': 'L(n)<=A*n^theta*(c+log(n))^p for every integer n>=1, under the stated contracts.',
            'scope': 'Critical-exponent leaf-count majorant; no new outer endpoint or physical admission.'}


def run(root):
    root = Path(root)
    sources = {}
    for path, digest in PINS.items():
        raw = (root/path).read_bytes()
        require(sha256(raw).hexdigest() == digest, 'source bytes: '+path)
        sources[path] = json.loads(raw)
    p7 = sources['research/higher-moment-strictification/RESULT.json']['invoice_oracle']
    p16 = sources['research/compact-joint-compiler/arithmetic/RESULT.json']
    native = sources['research/joint-helper-lattice/RESULT.json']
    require(all(p16[k] == native[k] for k in ('targets', 'paid')),
            'p16 consumer/native inventory equality')
    cases = [('p7', p7, F('0.997313'), F('0.997314'), F('0.321'), F(1)),
             ('p16', p16, F('0.996979'), F('0.996980'), F('0.564'), F(1))]
    results, rejected = {}, {}
    original = {row['name']: row['witness'] for row in
                sources['research/rank-convergence/BENCHMARKS.json']['cases']}
    for name, profile, lo, hi, beta, gap in cases:
        results[name] = certify(profile, lo, hi, beta, gap)
        mutations = {
            'no crossing': (F('0.998'), F('0.999'), beta, gap),
            'unfunded mirror': (lo, hi, F(0), gap),
            'false derivative': (lo, hi, beta, F(100)),
        }
        for label, args in mutations.items():
            try:
                certify(profile, *args)
            except ValueError as error:
                expected = {'no crossing': 'root sign crossing',
                            'unfunded mirror': 'uniform mirror inequality',
                            'false derivative': 'positive crossing derivative'}[label]
                require(str(error) == expected, 'unexpected control rejection')
                rejected[name+': '+label] = str(error)
            else:
                raise ValueError('accepted root-application mutation: '+label)
        # Retain the predecessor's actual geometry, tails, logarithmic power,
        # concavity constant, cutoff, and U/V/Q/d guards. The root replaces its
        # strict base exponent; cover endpoints and the p7 beta are explicit.
        previous = original[name]
        witness = {key: previous[key] for key in
                   ('a', 'b', 'height_base', 'ell0', 's', 'lambda', 'p', 'c')}
        witness['guards'] = {key: previous['guards'][key]
                             for key in ('U', 'V', 'Q', 'd', 'beta')}
        witness['upper_exponent'] = '.997483' if name == 'p7' else '.997067'
        if name == 'p7':
            witness['guards']['beta'] = '.322'
        results[name]['critical_majorant'] = critical_guards(profile, lo, hi, witness)
        defects = {
            'concavity': ('c', '1', 'critical concavity'),
            'tangent cover': ('ell0', 1, 'critical tangent cover'),
            'underfunded logarithm': ('p', str(F(witness['p'])/100), 'critical recurrence funding'),
        }
        for label, (key, value, expected) in defects.items():
            bad = dict(witness, **{key: value})
            try:
                critical_guards(profile, lo, hi, bad)
            except ValueError as error:
                require(str(error) == expected, 'unexpected critical-guard rejection')
                rejected[name+': '+label] = str(error)
            else:
                raise ValueError('accepted critical-guard mutation: '+label)
    return {'source_sha256': PINS, 'applications': results,
            'arithmetic_controls': arithmetic_controls(), 'rejected_controls': rejected,
            'arithmetic': 'Separate exact 128-bit outward log/exp intervals; no producer execution.'}


if __name__ == '__main__':
    print(json.dumps(run(Path(__file__).resolve().parents[2]), sort_keys=True, indent=2))

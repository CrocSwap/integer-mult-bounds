#!/usr/bin/env python3
"""Reusable exact sufficient certificates; no search result is trusted.

The mathematical contracts are in PROOF.md. This checker certifies finite
moment and compiler inequalities, conditional on the supplied native unit.
zxv with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import json
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import intervals as E


def histogram(value):
    E.need(isinstance(value, dict) and value, 'nonempty rank histogram')
    result = {}
    for key, count in value.items():
        rank = int(key)
        E.need(str(rank) == str(key) and rank > 0, 'canonical positive rank')
        E.need(type(count) is int and count > 0, 'positive integer multiplicity')
        result[rank] = count
    return result


def tax_data(profile, witness):
    T, P = histogram(profile['targets']), histogram(profile['paid'])
    m = max(T)
    C, u = Q(witness['saving']), Q(witness['u'])
    t = 1-C
    v, c, b = (witness[k] for k in ('v', 'cutoff', 'floor'))
    E.need(all(type(x) is int for x in (v, c, b)), 'integer construction')
    E.need(0 < C < 1 and C <= u and v >= 1, 'net tax exponent domain')
    E.need(1 < c < b < m and max(P) <= m, 'strict finite rank separation')
    T1, P1 = (sum(k*n for k, n in h.items()) for h in (T, P))
    E.need(T1 > P1, 'positive rank-one surplus')
    target = E.moment(T, t)
    paid = E.moment(P, t)
    alpha = E.divide(paid, target)
    gamma = E.divide(E.moment(P, t+u), E.mul(E.power(c, u), target))
    B = sum(T.values())
    delta = E.divide((Q(B*b),)*2, E.mul(E.power(c, C), target))
    delta0 = E.divide(E.scale(E.power(b, t), B), target)
    concavity_remainder = E.scale(E.qpower(t, t/C), C)
    monotone_coefficient = (max(C/u, concavity_remainder[0]),
                            max(C/u, concavity_remainder[1]))
    if u == C:
        jensen_coefficient = E.power(2, C)
    else:
        jensen_coefficient = E.scale(
            E.mul(E.power(2, u), E.qpower(1-C/u, u/C-1)), C/u)
    coefficient = (min(monotone_coefficient[0], jensen_coefficient[0]),
                   min(monotone_coefficient[1], jensen_coefficient[1]))
    epsilon = E.divide(E.scale(E.power(c, t), B), target)
    original_tax = E.mul(coefficient, E.ipow(gamma, v))
    completion_tax = E.sub(
        E.add(E.ipow(delta, v),
              E.scale(E.mul(concavity_remainder, E.ipow(epsilon, v)), 2)),
        E.ipow(delta0, v))
    bound = E.add(E.add(E.ipow(alpha, v), original_tax), completion_tax)
    E.need(bound[1] < 1, 'strict net moment certificate')
    old_bound = E.add(E.ipow(alpha, v),
                      E.scale(E.add(E.ipow(gamma, v), E.ipow(delta, v)), 2))
    return locals()


def net_tax(profile, witness):
    data = tax_data(profile, witness)
    C, u, v, c, b, m, B, T1, P1 = (data[k] for k in
        ('C', 'u', 'v', 'c', 'b', 'm', 'B', 'T1', 'P1'))
    alpha, gamma, delta, delta0, epsilon = (data[k] for k in
        ('alpha', 'gamma', 'delta', 'delta0', 'epsilon'))
    concavity_remainder, coefficient, original_tax, completion_tax, bound, old_bound = (
        data[k] for k in ('concavity_remainder', 'coefficient', 'original_tax',
                         'completion_tax', 'bound', 'old_bound'))
    return {'saving': str(C), 'v': v, 'cutoff': c, 'floor': b,
            'u': str(u), 'ambient_base': m, 'productive_fields_base': B,
            'rank_one_masses': {'target': T1, 'paid': P1},
            'alpha': E.display(alpha), 'gamma': E.display(gamma),
            'delta': E.display(delta), 'delta0': E.display(delta0),
            'epsilon': E.display(epsilon),
            'concavity_remainder': E.display(concavity_remainder),
            'splitting_coefficient': E.display(coefficient),
            'original_splitting_tax_upper': E.display(original_tax),
            'completion_net_tax_upper': E.display(completion_tax),
            'normalized_net_charge': E.display(bound),
            'strict_gap_lower': E.display(E.sub((Q(1),)*2, bound)),
            'predecessor_full_charge_bound': E.display(old_bound),
            'word_materialized': False}


def weighted_coefficients(p, q, A, B0, beta):
    """Coefficient comparison in the nonnegative integer falling-factorial basis."""
    E.need(type(p) is int and 1 <= p <= 200, 'bounded positive polynomial degree')
    E.need(0 < q <= 1 and A > 0 and B0 > 0 and beta > 0,
           'positive weighted-exit constants')
    S = [[0]*(p+1) for _ in range(p+1)]
    S[0][0] = 1
    for i in range(1, p+1):
        for j in range(1, i+1):
            S[i][j] = S[i-1][j-1]+j*S[i-1][j]
    numerator, denominator = [], []
    for j in range(p+1):
        numerator.append(q**j*sum(
            comb(p, i)*S[i][j]*(q*(A+1)**(p-i)+(1-q)*A**(p-i))
            for i in range(j, p+1)))
        denominator.append(sum(
            comb(p, i)*S[i][j]*B0**(p-i)*beta**i
            for i in range(j, p+1)))
    ratios = [x/y for x, y in zip(numerator, denominator)]
    return max(ratios), ratios.index(max(ratios)), numerator, denominator


def moment_coefficients(p, moments, A, B0, beta):
    """Arbitrary upper log moments, using partial exponential Bell polynomials."""
    E.need(type(p) is int and 1 <= p <= 200 and len(moments) == p+1,
           'bounded complete moment list')
    E.need(moments[0] == 1 and all(0 <= x <= 1 for x in moments),
           'unit-interval moment upper bounds')
    bell = [[Q(0)]*(p+1) for _ in range(p+1)]
    bell[0][0] = Q(1)
    for n in range(1, p+1):
        for k in range(1, n+1):
            bell[n][k] = sum(comb(n-1, j-1)*moments[j]*bell[n-j][k-1]
                             for j in range(1, n-k+2))
    shifted = [sum(comb(n, i)*A**(n-i)*moments[i] for i in range(n+1))
               for n in range(p+1)]
    numerator = [sum(comb(p, l)*shifted[p-l]*bell[l][j]
                     for l in range(j, p+1)) for j in range(p+1)]
    # The denominator's conversion to falling factorials is unchanged.
    _, _, _, denominator = weighted_coefficients(p, Q(1), A, B0, beta)
    ratios = [x/y for x, y in zip(numerator, denominator)]
    return max(ratios), ratios.index(max(ratios)), numerator, denominator


def concentrated_moments(p, v, raw_mean_upper, raw_bound, excess_upper):
    """Raw tensor concentration, then capped-reference mass perturbation."""
    E.need(type(v) is int and v >= 1 and 0 < raw_mean_upper <= raw_bound,
           'bounded raw log law')
    E.need(excess_upper >= 0, 'nonnegative paid mass perturbation')
    q = raw_mean_upper/raw_bound
    S = [[0]*(p+1) for _ in range(p+1)]
    S[0][0] = 1
    for n in range(1, p+1):
        for k in range(1, n+1):
            S[n][k] = S[n-1][k-1]+k*S[n-1][k]
    falling = [1]
    for k in range(1, p+1):
        falling.append(falling[-1]*(v-k+1) if k <= v else 0)
    moments = [Q(1)]
    for i in range(1, p+1):
        raw = (raw_bound/v)**i*sum(S[i][k]*falling[k]*q**k for k in range(i+1))
        moments.append(min(Q(1), (raw+excess_upper)/(1+excess_upper)))
    return moments


def weighted_exit(profile, witness, eta):
    data = tax_data(profile, witness)
    p, h, v, c, b, m = (witness['p'], witness['log_shift'], data['v'],
                         data['c'], data['b'], data['m'])
    options = witness['weighted']
    mean_key = ('raw_mean_upper' if witness['uniform_method'] == 'log-moments'
                else 'mean_upper')
    q, amin, amax, D, K = (Q(options[k]) for k in
        (mean_key, 'A_lower', 'A_upper', 'ambient_log_lower', 'floor_log_lower'))
    E.need(0 < q <= 1 and 0 < amin <= amax and D > 0 and K > 0,
           'weighted guard domain')
    logc = E.log_bounds(c)
    A = E.scale(E.divide(E.log_bounds(2), logc), Q(h, v))
    E.need(amin <= A[0] and A[1] <= amax, 'normalized log shift enclosure')
    E.need(D <= E.divide(E.log_bounds(m), logc)[0], 'ambient log ratio')
    E.need(K <= E.divide(E.log_bounds(b), logc)[0], 'target log ratio')
    P, t = data['P'], data['t']
    log_moment = (Q(0), Q(0))
    for rank, count in P.items():
        log_moment = E.add(log_moment,
                           E.scale(E.mul(E.power(rank, t), E.log_bounds(rank)), count))
    raw_mean = E.divide(log_moment, E.mul(data['paid'], logc))
    # Full completion paid charge is needed here; the net completion tax
    # subtracts new target credit and cannot bound paid log moments.
    full_excess = E.add(data['original_tax'], E.scale(E.ipow(data['delta'], v), 2))
    relative_excess = E.divide(full_excess, E.ipow(data['alpha'], v))
    mean = E.add(raw_mean, relative_excess)
    if witness['uniform_method'] == 'log-moments':
        raw_bound = Q(options['raw_log_bound'])
        excess_upper = Q(options['paid_excess_upper'])
        E.need(raw_bound > 0 and excess_upper > 0, 'concentration guard domain')
        E.need(raw_mean[1] < q, 'raw paid log mean')
        E.need(max(P)**raw_bound.denominator <= c**raw_bound.numerator,
               'raw paid log support')
        E.need(relative_excess[1] < excess_upper, 'full paid mass perturbation')
        moments = concentrated_moments(p, v, q, raw_bound, excess_upper)
        ratio, degree, num, den = moment_coefficients(p, moments, amax, amin+D, K)
        moment_details = {'raw_log_bound': str(raw_bound),
                          'paid_excess_upper': str(excess_upper),
                          'log_moment_upper_bounds': [str(x) for x in moments]}
    else:
        E.need(mean[1] < q, 'completed paid log mean')
        ratio, degree, num, den = weighted_coefficients(p, q, amax, amin+D, K)
        moment_details = {}
    E.need(ratio < eta[0], 'all weighted exit polynomial coefficients below capacity')
    return {mean_key: str(q), **moment_details,
            'raw_normalized_log_mean': E.display(raw_mean),
            'full_paid_relative_excess': E.display(relative_excess),
            'completed_normalized_log_mean_upper': E.display(mean),
            'A': E.display(A), 'A_lower': str(amin), 'A_upper': str(amax),
            'ambient_log_lower': str(D), 'floor_log_lower': str(K),
            'coefficient_ratio_max': E.display((ratio, ratio)),
            'maximizing_coefficient': degree,
            'numerator_coefficients': [str(x) for x in num],
            'denominator_coefficients': [str(x) for x in den]}


def uniform(profile, witness):
    """Shifted-log induction, with exact integer-grid final-rank search."""
    T = histogram(profile['targets'])
    m = max(T)
    C, kappa = Q(witness['saving']), Q(witness['kappa'])
    t = 1-C
    v, c, b = (witness[k] for k in ('v', 'cutoff', 'floor'))
    p, h = witness['p'], witness.get('log_shift', 1)
    E.need(type(p) is int and p > 0 and type(h) is int and h > 0,
           'positive integer logarithm power and shift')
    E.need(0 < kappa < C < 1, 'uniform exponent domain')
    eta = E.scale(E.ipow(E.power(m, -C), v), t)
    method = witness.get('uniform_method', 'shifted')
    details = {}
    if method == 'shifted':
        theta = Q(witness['theta'])
        E.need(0 < theta < 1, 'theta domain')
        a, d = theta.numerator, theta.denominator
        E.need(c**d < b**a, 'theta above actual separation exponent')
        E.need(2**(h*(d-a))*c**(v*d) <= m**(v*a), 'shifted logarithm guard')
        E.need(theta**p < eta[0], 'exit contraction below complement capacity')
        details['theta'] = str(theta)
    elif method in ('weighted', 'log-moments'):
        details['weighted_exit'] = weighted_exit(profile, witness, eta)
    else:
        raise ValueError('unknown uniform certificate method')
    log_m = E.scale(E.divide(E.log_bounds(m), E.log_bounds(2)), v)
    base_factor = E.ipow(E.add((Q(1),)*2, E.scale(log_m, Q(1, h))), p)
    base_cost = E.ipow(E.power(m, C), v)
    E.need(base_cost[1] < base_factor[0], 'entire ordinary base range fits')
    gap = (C-kappa)/7
    step, gain = gap.denominator, gap.numerator

    def passes(j):
        H = step*j
        # (1+H/h)^p < 2^(gap*H), with no transcendental evaluation.
        return (h+H)**p < h**p * 2**(gain*j)

    low, high = 0, 1
    while not passes(high):
        low, high = high, 2*high
        E.need(high.bit_length() < 40, 'bounded final-rank grid search')
    while high-low > 1:
        mid = (low+high)//2
        if passes(mid):
            high = mid
        else:
            low = mid
    H = step*high
    E.need(passes(high) and (high == 1 or not passes(high-1)),
           'passing grid point and preceding failure')
    # Above p/gap/ln(2), p*ln(1+H/h)-gap*H*ln(2) decreases.
    # ln(2)>1/2 is enough for this conservative check.
    E.need(H+h > 2*p/gap, 'decreasing final rank comparison')
    E.need(Q(H) > log_m[1], 'uniform rank beyond ordinary base')
    return {'kappa': str(kappa), 'gap': str(gap), 'method': method, **details,
            'uniform_saving': str(C-gap),
            'p': p, 'log_shift': h, 'eta': E.display(eta),
            'ordinary_base_cost': E.display(base_cost),
            'ordinary_base_factor': E.display(base_factor),
            'H': H, 'N': '2^'+str(H), 'grid_step': step,
            'grid_index': high, 'previous_grid_point_fails': high > 1,
            'word_materialized': False}


def certify(profile, witness):
    return {'net_tax': net_tax(profile, witness),
            'uniform': uniform(profile, witness)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', type=Path, nargs='?')
    parser.add_argument('witness', type=Path, nargs='?')
    parser.add_argument('--example', help='replay a BENCHMARKS.json example; verify.py authenticates sources')
    args = parser.parse_args()
    if args.example:
        if args.profile or args.witness:
            parser.error('choose --example or two input files')
        here = Path(__file__).resolve().parent
        cases = json.loads((here/'BENCHMARKS.json').read_text())['cases']
        matches = [case for case in cases if case['name'] == args.example]
        if len(matches) != 1:
            parser.error('unknown example')
        case = matches[0]
        profile = json.loads((here.parents[1]/case['source']).read_text())
        if case['profile_key']:
            profile = profile[case['profile_key']]
        witness = case['witness']
    else:
        if not args.profile or not args.witness:
            parser.error('provide profile.json witness.json, or --example NAME')
        profile, witness = (json.loads(path.read_text())
                            for path in (args.profile, args.witness))
    result = certify(profile, witness)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()

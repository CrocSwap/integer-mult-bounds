#!/usr/bin/env python3
"""Independent application corroboration; no compiler imports.

@CubeJerry with OpenAI Codex assistance. Apache-2.0.
Binomial mixing and Newton differences check exact rational coefficients.
Decimal calculations only corroborate the separate rigorous interval proof.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import argparse
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def binomial_moments(v, degree, bound, mean, excess):
    probability = mean / bound
    weights = [(1-probability)**v]
    for j in range(v):
        weights.append(weights[-1]*F(v-j, j+1)*probability/(1-probability))
    need(sum(weights) == 1, 'exact probability mass')
    raw = [F(0)]*(degree+1)
    for j, weight in enumerate(weights):
        value = F(1)
        for i in range(degree+1):
            raw[i] += weight*value
            value *= bound*F(j, v)
    return [F(1)]+[min(F(1), (x+excess)/(1+excess)) for x in raw[1:]]


def newton(values):
    result = []
    while values:
        result.append(values[0]/factorial(len(result)))
        values = [b-a for a, b in zip(values, values[1:])]
    return result


def convolution_polynomial(moments, shift):
    degree = len(moments)-1
    state = [shift**i for i in range(degree+1)]
    evaluations = []
    # At integer G, the polynomial contains G+1 formal iid variables.
    for _ in range(degree+1):
        state = [sum(F(comb(i, j))*state[i-j]*moments[j]
                     for j in range(i+1)) for i in range(degree+1)]
        evaluations.append(state[degree])
    return newton(evaluations)


def exact_checks(receipt, witness):
    opts = witness['weighted']
    degree, v = witness['p'], witness['v']
    mu = binomial_moments(v, degree, F(opts['raw_log_bound']),
                          F(opts['raw_mean_upper']), F(opts['paid_excess_upper']))
    reported = receipt['certificate']['uniform']['weighted_exit']
    need(mu == list(map(F, reported['log_moment_upper_bounds'])), 'binomial moments')
    numerator = convolution_polynomial(mu, F(opts['A_upper']))
    intercept = F(opts['A_lower'])+F(opts['ambient_log_lower'])
    slope = F(opts['floor_log_lower'])
    denominator = newton([(intercept+slope*g)**degree for g in range(degree+1)])
    need(numerator == list(map(F, reported['numerator_coefficients'])), 'Newton numerators')
    need(denominator == list(map(F, reported['denominator_coefficients'])), 'Newton denominators')
    need(all(x > 0 for x in denominator), 'positive denominators')
    ratios = [a/b for a, b in zip(numerator, denominator)]
    need(max(ratios) < F(272, 100000), 'exact capacity guard')
    need(ratios.index(max(ratios)) == reported['maximizing_coefficient'] == 37,
         'maximizing coefficient')
    h, H, step, j = 5550, 1449000000000, 1400000000, 1035
    need((h+H)**degree < h**degree*2**j, 'integer rank bound')
    need((h+H-step)**degree >= h**degree*2**(j-1), 'preceding grid fails')
    need(F(65807000000000, H) == F(9401, 207), 'reduction factor')
    bad = numerator.copy()
    bad[-1] += 1
    need(bad != list(map(F, reported['numerator_coefficients'])), 'coefficient mutation control')
    need(convolution_polynomial(mu, F(opts['A_lower'])) != numerator,
         'reversed shift guard control')
    return {'moments': len(mu), 'numerators': len(numerator),
            'denominators': len(denominator), 'maximizing_coefficient': 37,
            'grid_index': j, 'reduction_factor': '9401/207'}


def decimal_checks(receipt, witness):
    with localcontext() as ctx:
        ctx.prec = 100
        D = Decimal
        def rational(value):
            x = F(value)
            return D(x.numerator)/D(x.denominator)
        def power(x, exponent):
            return (D(x).ln()*exponent).exp()
        C, u = rational(witness['saving']), rational(witness['u'])
        t, v, c, b = 1-C, witness['v'], witness['cutoff'], witness['floor']
        P = {int(k): int(n) for k, n in receipt['invoice']['paid'].items()}
        T = {int(k): int(n) for k, n in receipt['invoice']['targets'].items()}
        def moment(hist, exponent):
            return sum(D(n)*power(rank, exponent) for rank, n in hist.items())
        pt, tt = moment(P, t), moment(T, t)
        h0 = C*power(t, t/C)
        q = min(max(C/u, h0), power(2, u)*(C/u)*power(1-C/u, (u-C)/C))
        alpha = pt/tt
        gamma = moment(P, t+u)/(power(c, u)*tt)
        delta = D(sum(T.values())*b)/(power(c, C)*tt)
        epsilon = D(sum(T.values()))*power(c, t)/tt
        delta0 = D(sum(T.values()))*power(b, t)/tt
        charge = alpha**v+q*gamma**v+delta**v+2*h0*epsilon**v-delta0**v
        relative = (q*gamma**v+2*delta**v)/alpha**v
        mean = sum(D(n)*power(r, t)*D(r).ln() for r, n in P.items())/(pt*D(c).ln())
        eta = t*power(max(T), -v*C)
        cert = receipt['certificate']
        pairs = [(charge, cert['net_tax']['normalized_net_charge']),
                 (q, cert['net_tax']['splitting_coefficient']),
                 (relative, cert['uniform']['weighted_exit']['full_paid_relative_excess']),
                 (mean, cert['uniform']['weighted_exit']['raw_normalized_log_mean']),
                 (eta, cert['uniform']['eta'])]
        for value, bounds in pairs:
            need(D(bounds['lower']) <= value <= D(bounds['upper']), 'Decimal interval agreement')
        need(charge < 1 and relative < D('.000001') and mean < D('.871') and eta > D('.00315'),
             'independent arithmetic guards')
        smaller = alpha**369+q*gamma**369+delta**369+2*h0*epsilon**369-delta0**369
        need(smaller > 1, 'smaller product rejected')
        return {'precision': 100, 'interval_comparisons': len(pairs),
                'net_charge': str(charge), 'paid_relative_excess': str(relative),
                'scope': 'Numerical corroboration, not a rigorous interval certificate.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', nargs='?', type=Path, default=Path(__file__).resolve().parent)
    package = parser.parse_args().package
    receipt = json.loads((package/'RESULT.json').read_bytes())
    witness = json.loads((package/'WITNESS.json').read_bytes())
    print(json.dumps({'marker': 'PASS_INDEPENDENT_SELECTED_COMPILER_ORACLE',
                      'exact': exact_checks(receipt, witness),
                      'decimal': decimal_checks(receipt, witness)}, sort_keys=True))


if __name__ == '__main__':
    main()

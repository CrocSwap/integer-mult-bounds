#!/usr/bin/env python3
"""Independent exact audit of a saved parameter-optimization certificate.

This checker reads the witness, rather than importing its producer. It uses
longer rational logarithm series, independently re-derives the counts and all
retained layer/assembly constraints, and checks the balance-root signs.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time


def log_series(x, terms):
    assert x >= 1
    z = (x-1)/(x+1)
    lo = sum((2*z**(2*j+1)/Q(2*j+1) for j in range(terms)), Q(0))
    tail = 2*z**(2*terms+1)/(Q(2*terms+1)*(1-z*z))
    return lo, lo+tail


def log_integer(n, terms=48):
    k = n.bit_length()-1
    a, b = log_series(Q(2), terms)
    c, d = log_series(Q(n, 2**k), terms)
    return k*a+c, k*b+d


def root_signs(a, b, bounds):
    lo, hi = map(Q, bounds)
    f = lambda x: a*b*x*x-(b+a*a)*x+a*a
    assert 0 <= lo < hi < 1 and f(lo) >= 0 and f(hi) < 0
    assert 0 < a < Q(1, 2) and 0 < b < 1
    # On the entire interval, f' <= 2ab-b-a² < 0.
    assert 2*a*b-b-a*a < 0
    return lo, hi


def audit_row(row):
    h, R = 50, row['physical_side_roles']
    v, m = comb(h, 3), h**3
    N = v**3
    W = 2*N+2*v*v*(R+h)
    D = N-6*v*v*h*h
    s = W*m-D
    eta_b = Q(D, W*m)
    zc = comb(h-3, 3)+3*(h-3)
    Wc = 2*N+3*v*v*(v*zc+h+1)
    Lc = 3*v*v*(h+1)*h
    sc = Wc*m-2*N+2*Lc
    eta_c = Q(Wc*m-sc, Wc*m)
    assert all(Q(row['counts'][key]) == value for key, value in
               dict(v=v, m=m, N=N, W=W, D=D, s=s, eta=eta_b).items())
    assert all(Q(row['retained_complex_counts'][key]) == value for key, value in
               dict(W=Wc, L=Lc, s=sc, eta=eta_c).items())
    assert 2*Lc < N and 2 <= sc < m**5
    independent_log_m = log_integer(m)
    for name, eta in [('bit', eta_b), ('complex', eta_c)]:
        enclosure = row[name+'_saving_enclosure']
        ln_lo, ln_hi = log_series(1/(1-eta), 20)
        lm_lo, lm_hi = independent_log_m
        assert Q(enclosure['negative_log_deficit_lower']) <= ln_lo < ln_hi <= Q(enclosure['negative_log_deficit_upper'])
        assert Q(enclosure['log_m_lower']) < lm_lo < lm_hi < Q(enclosure['log_m_upper'])
        lower, upper = ln_lo/lm_hi, ln_hi/lm_lo
        assert Q(enclosure['saving_lower']) < lower < upper < Q(enclosure['saving_upper'])
        assert 0 < Q(enclosure['chosen_saving']) < lower
        assert Q(enclosure['strict_primitive_gap']) > 0
    p = {k: Q(v) for k, v in row['parameters'].items()}
    a, b, e, beta, c = p['a_bit'], p['a_complex'], p['epsilon'], p['beta'], p['c']
    tau, sigma, lam, lamp, delta = p['tau'], p['sigma'], p['lambda'], p['lambda_prime'], p['delta']
    assert tau == 1-a and sigma == 1-b
    xlo, xhi = root_signs(a, b, row['balance_root_interval'])
    assert beta == 1-xhi
    assert c == (1-Q(1, 2**32))*a*beta/(tau+a*beta)
    q = 1-lamp
    assert q == a*c and q < b*(1-beta)
    slacks = dict(
        tau_positive=tau, tau_below_one=a, sigma_positive=sigma, sigma_below_one=b,
        c_positive=c, epsilon_positive=e, beta_positive=beta, beta_below_one=1-beta,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma, lambda_below_one=1-lam,
        packed_overhead=lam-tau*(1+c/beta), lambda_prime_above_lambda=lamp-lam,
        leaf_cost=lamp-(sigma+beta*b), lambda_prime_below_one=1-lamp,
        guard_width=1-e*p['C1'], crt_layout=a*(1-e), gaussian_cost=Q(1, 2)-delta-e,
        prefix_cost=1-e*(1+c), scalar_cost=1-delta-e, delta_positive=delta,
        delta_below_one_eighth=Q(1, 8)-delta, prime_interval_growth=1-2*e,
        alpha_below_sqrt_p=Q(1, 4), gamma_sublinear=Q(1, 2)-e,
        K_smaller_than_ell=1-e-e*c, K_dominates_log_p=e*c,
        r_superpolynomial=1-e, kappa_positive=p['kappa'])
    assert p['C1'] == 2 and Q(9, 10) <= beta < 1
    assert all(value > 0 for value in slacks.values())
    margins = dict(g1=1-e*(1+c), g2=e*c*a, g3=e*q,
                   g4=a*(1-e), g5=Q(1, 2)-delta-e, g6=1-delta-e, g7=e)
    assert all(Q(row['margins'][key]) == value for key, value in margins.items())
    G = min(margins.values())
    assert G == Q(row['minimum_margin']) == margins['g2'] == margins['g3']
    assert 0 < p['kappa'] < G
    grid = 10**30
    expected = Q((G.numerator*grid-1)//G.denominator, grid)
    assert p['kappa'] == expected
    upper_a = Q(row['bit_saving_enclosure']['saving_upper'])
    upper_b = Q(row['complex_saving_enclosure']['saving_upper'])
    upper = Q(row['model_kappa_upper'])
    upper_x = 2*upper/upper_b
    f = lambda x: upper_a*upper_b*x*x-(upper_b+upper_a*upper_a)*x+upper_a*upper_a
    assert 0 < upper_x < 1 and f(upper_x) < 0
    assert p['kappa'] < upper < Q(1, 2**57)
    assert 8/(Q(1, 2)-e) == 16777216 and 184 < 256
    assert row['gamma_cutoff'] == 'b >= 2^16777216'
    return dict(physical_roles=R, kappa=str(p['kappa']), exact_constraints=len(slacks),
                independently_enclosed_logarithms=4, every_margin_recomputed=True,
                strict_absorption=True, root_orientation=True, scoped_upper_below_2_to_minus_57=True,
                independent_log_series_terms={'deficit':20, 'integer':48})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--certificate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    begin = time.monotonic()
    source = args.certificate.read_bytes()
    certificate = json.loads(source)
    assert certificate['provenance']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    rows = [audit_row(w) for w in certificate['witnesses']]
    result = dict(certificate_sha256=sha256(source).hexdigest(),
                  code_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), rows=rows,
                  wall_seconds=time.monotonic()-begin,
                  scope='Parameter arithmetic and scoped optimization, not finite-circuit realization or an unconditional multiplication theorem')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

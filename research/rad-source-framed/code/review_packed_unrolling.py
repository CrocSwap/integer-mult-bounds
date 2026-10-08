#!/usr/bin/env python3
"""Independent growing-geometric recurrence and composed parameter audit.

The direct controls execute integer recurrences with genuine stopped leaves,
not just the geometric identity used by the producer. The analytic all-size
proof and fixed-tape interfaces are stated in the companion report.
"""

import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import time

from review_asymmetric_motif import counts, independent_saving
from review_parameter_audit import root_signs


def ceiling(x):
    return -(-x.numerator//x.denominator)


def stopped_recurrences():
    # m=64, tau=1/2, sigma=2/3, beta=1/3, c=1/6.
    # d=64^(6k), K=64^k, and every overhead sqrt(K*e) is integral.
    # The normalized internal/leaf exponents are 25/36 and 7/9.
    checked, internal, small, strict_lower_examples = 0, 0, 0, 0
    examples = []
    for k in range(1, 13):
        threshold = 64**(2*k)
        for n in range(6*k+1):
            e = 64**n
            for branching in (12, 16):
                if e < threshold:
                    direct, depth, leaf = e, 0, e
                    assert direct <= 2**(28*k)
                    small += 1
                else:
                    depth = n-2*k+1
                    leaf = e//64**depth
                    assert threshold//64 <= leaf < threshold
                    # Independently run the bottom-up recurrence.
                    direct = leaf
                    for j in reversed(range(depth)):
                        node = e//64**j
                        overhead = 2**(3*(k+n-j))
                        assert overhead*overhead == 64**k*node
                        direct = branching*direct+overhead+1
                    exact_sum = (branching**depth*leaf
                                 +sum(branching**j*(2**(3*(k+n-j))+1)
                                      for j in range(depth)))
                    assert direct == exact_sum
                    # Bound using m^sigma=16, including constant overhead.
                    main = sum(16**j*2**(3*(k+n-j)) for j in range(depth))
                    constant = sum(16**j for j in range(depth))
                    leaves = 16**depth*leaf
                    assert main == 2**(3*(k+n))*(2**depth-1)
                    assert main < 2*2**(k+4*n) <= 2*2**(25*k)
                    assert constant <= 2**(25*k)
                    assert leaves == 2**(4*n+4*k-2) <= Q(2**(28*k), 4)
                    assert direct <= 3*2**(25*k)+Q(2**(28*k), 4)
                    # At the first internal node the leaf is smaller by m,
                    # so using u <= d^beta for a negative exponent reverses
                    # the needed inequality by the factor m^(sigma-tau)=2.
                    if n == 2*k:
                        assert leaf == threshold//64
                        assert Q(2, 2**(2*k)) == Q(1, 2**(2*k-1))
                        strict_lower_examples += 1
                    internal += 1
                    if n == 6*k and branching == 16:
                        examples.append(dict(k=k, depth=depth,
                                             exact_normalized_cost=str(direct),
                                             leaf_size=str(leaf)))
                checked += 1
    assert checked == internal+small
    return dict(complete_stopped_recurrences=checked, internal_pieces=internal,
                individually_executed_pieces=small,
                leaf_lower_bound_orientation_controls=strict_lower_examples,
                branching_factors=[12, 16],
                fixed_parameters=dict(m=64, tau='1/2', sigma='2/3', beta='1/3', c='1/6'),
                internal_exponent='25/36', leaf_exponent='7/9', examples=examples)


def finite_counts(raw):
    if 'p' in raw:
        result = counts(raw['p'], raw['q'], raw['outer_side_roles'], raw['middle_side_roles'])
    else:
        h, roles = raw['h'], raw['side_roles']
        v, m = comb(h, 3), h**3
        n = v**3
        w = 2*n+2*v*v*(roles+h)
        loss = 3*v*v*h*h
        result = dict(v=v, m=m, N=n, W=w, L=loss, D=n-2*loss,
                      s=w*m-n+2*loss, eta=Q(n-2*loss, w*m))
    assert all(Q(raw[key]) == result[key] for key in ('N', 'm', 'W', 'L', 'D', 's', 'eta'))
    assert 0 < result['D'] and 2 <= result['s'] < result['m']**5
    return result


def audit(row):
    n = finite_counts(row['bit_counts'])
    complex_ = row['complex_counts']
    v, m = comb(50, 3), 125000
    N = v**3
    W = 2*N+3*v*v*(v*(comb(47, 3)+141)+51)
    L = 3*v*v*51*50
    s = W*m-2*N+2*L
    eta = Q(2*N-2*L, W*m)
    for key, value in dict(ground=50, N=N, m=m, W=W, L=L, s=s, eta=eta).items():
        assert Q(complex_[key]) == value
    for name, fraction, radix in [('bit', n['eta'], n['m']), ('complex', eta, m)]:
        lo, hi = independent_saving(fraction, radix)
        enclosure = row[name+'_saving_enclosure']
        assert Q(enclosure['saving_lower']) < lo < hi < Q(enclosure['saving_upper'])
        assert 0 < Q(enclosure['chosen_saving']) < lo
    p = {key: Q(value) for key, value in row['parameters'].items()}
    a, b = p['a_bit'], p['a_complex']
    tau, sigma, beta, c, lam, lp = (p[key] for key in
                                   ('tau', 'sigma', 'beta', 'c', 'lambda', 'lambda_prime'))
    eps, r, delta, zeta = (p[key] for key in
                           ('epsilon', 'alpha_squared_power', 'delta', 'zeta'))
    assert tau == 1-a and sigma == 1-b and 0 < b < a < Q(1, 32)
    x = a*a/(b*tau+a*a)
    assert beta == 1-x
    cstar = a*(1-x)+b*x
    assert cstar == a*b/(b*tau+a*a) and a*cstar == b*x
    assert c == cstar*(1-Q(1, 2**32)) and lp == 1-a*c
    internal = sigma+beta*(tau-sigma)+tau*c
    leaf = sigma+beta*(1-sigma)
    assert Q(row['internal_exponent']) == internal
    assert Q(row['leaf_exponent']) == leaf
    assert lam == (lp+max(sigma, internal))/2
    B = s+64*(W+m+1)**3
    assert zeta == Q(1, 2**30) and p['C1'] == 5-4*beta+zeta
    assert eps == (1-Q(1, 2**20))/p['C1']
    assert r == (1-eps)/2 and delta == r/8
    assert p['C0'] == 32*m*B*B*(1+1/zeta)
    assert 9*(1+1/zeta)+18 < 32*(1+1/zeta)
    slacks = dict(tau=tau, sigma=sigma, sigma_above_tau=sigma-tau,
                  beta=beta, beta_below_one=1-beta, c=c,
                  lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
                  internal_bound=lam-internal, lambda_prime_above_lambda=lp-lam,
                  leaf_bound=lp-leaf, lambda_prime_below_one=1-lp,
                  guard=1-eps*p['C1'], prefix=1-eps*(1+c),
                  local_inverse=1-eps-delta, boundary_inverse=r-delta,
                  gamma=1-eps-r, cell_separation=eps-(1-r)/2,
                  alpha_power=r, alpha_below_sqrt_p=1-r,
                  primes_and_lines=1-eps, K_smaller_than_axis=1-eps-eps*c,
                  K_dominates_log_p=eps*c, delta=delta, delta_below_eighth=Q(1, 8)-delta,
                  kappa=p['kappa'])
    assert all(value > 0 for value in slacks.values())
    margins = dict(g1=1-eps*(1+c), g2=eps*a*c, g3=eps*(1-lp),
                   g4=a*(1-eps), g5=min(1-eps-delta, r-delta),
                   g6=1-eps-delta, g7=eps)
    assert all(Q(row['margins'][key]) == value for key, value in margins.items())
    G = min(margins.values())
    assert G == margins['g2'] == margins['g3'] == Q(row['minimum_margin'])
    assert 0 < p['kappa'] < G
    assert p['kappa'] == Q((G.numerator*10**30-1)//G.denominator, 10**30)
    au, bu = (Q(row[name+'_saving_enclosure']['saving_upper']) for name in ('bit', 'complex'))
    upper = au*au*bu/(bu*(1-au)+5*au*au)
    assert Q(row['model_upper']) == upper > p['kappa']
    assert a*a*b/(b*tau+5*a*a) == a*cstar/(1+4*x)
    assert 2*a-a*a > 0  # Cleared numerator of dU/da at fixed b.
    k = ceiling(1/r)
    cutoffs = dict(gamma=ceiling(7/(1-eps-r)), logarithmic_alpha=16*k*k+1,
                   full_guard=ceiling(Q((2*ceiling(p['C0'])).bit_length())/(1-eps*p['C1'])),
                   partial_cell=ceiling(9/(eps-(1-r)/2)))
    assert row['log2_b_cutoffs'] == cutoffs
    assert row['common_log2_b_cutoff'] == max(cutoffs.values())
    _, oldhi = root_signs(a, b, row['old_per_node_bound']['balance_root_interval'])
    oldbeta = 1-oldhi
    oldc = a*oldbeta/(tau+a*oldbeta)*(1-Q(1, 2**32))
    oldeps = (1-Q(1, 2**20))/(5-4*oldbeta+zeta)
    oldG = oldeps*a*oldc
    oldkappa = Q((oldG.numerator*10**30-1)//oldG.denominator, 10**30)
    assert Q(row['old_per_node_bound']['minimum_margin']) == oldG < G
    assert Q(row['old_per_node_bound']['kappa']) == oldkappa < p['kappa']
    assert Q(row['strict_improvement_factor']) == p['kappa']/oldkappa > 1
    oldhyp = lp-tau*(1+c/beta)
    assert Q(row['old_per_node_hypothesis_gap']) == oldhyp < 0
    return dict(name=row['name'], independent_strict_conditions=len(slacks),
                kappa=str(p['kappa']), exact_balance_and_cutoffs=True,
                independent_log_enclosures=True, old_per_node_premise_actually_fails=True,
                exact_improvement_factor=str(p['kappa']/oldkappa),
                cutoffs=cutoffs, conditional_original_interfaces=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--certificate', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    started = time.monotonic()
    raw = args.certificate.read_bytes()
    data = json.loads(raw)
    assert data['provenance']['commit'] == 'bcd4ebde8692383539f8a48734e5fbf3a18a32c2'
    result = dict(input_sha256=sha256(raw).hexdigest(),
                  source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  direct_stopped_recurrences=stopped_recurrences(),
                  rows=[audit(row) for row in data['witnesses']],
                  wall_seconds=time.monotonic()-started,
                  scope='Independent exact recurrence controls and strict composed arithmetic; all-size argument and unchanged tape/guard interfaces in companion report')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS', result['direct_stopped_recurrences']['complete_stopped_recurrences'],
          'direct stopped recurrences and', len(result['rows']), 'composed arithmetic rows')


if __name__ == '__main__':
    main()

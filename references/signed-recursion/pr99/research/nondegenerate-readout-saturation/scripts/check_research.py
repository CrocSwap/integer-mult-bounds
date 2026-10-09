#!/usr/bin/env python3
"""Independent checks of the pinned main witness; no upstream code imported.

Checks arithmetic and small algebraic mechanisms, not the complete theorem.
Log/exp bounds use Fraction arithmetic and explicit positive-series tails.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from math import comb, factorial, log, exp, log2
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / 'sources/crocswap/research/matrix-exponent-synthesis/candidate/arithmetic.json'


def require(test, message):
    if not test:
        raise ValueError(message)


def log_small(x, terms=40):
    require(1 <= x <= 2, 'log range reduction')
    z = (x - 1) / (x + 1)
    lo = sum((2*z**(2*j+1)/Q(2*j+1) for j in range(terms)), Q(0))
    tail = 2*z**(2*terms+1)/Q(2*terms+1)/(1-z*z)
    return lo, lo+tail


def log_interval(x):
    x, k = Q(x), 0
    require(x >= 1, 'log input')
    while x > 2:
        x /= 2
        k += 1
    a, b = log_small(x)
    c, d = log_small(Q(2))
    return a+k*c, b+k*d


def exp_interval(lo, hi, degree=10):
    require(0 <= lo <= hi < 1, 'small exponential input')
    lower = sum((lo**j/Q(factorial(j)) for j in range(degree+1)), Q(0))
    upper = sum((hi**j/Q(factorial(j)) for j in range(degree+1)), Q(0))
    # Every ratio after the first omitted term is at most hi/(degree+2).
    upper += hi**(degree+1)/Q(factorial(degree+1))/(1-hi/Q(degree+2))
    return lower, upper


def moment_interval(profile, saving):
    m, W = profile['m'], profile['W']
    low = high = Q(0)
    for t, count in profile['child_multiplicities'].items():
        t = int(t)
        a, b = log_interval(Q(m, t))
        c, d = exp_interval(saving*a, saving*b)
        weight = Q(count*t, m*W)
        low += weight*c
        high += weight*d
    return low, high


def check_profile(p):
    m, W, N, L = (p[k] for k in ('m', 'W', 'N', 'L'))
    axes = p['axes']
    require(m == axes[0]['h']*axes[1]['h'], 'ambient dimension')
    require(N == comb(23, 3)*comb(25, 3), 'source count')
    require(W == 2*N + 2300*axes[0]['R'] + 1771*axes[1]['R'], 'role width')
    require(L == 2300*23*22 + 1771*25*24, 'copied-center loss')
    total = Counter()
    for part in p['parts'].values():
        total.update({int(t): n for t, n in part.items()})
    require(total == Counter({int(t): n for t, n in p['child_multiplicities'].items()}),
            'complete component list')
    require(all(0 < t < m and n > 0 for t, n in total.items()), 'strict children')
    rank = sum(t*n for t, n in total.items())
    require(rank == p['total_rank'] == m*W-N+L, 'complete rank ledger')
    require(m*W-rank == p['deficit'] == N-L, 'deficit')
    require(max(total) == p['maxchild'], 'largest child')
    for axis in axes:
        h, R = axis['h'], axis['R']
        require(sum(i*n for i, n in enumerate(axis['blocks'])) == h*R+h*(h-1),
                'paid local rank')
    return dict(m=m, W=W, rank=rank, deficit=N-L,
                relative_deficit=float(Q(N-L, m*W)), largest_child=max(total))


def check_assembly(cert):
    bridge = cert['finite_bridge']
    coefficient = 0
    for name in ('bit', 'complex'):
        axis = bridge[name]
        m, W, child = (axis[k] for k in ('m', 'W', 'maxchild'))
        degree = 1
        while m**degree <= 2*child**degree:
            degree += 1
        require(degree == axis['halving_degree'], 'depth to halve')
        require(W.bit_length() == axis['wire_bits'], 'wire descriptor bits')
        coefficient += degree*W.bit_length()
    rowgap = bridge['rows']['degree']-Q(51, 25)*coefficient
    require(coefficient == bridge['rows']['coefficient'], 'product row stock')
    require(rowgap == Q(bridge['rows']['degree_gap']) > 0, 'row slack')
    cb = bridge['complex']
    W, m, s, gates = (cb[k] for k in ('W', 'm', 's', 'scalar_group_upper'))
    E = 64*(W+m+gates+1)**3
    B = s+E
    literal = 2*gates*W**2+8*s+4*W+4+32*m
    sem = dict(E=E, B=B, C0=32*m*B*B, C1=1, literal_charge=literal,
               strict_literal_gap=E-literal,
               induction_gap=2*B*(m-cb['maxchild'])-(s+E))
    require(all(Q(bridge['semantic'][k]) == v for k, v in sem.items()),
            'semantic precision constants')
    a, b = Q(cert['bit_saving']), Q(717, 10**7)
    kappa = Q(cert['kappa'])
    beta, eta = Q(1, 20), Q(cert['h_backoff'])
    tau, sigma = 1-a, 1-b
    q = a*(1-2*eta)
    c, epsilon = q+eta/4, (1-eta)/(1+q)
    lam, lp = (tau+1-q)/2, 1-q
    g = epsilon*q
    r, delta = (g+1-epsilon)/2, eta/8
    internal, leaf = tau+(1-beta)*max(sigma-tau, Q(0)), sigma+beta*(1-sigma)
    params = dict(a_bit=a, a_complex=b, tau=tau, sigma=sigma, beta=beta, h=eta,
                  q=q, c=c, epsilon=epsilon, lambda_=lam, lambda_prime=lp,
                  alpha_squared_power=r, delta=delta, C0=sem['C0'], C1=1, kappa=kappa)
    margins = dict(g1=1-epsilon, g2=a, g3=g, g4=a,
                   g5=min(1-epsilon-delta, r-delta), g6=1-epsilon-delta, g7=epsilon)
    slacks = dict(a_positive=a, a_below_b=b-a, b_below_one_over32=Q(1,32)-b,
        beta_positive=beta, beta_below_one=1-beta, phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q, q_below_internal=1-internal-q, q_below_leaf=1-leaf-q,
        c_positive=c, c_below_one=1-c, q_below_reservations=c-q,
        lambda_above_tau=lam-tau, lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal, lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf, compact_reservations=lp-(1-c), lambda_prime_below_one=q,
        epsilon_positive=epsilon, epsilon_below_one=1-epsilon, guard_width=1-epsilon,
        K_geometry=1-epsilon*(1+c), K_dominates_log=epsilon*c,
        record_suffix=1-epsilon, phase_local=1-epsilon-delta, phase_boundary=r-delta,
        gamma_sublinear=1-epsilon-r, cell_above_band=epsilon-(1-r)/2,
        prime_interval_packing=1-epsilon, alpha_positive=r, alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r, delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta, short_record_fallback=epsilon-a,
        small_field_exposure=1-epsilon-g, artificial_boundary=8-epsilon+r-delta-g,
        literal_scalar_guard=Q(E-literal), row_product_gap=rowgap)
    slacks.update({k+'_above_kappa': v-kappa for k, v in margins.items()})
    for key, data in (('parameters', params), ('constraints', slacks), ('margins', margins)):
        require(set(data) == set(cert['assembly'][key]), key+' keys')
        require(all(Q(cert['assembly'][key][k]) == v for k, v in data.items()), key+' values')
    require(len(slacks) == 47 and all(v > 0 for v in slacks.values()), 'strict assembly')
    require(min(margins.values()) == g > kappa, 'absorption gap')
    return dict(constraints=47, margins={k: float(v) for k, v in margins.items()},
                kappa=float(kappa), bit_saving=float(a), complex_saving=float(b),
                epsilon=float(epsilon), backoff=str(eta), absorption_gap=float(g-kappa),
                scoped_ceiling=float(a/(1+a)), parameter_headroom=float(a/(1+a)-kappa),
                row_stock_coefficient=coefficient)


def algebra_checks():
    triples = list(combinations(range(8), 3))
    for S in triples:
        for T in triples:
            j = len(set(S)&set(T))
            require((int(j == 1)+j) % 2 == int(S == T), 'binary intersection identity')
            center = Q(j-1, 2)
            side = -center if S != T and j % 2 == 0 else Q(0)
            require(center+side == int(S == T), 'dyadic intersection identity')
    cases = 0
    for v in range(128):
        for w in range(16):
            for z in (0, 1):
                initial = v
                v1 = v+2*z*w
                w1 = w+(v1 % 2)
                v2 = v1+z*(1-2*w1)
                w2 = w1-((v2 % 2)^z)
                require(v2 == initial+z*(1-2*(initial % 2)) and w2 == w,
                        'four-update dirty parity identity')
                cases += 1
    return dict(triple_pairs=len(triples)**2, parity_cases=cases)


def main():
    cert = json.loads(CERT.read_text())
    p = cert['source_profile']
    profile = check_profile(p)
    saving = Q(cert['bit_saving'])
    lo, hi = moment_interval(p, saving)
    require(hi < 1, 'independent strict moment contraction')
    derivative = sum(n*int(t)*log(p['m']/int(t)) for t, n in p['child_multiplicities'].items())/(p['m']*p['W'])
    naive = -log(1-profile['relative_deficit'])/log(p['m'])
    report = dict(scope='Arithmetic and small algebra only; no physical word replay or end-to-end theorem proof.',
        source_commit='56b66d58297deca1d7dd130247d720e960f77a37', profile=profile,
        moment=dict(strict_gap_lower=float(1-hi), strict_gap_upper=float(1-lo),
                    enclosure_width=float(hi-lo), logarithm_terms=40, exponential_degree=10,
                    comparison_with_published_interval=bool(Q(cert['moment']['lower']) <= hi and lo <= Q(cert['moment']['upper']))),
        sensitivity=dict(derivative_at_zero=derivative,
                         first_order_root=profile['relative_deficit']/derivative,
                         unbatched_rank_only_saving=naive,
                         mixed_width_gain=float(saving)/naive),
        assembly=check_assembly(cert), algebra=algebra_checks(),
        illustrative_equal_constant_factors={str(n): exp(float(Q(cert['kappa']))*log(log2(n))) for n in (4096, 10**6, 10**12)},
        theoretical_factor_two_log2_log2_n=1/float(Q(cert['kappa'])))
    (ROOT/'notes').mkdir(exist_ok=True)
    (ROOT/'notes/independent-checks.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

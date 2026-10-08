#!/usr/bin/env python3
"""Conditional 1479/10^12 witness: faster Gaussian resampling.

The retained witness was limited by the Gaussian line maps, whose cost
O(t p^(3/2+delta) alpha) forces epsilon<1/5. Two changes remove that limit:

* Gaussian sums along a line are evaluated blockwise as chirped correlations,
  using the established integer multiplier, in O(p^(1+delta)) per output.
* The correction E of the resampling system has powers decaying like
  exp(-pi alpha^2 sigma n) after a burn-in of order 1/theta, so the Neumann
  series needs O(p/alpha^2+1/theta) terms rather than p/(alpha^2 theta).

With alpha^2 about b/(8d) the line maps cost O(d^2 p^delta) per bit, and
epsilon may approach 1/2. The bit and complex networks, compact-control
movement and guard are those of the compressed-complex witness.
"""
from fractions import Fraction as Q
from math import comb, floor, gcd
from pathlib import Path
import json

from certify import Parameters, constraints, margins, require, verify_sources
from compact_control_layer import layer_exponents
from complex_circuit import ComplexSideCircuit
from complex_network import COMPLEX_SAVING, H, counts, guard
from paired_network import BIT_SAVING
from prepare_layers import serializable

ROOT = Path(__file__).resolve().parents[1]
KAPPA = Q(1479, 10**12)
ZETA = Q(1, 10000)
# Rational enclosures 333/106 < pi < 355/113 and 693/1000 < log 2 < 6932/10000
# bound pi*log2(e)=pi/log(2) on both sides.
KAPPA0_LO = Q(333, 106)/Q(6932, 10000)
KAPPA0_HI = Q(355, 113)/Q(693, 1000)


def ceil(x):
    return -(-x.numerator//x.denominator)


def parameters():
    return Parameters(tau=1-BIT_SAVING, sigma=1-COMPLEX_SAVING,
                      epsilon=Q(49999, 100000), c=Q(9999, 10000),
                      lam=1-Q(29595, 10**13), lamp=1-Q(2959, 10**12),
                      kappa=KAPPA, beta=Q(19, 25), delta=Q(1, 10**6),
                      C1=5-4*Q(19, 25)+ZETA)


def fast_constraints(p):
    """Tight-Gaussian slacks with the Gaussian conditions of the new line maps.

    The old cost 3/4+delta+5eps/4 becomes 2eps+delta. The old conditions on
    alpha and gamma held only for alpha about (db)^(1/4); with alpha about
    (b/(8d))^(1/2), gamma<=b/4 holds by construction, alpha<sqrt(p) always,
    and alpha^2 theta_i>=1 holds eventually because 2eps<1.
    """
    s = constraints(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    for key in ('gaussian_cost', 'dimension_upper_bound', 'alpha_below_sqrt_p', 'gamma_sublinear'):
        del s[key]
    s['gaussian_cost'] = 1-p.delta-2*p.epsilon
    s['alpha_squared_theta_growth'] = 1-2*p.epsilon
    return s


def fast_margins(p):
    g = margins(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    g['g5'] = 1-p.delta-2*p.epsilon
    return g


def witness(p, n):
    g = guard(n, p.beta, ZETA)
    require(p.C1 == g['C1'], 'Guard mismatch')
    e = layer_exponents(p.tau, p.sigma, p.beta, p.c)
    slacks = fast_constraints(p)
    slacks['packed_overhead'] = p.lam-e['internal']
    slacks['reserved_axes'] = p.lamp-e['preprocessing']
    for name, slack in slacks.items(): require(slack > 0, 'Constraint failed: '+name)
    gs = fast_margins(p)
    require(min(gs.values()) > p.kappa, 'No final absorption gap')
    return dict(parameters=vars(p), guard=g, recurrence=e, constraint_slacks=slacks,
                margins=gs, minimum_margin=min(gs.values()),
                limiting_margins=[k for k, v in gs.items() if v == min(gs.values())],
                absorption_gap=min(gs.values())-p.kappa)


def witness_only():
    """Counts and parameter witness without the finite checks (for the patch)."""
    n = counts(ComplexSideCircuit(H))
    require(n['eta'] > COMPLEX_SAVING*Q(966, 100), 'Complex saving failed')
    return witness(parameters(), n)


def nearest(x):
    """Nearest integer with ties rounded up, as for q_j=floor(tj/s+1/2)."""
    return floor(x+Q(1, 2))


def step_inequality(s, t, H):
    """Exact check of c(j,h) >= Phi(j+h)-Phi(j)+sigma h^2 for 0<=j<s, 0<|h|<=H.

    c(j,h)=sigma h (sigma h+2 beta_j) and Phi(j)=sigma(beta_j^2+1/4)/theta.
    Returns the minimum exact excess, which must equal its closed form.
    """
    require(1 < s < t < 2*s and gcd(s, t) == 1, 'Need s<t<2s coprime')
    sigma = Q(t, s); theta = sigma-1
    beta = lambda j: sigma*j-nearest(sigma*j)
    phi = lambda j: sigma*(beta(j)**2+Q(1, 4))/theta
    worst = None
    for j in range(s):
        for h in range(-H, H+1):
            if not h: continue
            c = sigma*h*(sigma*h+2*beta(j))
            excess = c-(phi(j+h)-phi(j))-sigma*h*h
            y = beta(j)+h*theta; w = nearest(sigma*(j+h))-nearest(sigma*j)-h
            require(excess == sigma/theta*w*(2*y-w), 'Closed form failed')
            require(excess >= 0, 'Step inequality failed')
            require(abs(beta(j+h)) <= Q(1, 2), 'Phase outside the half interval')
            worst = excess if worst is None else min(worst, excess)
    return worst


def neumann_count(p_bits, alpha, theta):
    """n_new=ceil((p+1)/(4 alpha^2)+1/theta) and the original count ceil(p/(alpha^2 theta)).

    With L=log2(2.01)<101/100 and pi log2(e) > KAPPA0_LO, each extra power of E
    gains at least KAPPA0_LO*alpha^2-L >= 4 alpha^2 bits, and the burn-in costs at
    most KAPPA0_HI*alpha^2*(1/(4 theta)+1/2) bits.
    """
    a2 = alpha*alpha
    require(alpha >= 2 and a2*theta >= 1 and theta < 1, 'Need alpha>=2, alpha^2 theta>=1, theta<1')
    require(Q(201, 100)**100 < 2**101, 'log2(2.01)<101/100 failed')
    require(KAPPA0_LO*a2-Q(101, 100) >= 4*a2, 'Per-step decay constant failed')
    n_new = ceil(Q(p_bits+1, 4*a2)+1/theta)
    require(4*a2*n_new >= p_bits+1+KAPPA0_HI*a2*(1/(4*theta)+Q(1, 2)), 'Neumann count failed')
    n_hvdh = ceil(Q(p_bits)/(a2*theta))
    return dict(n_new=n_new, n_hvdh=n_hvdh, n=min(n_new, n_hvdh))


def application_counts(d, b):
    """Counts at given (d,b): alpha=floor(sqrt(b/(8d))), theta>1/(4d)."""
    from math import isqrt
    alpha = isqrt(b//(8*d))
    while 8*d*(alpha+1)**2 <= b: alpha += 1
    while 8*d*alpha**2 > b: alpha -= 1
    gamma = 2*d*alpha*alpha
    theta = Q(1, 4*d)
    require(gamma*4 <= b, 'gamma exceeds b/4')
    return dict(d=d, b=b, alpha=alpha, gamma=gamma, **neumann_count(6*b, alpha, theta))


def certificate():
    c = ComplexSideCircuit(H); n = counts(c)
    require(n['eta'] > COMPLEX_SAVING*Q(966, 100), 'Complex saving failed')
    p = parameters(); w = witness(p, n)
    require(Q(1, 2**30) < KAPPA < Q(1, 2**29), 'Unexpected dyadic scale')
    steps = {f'{s}/{t}': str(step_inequality(s, t, 6)) for s, t in ((7, 8), (31, 32), (61, 64), (97, 101), (251, 256))}
    samples = [application_counts(d, b) for d, b in ((8, 2**20), (64, 2**30), (1000, 2**40))]
    for x in samples: require(x['n_new'] <= 30*x['d'], 'Neumann count exceeds 30d')
    # Under the retained Gaussian margin the same networks are capped below a_b/5.
    return dict(status='CONDITIONAL 1479/10^12 WITNESS; FAST GAUSSIAN RESAMPLING; NOT FORMAL VERIFICATION',
                upstream_commit=verify_sources(), complex_counts=dict(h=n['h'], W=n['W'], s=n['s'], eta=n['eta']),
                bit_saving=BIT_SAVING, complex_saving=COMPLEX_SAVING, witness=w,
                step_inequality_minimum_excess=steps, neumann_samples=samples,
                gaussian_cost_power='2*epsilon+delta (was 3/4+delta+5*epsilon/4)',
                improvement_over_compressed_complex=KAPPA/Q(59, 10**11),
                improvement_over_compact_control=KAPPA/Q(83, 10**12),
                scoped_ceiling=dict(upper=BIT_SAVING/2, below_2_to_minus_29=BIT_SAVING/2 < Q(1, 2**29),
                    scope='g2,g3,g4 <= a_b*min(eps,1-eps); published h=50 paired bit network only.'),
                scope='Conditional on the pinned upstream interfaces, the compact-control movement and guard, '
                      'the compressed complex network, and the written fast resampling lemmas. '
                      'Exact arithmetic and finite checks are not formal verification.')


if __name__ == '__main__':
    result = serializable(certificate())
    (ROOT/'certificates/fast-gaussian.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('PASS conditional', KAPPA, '> 2^-30; minimum margin', result['witness']['minimum_margin'],
          'limiting', result['witness']['limiting_margins'])

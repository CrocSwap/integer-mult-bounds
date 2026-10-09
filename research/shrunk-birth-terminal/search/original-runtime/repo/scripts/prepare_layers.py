#!/usr/bin/env python3
"""Reusable layer estimates and complex-family screen, not a new headline bound.

The sparse-cost examples are implications of an UNPROVED primitive. They are
kept explicitly separate from estimates for the existing machine routine.
"""
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import Parameters, constraints, margins, network, require, verify_sources
from search_network import log_integer_bounds, log_ratio_bounds

ROOT = Path(__file__).resolve().parents[1]
BIT_SAVING = Q(296, 10**11)


def guard(beta, zeta=Q(1, 100), h=50):
    """Explicit guard for any fixed rational beta in (0,1); see the proof note."""
    require(0 < beta < 1 and zeta > 0, 'Need 0<beta<1 and zeta>0')
    n = network(h)
    m, s, B = n['m'], n['sc'], n['B']
    E = B-s
    require(m >= 3 and 2 <= s < m**5, 'Unverified coefficient-depth hypothesis')
    require(s*(8+E) <= 9*B*B, 'One-piece constant failed')
    C1 = 5-4*beta+zeta
    raw_C0 = max(Q(128*m*B*B), 18*m*B*B*(1+1/zeta))
    C0 = -(-raw_C0.numerator//raw_C0.denominator)
    require(9*m*B*B*(1+1/zeta)+18 <= C0, 'Whole-layer constant failed')
    return dict(h=h, m=m, s=s, E=E, B=B, beta=beta, zeta=zeta,
                C0=C0, C1=C1, one_piece_exponent=5-4*beta)


def packed_exponents(tau, sigma, beta, c, *, theta=None):
    """Sum the recurrence for either exponent ordering.

    theta=tau is the EXISTING packed bound. Any other theta is only a
    hypothetical O(V e^tau K^theta) primitive with the same remaining contract.
    """
    require(0 < tau < 1 and 0 <= sigma < 1 and 0 < beta < 1 and c > 0,
            'Invalid recurrence parameters')
    theta = tau if theta is None else theta
    require(theta >= 0, 'Negative spacing exponent is not supported')
    internal = tau+(1-beta)*max(sigma-tau, Q(0))+theta*c
    leaf = sigma+beta*(1-sigma)
    return dict(internal=internal, leaf=leaf, layer=max(internal, leaf),
                theta=theta, hypothetical=theta != tau)


def check_parameters(p, g, *, hypothetical_theta=None):
    """Check the stated extensions, without relaxing the published checker."""
    require(g == guard(g['beta'],g['zeta'],g['h']), 'Guard certificate was altered')
    require(p.beta == g['beta'] and p.C1 == g['C1'], 'Guard/parameter mismatch')
    require(1-p.tau <= BIT_SAVING, 'Preparation retains the published bit saving')
    require(1-p.sigma < complex_saving_bounds(g['h'])[0],
            'Complex exponent is not supported by the chosen motif')
    exp = packed_exponents(p.tau, p.sigma, p.beta, p.c, theta=hypothetical_theta)
    slacks = constraints(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    slacks['packed_overhead'] = p.lam-exp['internal']
    for name, slack in slacks.items():
        require(slack > 0, 'Failed preparation constraint: '+name)
    gs = margins(p, layout_model='nonadjacent', assembly_model='tight-gaussian')
    require(min(gs.values()) > p.kappa, 'No strict final margin')
    return dict(status=('HYPOTHETICAL SPARSE PRIMITIVE; NOT A MULTIPLICATION RESULT'
                        if exp['hypothetical'] else
                        'Existing packed routine; conditional preparation estimates'),
                parameters=vars(p), guard=g, recurrence=exp,
                constraint_slacks=slacks, margins=gs, minimum_margin=min(gs.values()))


def complex_saving_bounds(h):
    n = network(h)
    eta = n['eta_c']
    require(0 < eta < Q(1, 2), 'Complex deficit must be positive')
    lo, hi = log_ratio_bounds(1/(1-eta), terms=3)
    dlo, dhi = log_integer_bounds(n['m'])
    return lo/dhi, hi/dlo


def complex_search():
    # L_c<N is sufficient for the phase interface; L_c<N/2 is not needed.
    # C(h,3)>3h(h+1) iff h^2-21h-16>0, hence integer h>=22.
    bounds = {h: complex_saving_bounds(h) for h in range(22, 200)}
    winner = max(bounds, key=lambda h: bounds[h][0])
    lo, hi = bounds[winner]
    require(all(lo > b[1] for h, b in bounds.items() if h != winner),
            'Finite winner not separated')
    n200 = network(200)
    # eta_c<2/(3*z_c*m), log(m)>1; every factor increases for h>=200.
    tail = Q(2, 3*n200['zc']*n200['m']-2)
    require(log_integer_bounds(n200['m'])[0] > 1, 'Tail log denominator failed')
    require(lo > tail, 'Tail could improve the result')
    n = network(winner)
    certified = Q(418, 10**12)
    _, log_hi = log_integer_bounds(n['m'])
    require(n['eta_c'] > certified*log_hi, 'Chosen simple complex saving failed')
    require(n['Lc'] < n['N'] and 2*n['Lc'] >= n['N'],
            'Expected the complex-only admissibility range')
    require(n['sc'] < n['m']**5, 'Guard requires a different depth bound')
    fixed50 = Q(169, 10**13)
    require(network(50)['eta_c'] > fixed50*log_integer_bounds(50**3)[1],
            'Fixed-h=50 saving failed')
    return dict(status='Conditional complex interface; separate-arity integration not patched',
                winner_h=winner, admissible_integer_h_minimum=22,
                saving_lower=lo, saving_upper=hi, certified_saving=certified,
                counts={k:n[k] for k in ('h','m','v','N','Wc','sc','Lc','eta_c')},
                fixed_h50_saving=fixed50, tail_start=200, tail_upper=tail,
                finite_enclosures={str(h):dict(lower=b[0],upper=b[1]) for h,b in bounds.items()},
                scope='Original complex motif only, all integer h>=22; no shared bit positivity requirement. Written interface audit required, not a formal proof.')


def scenarios():
    a = BIT_SAVING
    epsilon = Q(199,1000)
    # The published numerical choice remains valid under the generalized proof.
    beta = Q(999,1000)
    g = guard(beta)
    existing = Parameters(1-a, 1-Q(1,10**11), epsilon, beta*a,
                          1-(1+beta)*a*a/2, 1-beta*a*a, Q(1,2**59),
                          beta=beta, delta=Q(1,10000), C1=g['C1'])
    result = {'existing_59_control':check_parameters(existing,g)}
    # These two rows assume theta=a instead of theta=tau. No such primitive
    # is supplied here. They expose exact research targets and guard budgets.
    for name,h,ac,beta,c,q,k in (
        ('hypothetical_39',50,Q(1,10**11),Q(1,100),Q(1,200),Q(95,10**13),39),
        ('hypothetical_34',25,Q(418,10**12),Q(1,5),Q(1,10),Q(3,10**10),34)):
        g = guard(beta,h=h)
        exp = packed_exponents(1-a,1-ac,beta,c,theta=a)
        lamp = 1-q
        lam = (max(1-a,1-ac,exp['internal'])+lamp)/2
        p = Parameters(1-a,1-ac,epsilon,c,lam,lamp,Q(1,2**k),
                       beta=beta,delta=Q(1,10000),C1=g['C1'])
        result[name] = check_parameters(p,g,hypothetical_theta=a)
        actual = packed_exponents(p.tau,p.sigma,p.beta,p.c)
        require(actual['internal'] > 1, 'Hypothetical target accidentally uses an existing bound')
        result[name]['existing_primitive_internal_exponent'] = actual['internal']
        result[name]['missing_hypothesis'] = 'Uniform fixed-tape O(V f^(1-a) K^a) selected-bit primitive, up to fixed powers of log(p) only, including descriptors, exceptional repair, and dirty-scratch restoration.'
    return result


def certificate():
    return dict(status='PREPARATION PASS; published headline remains conditional 2^-59',
                upstream_commit=verify_sources(), complex_family=complex_search(),
                scenarios=scenarios(),
                verification_boundary='Exact arithmetic and finite recurrence checks accompany written proofs. Sparse scenarios are unproved design targets, not certificates of new algorithms.')


def serializable(value):
    if isinstance(value,Q):
        return str(value)
    if isinstance(value,dict):
        return {k:serializable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [serializable(v) for v in value]
    return value


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/layer-preparation.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS preparation estimates; complex-family optimum h='+str(result['complex_family']['winner_h']))
    print('Published result remains 2^-59. Sparse targets 2^-39 and 2^-34 remain hypothetical.')

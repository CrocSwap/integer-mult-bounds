#!/usr/bin/env python3
"""Exact witness from aligning pair groups across common-point circuits."""
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import Parameters, certify_parameters, network, require, verify_sources
from paired_exclusion_circuit import PairedExclusionCircuit
from paired_network import guard_certificate, LOG_BOUND, COMPLEX_SAVING
from search_network import log_integer_bounds
from shared_point_circuit import SharedPointCircuit
from shared_point_network import counts

ROOT = Path(__file__).resolve().parents[1]
H = 50
BIT_SAVING = Q(305, 10**11)
KAPPA = Q(17, 2**63)


def circuit(h=H):
    require(h >= 6 and h % 2 == 0, 'The aligned pairing requires even h>=6')
    # Keep all complete global pairs together and put i's partner last.
    orders = [[j for j in range(h) if j not in (i, i ^ 1)] + [i ^ 1]
              for i in range(h)]
    return SharedPointCircuit(h, PairedExclusionCircuit(h-1), point_orders=orders)


def parameters():
    a = BIT_SAVING
    beta = Q(999, 1000)
    return Parameters(1-a, 1-COMPLEX_SAVING, Q(199, 1000), beta*a,
                      1-(1+beta)*a*a/2, 1-beta*a*a, KAPPA,
                      beta=beta, delta=Q(1, 10000), C1=2)


def certificate():
    c = circuit()
    n = counts(H, c)
    old = network(H)
    p = parameters()
    local = c.local.verify()
    symbolic = c.verify()
    frames = c.verify_frames()
    lo, hi = log_integer_bounds(n['m'])
    require(hi < LOG_BOUND, 'Logarithm enclosure failed')
    require(n['eta'] > BIT_SAVING*LOG_BOUND, 'Aligned bit saving failed')
    require(old['eta_c'] > COMPLEX_SAVING*LOG_BOUND, 'Complex saving failed')
    require(2*old['Lc'] < old['N'], 'Complex residual construction failed')
    guard = guard_certificate(beta=p.beta)
    witness = certify_parameters(p, generalized_beta=True, strict_margin=True,
                                 layout_model='nonadjacent', guard_model='stopping',
                                 assembly_model='tight-gaussian')
    require(Q(witness['minimum_margin']) == p.epsilon*p.beta*BIT_SAVING**2,
            'Wrong limiting margin')
    require(n['side_roles_per_invocation'] < 509194, 'No circuit improvement')
    # The dimension, Gaussian width, complex motif and guard are unchanged.
    gamma_exp = Q(1, 2)+Q(3, 2)*p.epsilon
    require(gamma_exp == Q(1597, 2000), 'Changed Gaussian exponent')
    require(8**2*32 < 46**2 and 184**2000 < 2**(40*403),
            'Gaussian ceiling or cutoff failed')
    a_upper = n['eta']/((1-n['eta'])*lo)
    ceiling = a_upper*a_upper/(5*(1-a_upper))
    require(ceiling < Q(1, 2**58), 'Unexpected crossing of 2^-58')
    return dict(
        status='CONDITIONAL 17*2^-63 WITNESS; aligned common-point pair groups',
        upstream_commit=verify_sources(),
        point_order_rule='increasing points except i and i^1, followed by i^1',
        bit_counts={k: str(v) for k, v in n.items()},
        complex_counts={k: str(old[k]) for k in ('h', 'v', 'm', 'N', 'Wc', 'sc', 'Lc', 'eta_c')},
        local_circuit=local, global_circuit=symbolic, frames=frames,
        bit_saving=str(BIT_SAVING), complex_saving=str(COMPLEX_SAVING),
        log_m_upper=str(LOG_BOUND), log_enclosure=[str(lo), str(hi)],
        bit_deficit_slack=str(n['eta']-BIT_SAVING*LOG_BOUND),
        complex_deficit_slack=str(old['eta_c']-COMPLEX_SAVING*LOG_BOUND),
        stopped_guard=guard,
        gaussian=dict(alpha_definition='ceil((32*d*b)^(1/4))',
                      alpha_exponent=str(Q(1, 4)+p.epsilon/4),
                      gamma_exponent=str(gamma_exp), gamma_cutoff='b>=2^40'),
        witness=witness,
        fixed_network_ceiling=dict(value=str(ceiling),
                                   strictly_below_2_to_minus_58=True,
                                   scope='This aligned graph and revised inequalities only.'),
        scope='Conditional on the retained paired frame transfer, stopped guard, '
              'tight Gaussian audit and upstream algorithmic interfaces; not a practical speedup.')


if __name__ == '__main__':
    result = certificate()
    (ROOT / 'certificates/aligned-paired-network.json').write_text(
        json.dumps(result, indent=2, sort_keys=True)+'\n', newline='\n')
    print('PASS conditional 17*2^-63; minimum', result['witness']['minimum_margin'])
    print('Side roles:', result['bit_counts']['side_roles_per_invocation'])

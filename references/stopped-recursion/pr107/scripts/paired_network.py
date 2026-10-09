#!/usr/bin/env python3
"""Conditional 2^-59 certificate: paired sums, stopped guard, tighter Gaussian width."""
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import Parameters,certify_parameters,network,require,verify_sources
from shared_point_circuit import SharedPointCircuit
from shared_point_network import counts
from paired_exclusion_circuit import PairedExclusionCircuit
from search_network import log_integer_bounds

ROOT=Path(__file__).resolve().parents[1]
H=50
BIT_SAVING=Q(296,10**11)
COMPLEX_SAVING=Q(1,10**11)
LOG_BOUND=Q(11737,1000)
KAPPA=Q(1,2**59)


def circuit(h=H):return SharedPointCircuit(h,PairedExclusionCircuit(h-1))


def parameters():
    a=BIT_SAVING;b=Q(999,1000)
    return Parameters(1-a,1-COMPLEX_SAVING,Q(199,1000),b*a,
                      1-(1+b)*a*a/2,1-b*a*a,KAPPA,beta=b,
                      delta=Q(1,10000),C1=2)


def guard_certificate(h=H,beta=Q(999,1000)):
    n=network(h);m=n['m'];s=n['sc'];E=n['B']-s;B=n['B']
    require(m>=3 and 2<=s<m**5,'The stopped guard requires 2<=s_c<m^5')
    require(Q(9,10)<=beta<1,'Stopping exponent outside proved guard range')
    depth=5-4*beta
    require(depth<=Q(7,5) and depth+Q(1,2)<2,'Insufficient guard exponent')
    require(s*(8+E)<=9*B*B,'One-piece depth constant is too small')
    C0=128*m*B*B
    require(18*m*B*B+18<=36*m*B*B<C0,'Layer depth constant is too small')
    return dict(h=h,m=m,complex_s=str(s),E=str(E),B=str(B),C0=str(C0),C1=2,
                beta=str(beta),one_piece_depth_exponent=str(depth),
                depth_with_piece_count_exponent=str(depth+Q(1,2)),
                s_below_m_fifth=True,
                scope='Exact constants for the written stopped-depth proof; coefficient depth uses the unchanged h=50 complex motif, not the new bit motif.')


def certificate():
    c=circuit();n=counts(H,c);old=network(H);p=parameters()
    local=c.local.verify();symbolic=c.verify();frames=c.verify_frames()
    lo,hi=log_integer_bounds(n['m'])
    require(hi<LOG_BOUND,'Logarithm enclosure failed')
    require(n['eta']>BIT_SAVING*LOG_BOUND,'Bit saving failed')
    require(old['eta_c']>COMPLEX_SAVING*LOG_BOUND,'Complex saving failed')
    require(2*old['Lc']<old['N'],'Complex residual construction is outside its positive-deficit range')
    guard=guard_certificate(beta=p.beta)
    # alpha=ceil((32*d*b)^(1/4)); gamma=2*d*alpha^2.
    require(8**2*32<46**2,'Gaussian ceiling constant failed')
    gamma_exp=Q(1,2)+Q(3,2)*p.epsilon
    require(gamma_exp==Q(1597,2000),'Unexpected gamma exponent')
    require(184**2000<2**(40*403),'The stated b>=2^40 cutoff failed')
    witness=certify_parameters(p,generalized_beta=True,strict_margin=True,
                layout_model='nonadjacent',guard_model='stopping',assembly_model='tight-gaussian')
    require(Q(witness['minimum_margin'])==p.epsilon*p.beta*BIT_SAVING**2,'Wrong limiting margin')
    a_upper=n['eta']/((1-n['eta'])*lo)
    ceiling=a_upper*a_upper/(5*(1-a_upper))
    require(ceiling<Q(1,2**58),'Unexpected crossing of the next dyadic target')
    return dict(status='CONDITIONAL 2^-59 WITNESS; three proof extensions supplied separately',
                upstream_commit=verify_sources(),bit_counts={k:str(v) for k,v in n.items()},
                complex_counts={k:str(old[k]) for k in ('h','v','m','N','Wc','sc','Lc','eta_c')},
                local_circuit=local,global_circuit=symbolic,frames=frames,
                bit_saving=str(BIT_SAVING),complex_saving=str(COMPLEX_SAVING),
                log_m_upper=str(LOG_BOUND),log_enclosure=[str(lo),str(hi)],
                bit_deficit_slack=str(n['eta']-BIT_SAVING*LOG_BOUND),
                complex_deficit_slack=str(old['eta_c']-COMPLEX_SAVING*LOG_BOUND),
                stopped_guard=guard,
                gaussian=dict(alpha_definition='ceil((32*d*b)^(1/4))',
                    alpha_exponent=str(Q(1,4)+p.epsilon/4),gamma_exponent=str(gamma_exp),
                    gamma_cutoff='b>=2^40',gaussian_cost_exponent=str(Q(3,4)+p.delta+Q(5,4)*p.epsilon),
                    resampling_margin='alpha^4*theta_i > 8*b > p=6*b'),
                witness=witness,
                fixed_network_ceiling=dict(value=str(ceiling),formula='a^2/(5*(1-a))',
                    strictly_below_2_to_minus_58=True,
                    scope='This bit graph and the revised Gaussian/guard inequalities only; not a bound on other networks or algorithms.'),
                scope='Conditional on the paired circuit/frame transfer, stopped-depth guard proof, tighter Gaussian setup audit, and unchanged upstream algorithmic interfaces.')


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/paired-network.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS conditional 2^-59; minimum',result['witness']['minimum_margin'])
    print('Ratio of minimum margin to kappa:',float(Q(result['witness']['minimum_margin'])/KAPPA))

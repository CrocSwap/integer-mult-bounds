"""Exact conditional assembly for the separately audited ternary bit network."""
from fractions import Fraction as Q
from pathlib import Path
import json

from certify import Parameters,constraints,margins,require
from experiments.shared_core import shared_counts

ROOT=Path(__file__).resolve().parents[1]
BIT_SAVING=Q(467,10**11)
KAPPA=Q(1,2**30)
SIDE_ROLES=20780789


def counts():return shared_counts(118755,406,29,SIDE_ROLES)


def parameters():
    return Parameters(tau=1-BIT_SAVING,sigma=1-Q(5,10**9),
        epsilon=Q(1999,10000),c=Q(1),lam=1-Q(4669,10**12),
        lamp=1-Q(4668,10**12),kappa=KAPPA,beta=Q(1,100),
        delta=Q(1,10**6),C1=Q(4961,1000))


def assembly_control(network=None):
    n=counts() if network is None else network;p=parameters()
    require(n['n']==118755 and n['r']==406 and n['d']==29 and
            n['side_roles_per_invocation']==SIDE_ROLES,'Wrong ternary network')
    require(n['saving_lower']>BIT_SAVING,'Unsupported ternary saving')
    old=json.loads((ROOT/'certificates/complex-compression.json').read_text())
    control=old['assembly_control'];oldp=control['parameters']
    require(Q(oldp['sigma'])==p.sigma and Q(oldp['beta'])==p.beta,
            'Retained complex interface changed')
    require(Q(control['guard_C1'])==p.C1==5-4*p.beta+Q(1,1000),
            'Retained precision guard changed')
    chi=p.tau+(1-p.beta)*max(p.sigma-p.tau,0)
    cs=constraints(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    cs['packed_overhead']=p.lam-chi
    cs['reserved_axes']=p.lamp-max(0,1-p.c)
    require(all(x>0 for x in cs.values()),'Ternary assembly constraint failed')
    gs=margins(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    require(min(gs.values())>p.kappa,'Ternary absorption gap failed')
    require(p.tau>p.sigma and chi==p.tau,'Wrong internal exponent branch')
    return dict(parameters=vars(p),constraint_slacks=cs,margins=gs,
        minimum_margin=min(gs.values()),absorption_gap=min(gs.values())-p.kappa,
        internal_exponent=chi,complex_counts=old['counts'],
        retained_complex_guard_C0=int(control['guard_C0']),guard_C1=p.C1,
        complex_scalar_node_charge=int(control['guard_node_charge']),
        powers=dict(d=p.epsilon,K=p.epsilon*p.c,ell=1-p.epsilon,
                    alpha=(1+p.epsilon)/4,gamma=(1+3*p.epsilon)/2,
                    prime_interval_ratio=1-2*p.epsilon,guard=p.epsilon*p.C1),
        scope='Conditional on the complete ternary construction audit and retained upstream/extensions; numerical inequalities alone are not a proof.')

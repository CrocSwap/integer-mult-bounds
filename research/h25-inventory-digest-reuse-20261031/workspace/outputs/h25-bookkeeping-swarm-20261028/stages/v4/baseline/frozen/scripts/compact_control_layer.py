#!/usr/bin/env python3
"""Exact accounting for the written compact-control layer extension.

Arithmetic checks accompany, and do not replace, the fixed-tape construction
and proof. Historical witnesses and pinned upstream files are unchanged.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

from certify import Parameters,constraints,margins,network,require,verify_sources
from paired_network import BIT_SAVING
from prepare_layers import guard,packed_exponents,complex_saving_bounds,serializable
from search_network import log_integer_bounds
from audit_short_guards import guard_width

ROOT=Path(__file__).resolve().parents[1]
COMPLEX_H=25
COMPLEX_SAVING=Q(418,10**12)
KAPPA=Q(83,10**12)


def ceil_log(n,base):
    require(n>=1 and base>=2,'Invalid logarithm')
    j=0;power=1
    while power<n:power*=base;j+=1
    return j


def allocation(d,D,K,G,m,W):
    """Field dimensions only; no exponentially large arrays are materialized."""
    require(1<=D<=d and min(K,G)>=1 and min(m,W)>=2,'Invalid dimensions')
    q0=ceil_log(W,2)*ceil_log(2*d,m)
    k0=ceil_log(d,m)
    H=d*G
    front=(2*H+K-1)//K;back=(H+K-1)//K
    reserved=q0+front+back
    require(q0*K>=k0*ceil_log(W,2),'Insufficient row divisor capacity')
    require(front*K>=2*H and back*K>=H,'Insufficient compact fields')
    return dict(d=d,D=D,K=K,G=G,compact_capacity=H,row_chunks=q0,
                front_chunks=front,back_chunks=back,reserved_chunks=reserved,
                recursion_depth_cap=k0,row_bits=q0*K,
                mode='individual' if D<=reserved else 'recursive',
                active_chunks=max(0,D-reserved),
                preprocessed_chunks=min(D,reserved),
                front_slack_bits=front*K-2*H,back_slack_bits=back*K-H)


def repair_bound(p,n,K):
    require(p>=2 and 0<=n<=p,'Invalid repair family')
    G=guard_width(p);ell=(p-1).bit_length()
    require(K>=G+4*ell+10,'Use the common eventual cutoff')
    delta=Q(2*n,1<<G)+Q(8*n,1<<(K-G))
    require(delta<=Q(5,128*p**3),'Repair density bound failed')
    return dict(p=p,n=n,K=K,G=G,late_bad_fraction_upper=delta,
                uniform_upper=Q(5,128*p**3))


def layer_exponents(tau,sigma,beta,c):
    require(c>0,'Positive spacing growth required')
    e=packed_exponents(tau,sigma,beta,c,theta=Q(0))
    return dict(internal=e['internal'],leaf=e['leaf'],
                preprocessing=max(Q(0),1-c),
                layer=max(e['internal'],e['leaf'],1-c,Q(0)))


def parameters():
    return Parameters(tau=1-BIT_SAVING,sigma=1-COMPLEX_SAVING,
        epsilon=Q(1999,10000),c=Q(1,5),
        lam=1-Q(1671,4*10**12),lamp=1-Q(167,4*10**11),
        kappa=KAPPA,beta=Q(1,1000),delta=Q(1,10**6),C1=Q(49961,10000))


def check(p,h=COMPLEX_H,zeta=Q(1,10000)):
    require(0<1-p.tau<=BIT_SAVING,'Bit exponent exceeds retained witness')
    n=network(h);lo,hi=complex_saving_bounds(h)
    require(0<1-p.sigma<lo,'Complex exponent lacks a strict certificate')
    require(n['Lc']<n['N'],'Complex deficit is not positive')
    g=guard(p.beta,zeta,h)
    require(p.C1==g['C1'],'Guard mismatch')
    e=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    slacks=constraints(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    # This is a different proved primitive, not a relaxation of the old
    # packed routine. Its overhead and reservation obligations are explicit.
    slacks['packed_overhead']=p.lam-e['internal']
    slacks['reserved_axes']=p.lamp-e['preprocessing']
    for name,slack in slacks.items():require(slack>0,'Compact-control constraint: '+name)
    gs=margins(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    require(min(gs.values())>p.kappa,'No final absorption gap')
    require(Q(1,2**34)<p.kappa<Q(1,2**33),'Unexpected dyadic scale')
    # The older two hypothetical milestones can be assessed by separate
    # calls with their own kappa; the main witness is stronger than 2^-34.
    return dict(parameters=vars(p),complex_h=h,guard=g,recurrence=e,
                constraint_slacks=slacks,margins=gs,minimum_margin=min(gs.values()),
                absorption_gap=min(gs.values())-p.kappa,
                complex_saving_enclosure=(lo,hi))


def milestone(p,h,zeta=Q(1,100)):
    """Check earlier requested dyadic targets under the new recurrence."""
    g=guard(p.beta,zeta,h)
    require(p.C1==g['C1'],'Milestone guard mismatch')
    require(1-p.tau<=BIT_SAVING and 1-p.sigma<complex_saving_bounds(h)[0],
            'Unsupported motif exponent')
    e=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=constraints(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    cs['packed_overhead']=p.lam-e['internal']
    cs['reserved_axes']=p.lamp-e['preprocessing']
    require(all(v>0 for v in cs.values()),'Milestone constraint failed')
    gs=margins(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    require(min(gs.values())>p.kappa,'Milestone has no absorption gap')
    return dict(parameters=vars(p),guard=g,recurrence=e,constraint_slacks=cs,
                minimum_margin=min(gs.values()),absorption_gap=min(gs.values())-p.kappa)


def certificate():
    from prepare_layers import scenarios
    p=parameters();main=check(p);n=network(COMPLEX_H)
    _,log_hi=log_integer_bounds(n['m'])
    require(n['eta_c']>COMPLEX_SAVING*log_hi,'Simple exponential comparison failed')
    targets={}
    for key,h in (('hypothetical_39',50),('hypothetical_34',25)):
        old=scenarios()[key]
        targets[key.replace('hypothetical_','target_')]=milestone(Parameters(**old['parameters']),h)
    hi=complex_saving_bounds(COMPLEX_H)[1]
    # The Gaussian margin enforces epsilon<1/5; the leaf margin limits
    # 1-lambda' to (1-beta)*a_c<a_c. Thus kappa<a_c/5 here.
    ceiling=hi/5
    require(ceiling<Q(1,2**33),'This family could cross the next dyadic value')
    plans=[allocation(d,d,K,guard_width(p0),15625,n['Wc']) for d,K,p0 in
           ((1,1,16),(100,2,10**10),(10**30,10**6,10**151))]
    require(plans[-1]['mode']=='recursive','Large reservation control failed')
    proof_files=['notes/compact-control-movement.tex','notes/compact-control-layout.tex',
                 'notes/compact-control-guard.tex','notes/independent-complex.tex']
    return dict(status='CONDITIONAL COMPACT-CONTROL WITNESS; SUPPLIED WRITTEN TAPE AND LAYER PROOFS; NOT FORMAL VERIFICATION',
                upstream_commit=verify_sources(),main=main,milestones=targets,
                complex_counts={k:n[k] for k in ('h','m','v','N','Wc','sc','Lc','eta_c')},
                complex_log_upper=log_hi,complex_deficit_slack=n['eta_c']-COMPLEX_SAVING*log_hi,
                allocation_controls=plans,
                repair_controls=[repair_bound(p0,p0,8*(p0-1).bit_length()+16)
                                 for p0 in (2,16,100,10**6)],
                scoped_ceiling=dict(upper=ceiling,below_next_dyadic=True,
                    witness_fraction_of_upper=KAPPA/ceiling,
                    scope='Unchanged complex h=25 motif and retained Gaussian/leaf assembly inequalities; not a bound on new complex networks or algorithms.'),
                improvement_over_published_59=KAPPA*2**59,
                bit_arity=125000,complex_arity=15625,
                proof_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                              for name in proof_files},
                scope='Conditional on the pinned upstream interfaces, published paired-bit and Gaussian refinements, and the new compact-control movement, reservation, repair, independent-complex and generalized-guard proofs. Exact arithmetic is not formal verification.')


if __name__=='__main__':
    (ROOT/'certificates/compact-control-layer.json').write_text(
        json.dumps(serializable(certificate()),indent=2,sort_keys=True)+'\n')
    print('PASS conditional compact-control accounting:',KAPPA,'> 2^-34; proof review required.')

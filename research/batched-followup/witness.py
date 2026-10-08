"""Exact dimension-30 continuation of PR #10's conditional batching model."""
from dataclasses import asdict
from fractions import Fraction as Q
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from controlled_bit_rank_moment import counts
from batched_bit_rank_moment import rational_log_bounds
from batched_network import complex_certificate, complex_counts
from bulk_complex_guard import bulk_complex_guard
from certify import Parameters
from fast_gaussian import fast_constraints, fast_margins
from compact_control_layer import layer_exponents
from prepare_layers import serializable

BIT_SAVING=Q(253,10**9)
KAPPA=Q(12649,10**11)


def log_upper(x):
    x=Q(x)
    assert x>=1
    k=0
    while x>2:
        x/=2
        k+=1
    return k*rational_log_bounds(2)[1]+rational_log_bounds(x)[1]


def bit(roles,a=BIT_SAVING):
    n=counts(h=30,roles=roles)
    m,den=n['m'],n['W']*n['m']
    ratios=[Q(1,m)]+[Q(row['chunk_digits'],m) for row in n['recursive_blocks']]
    weights=[Q(n['singleton_calls'],den)]+[Q(row['copies']*row['chunk_digits'],den) for row in n['recursive_blocks']]
    assert all(0<x<1 for x in ratios)
    assert sum(weights)==1-n['eta']
    enclosures=[log_upper(1/x) for x in ratios]
    logs=[Q(-(-ell.numerator*10**9//ell.denominator),10**9) for ell in enclosures]
    assert all(exact<=simple for exact,simple in zip(enclosures,logs))
    assert all(0<a*x<1 for x in logs)
    upper=sum(w/(1-a*ell) for w,ell in zip(weights,logs))
    assert upper<1, 'Unsupported bit exponent'
    return dict(counts=n,bit_saving=a,ratios=ratios,weights=weights,
                log_upper_bounds=logs,log_enclosures=enclosures,
                moment_upper=upper,strict_gap=1-upper)


def assembly(kappa=KAPPA):
    p=Parameters(tau=1-BIT_SAVING,sigma=1-Q(7,10**7),
                 epsilon=Q(49999993,10**8),c=Q(1),beta=Q(1,1000),
                 delta=Q(1,10**10),lam=1-BIT_SAVING+Q(1,10**16),
                 lamp=1-BIT_SAVING+Q(2,10**16),C1=Q(11999,10000),kappa=kappa)
    guard=bulk_complex_guard(complex_counts(),p.beta,Q(1,10000))
    assert guard['C1']==p.C1
    ex=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=fast_constraints(p)
    cs['packed_overhead']=p.lam-ex['internal']
    cs['reserved_axes']=p.lamp-ex['preprocessing']
    gs=fast_margins(p)
    assert all(x>0 for x in cs.values())
    assert min(gs.values())>p.kappa>Q(6149999,5*10**13)
    return dict(parameters=asdict(p),guard=guard,recurrence=ex,
                constraints=cs,margins=gs,minimum_margin=min(gs.values()),
                absorption_gap=min(gs.values())-p.kappa)


def certificate(roles):
    return dict(status='CONDITIONAL DIMENSION-30 BATCHED WITNESS; UNREVIEWED',
                bit=bit(roles),complex=complex_certificate(),assembly=assembly(),
                inherited_pr10_commit='62691e395a0458ce089a1c7b5d89e74291e95e29',
                kappa_ratio_to_pr10=KAPPA/Q(6149999,5*10**13),
                scope='Dimension-30 producer and matching with the dimension-parametric '
                      'controlled-basis proof; unchanged dimension-28 complex network. '
                      'All PR #10 transfer, row, path-depth, Gaussian and upstream '
                      'interfaces remain mathematical dependencies.')


if __name__=='__main__':
    path=ROOT/'build/geometric-dimensions/30/result.json'
    roles=json.loads(path.read_text())['checked']['role_upper_bound']
    result=certificate(roles)
    (Path(__file__).with_name('certificate.json')).write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional kappa =',KAPPA)
    print('Strict bit moment gap:',float(result['bit']['strict_gap']))
    print('Strict assembly absorption gap:',result['assembly']['absorption_gap'])

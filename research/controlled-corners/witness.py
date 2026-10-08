"""Exact cost certificate for three further controlled projector blocks."""
from dataclasses import asdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from controlled_bit_rank_moment import counts
from batched_network import complex_certificate,complex_counts
from bulk_complex_guard import bulk_complex_guard
from batched_bit_rank_moment import rational_log_bounds
from certify import Parameters
from fast_gaussian import fast_constraints,fast_margins
from compact_control_layer import layer_exponents
from prepare_layers import serializable

BIT_SAVING=Q(40315,10**11)
KAPPA=Q(20156,10**11)


def log_upper(x):
    x=Q(x);k=0
    assert x>=1
    while x>2:x/=2;k+=1
    exact=k*rational_log_bounds(2)[1]+rational_log_bounds(x)[1]
    return Q(-(-exact.numerator*10**10//exact.denominator),10**10)


def bit(roles,a=BIT_SAVING,entrance=True,data=True,early_data=True):
    n=counts(h=30,roles=roles);h=n['h'];m=n['m'];B=n['v']**2*roles
    blocks=[dict(row) for row in n['recursive_blocks']]
    if entrance:blocks.append(dict(name='stage_two_auxiliary_entrance_middle',copies=B,chunk_digits=h*h-2*h))
    if data:blocks.append(dict(name='stage_three_data_corner_middle',copies=2*n['N'],chunk_digits=h*h-2*h+2))
    if early_data:blocks.append(dict(name='stage_two_data_entrance_middle',copies=2*n['N'],chunk_digits=h*h-4*h+2))
    singleton=n['original_rank_sum']-sum(row['copies']*row['chunk_digits'] for row in blocks)
    assert singleton>0
    denom=n['W']*m
    ratios=[Q(1,m)]+[Q(row['chunk_digits'],m) for row in blocks]
    weights=[Q(singleton,denom)]+[Q(row['copies']*row['chunk_digits'],denom) for row in blocks]
    assert sum(weights)==1-n['eta']
    logs=[log_upper(1/r) for r in ratios]
    assert all(0<a*ell<1 for ell in logs)
    upper=sum(w/(1-a*ell) for w,ell in zip(weights,logs))
    assert upper<1,'Unsupported controlled-corner saving'
    return dict(counts=n,blocks=blocks,singleton_calls=singleton,bit_saving=a,
                ratios=ratios,weights=weights,log_upper_bounds=logs,
                moment_upper=upper,strict_gap=1-upper)


def assembly(kappa=KAPPA):
    p=Parameters(tau=1-BIT_SAVING,sigma=1-Q(7,10**7),
                 epsilon=Q(99999979,200000000),c=Q(1),beta=Q(1,1000),
                 delta=Q(1,10**10),lam=1-BIT_SAVING+Q(1,10**16),
                 lamp=1-BIT_SAVING+Q(2,10**16),C1=Q(11999,10000),kappa=kappa)
    guard=bulk_complex_guard(complex_counts(),p.beta,Q(1,10000))
    assert guard['C1']==p.C1
    ex=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=fast_constraints(p)
    cs['packed_overhead']=p.lam-ex['internal'];cs['reserved_axes']=p.lamp-ex['preprocessing']
    gs=fast_margins(p)
    assert all(x>0 for x in cs.values())
    assert min(gs.values())>p.kappa>Q(12649,10**11)
    return dict(parameters=asdict(p),guard=guard,recurrence=ex,constraints=cs,
                margins=gs,minimum_margin=min(gs.values()),absorption_gap=min(gs.values())-p.kappa)


def certificate(roles):
    return dict(status='UNREVIEWED CONDITIONAL CONTROLLED-CORNER WITNESS',
                bit=bit(roles),complex=complex_certificate(),assembly=assembly(),
                ratio_to_pr12=KAPPA/Q(12649,10**11),
                retained_pr12_commit='35d31e30f28bc5da0ae6a88e7b03d75ebc855534',
                retained_pr10_commit='62691e395a0458ce089a1c7b5d89e74291e95e29',
                scope='Three new contiguous bit-recursion blocks under a strengthened '
                      'simultaneous-basis argument. Unchanged PR #12 producer, scalar '
                      'schedule and matching; unchanged PR #10 complex network and '
                      'depth guard. Exact checks are not formal verification of the '
                      'general rational argument or full multiplication theorem.')


def main():
    prior=ROOT/'research/batched-followup/certificate.json'
    old=json.loads(prior.read_text())
    for name,digest in old['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    roles=old['bit']['counts']['roles_per_invocation']
    result=certificate(roles)
    for action in (lambda:bit(roles,entrance=False),lambda:bit(roles,data=False),
                   lambda:bit(roles,early_data=False),lambda:bit(roles,Q(404,10**9)),
                   lambda:assembly(result['assembly']['minimum_margin'])):
        try:action()
        except AssertionError:pass
        else:raise AssertionError('Negative control was accepted')
    spec=importlib.util.spec_from_file_location('corner_matrix_checks',HERE/'matrix_checks.py')
    controls=importlib.util.module_from_spec(spec);spec.loader.exec_module(controls)
    result['matrix_checks']=[controls.one(h) for h in (3,4,5)]
    spec=importlib.util.spec_from_file_location('corner_rational_checks',HERE/'rational_checks.py')
    rational_controls=importlib.util.module_from_spec(spec);spec.loader.exec_module(rational_controls)
    result['rational_matrix_checks']=[rational_controls.check(h) for h in (3,4)]
    result['retained_producer_certificate_sha256']=sha256(prior.read_bytes()).hexdigest()
    result['source_sha256']={p.name:sha256(p.read_bytes()).hexdigest()
                            for p in sorted(HERE.iterdir()) if p.suffix in ('.py','.tex')}
    (HERE/'certificate.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS exact controlled pivot profiles over F_1009 at h=3,4,5')
    print('PASS exact rational reconstruction of all five controlled profiles at h=3,4')
    print('PASS required-block, exponent and absorption negative controls')
    print('Conditional kappa:',KAPPA,'bit moment gap:',float(result['bit']['strict_gap']))


if __name__=='__main__':main()

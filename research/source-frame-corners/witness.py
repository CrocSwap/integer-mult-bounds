"""Source-frame h30 network with two compatible data blocks; exact certificates."""
from dataclasses import asdict, replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(HERE/'pr13/scripts')]
import source_frame_network as pr13
from controlled_bit_rank_moment import counts
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints,fast_margins
from certify import Parameters
from prepare_layers import serializable

BIT_SAVING=Q(1816,10**9)
COMPLEX_SAVING=Q(18179,10**10)
KAPPA=Q(90799,10**11)


def log_upper(x):
    x=Q(x);k=0
    assert x>=1
    while x>2:x/=2;k+=1
    exact=k*pr13.rational_log_bounds(2)[1]+pr13.rational_log_bounds(x)[1]
    return Q(-(-exact.numerator*10**10//exact.denominator),10**10)


def bit(roles,a=BIT_SAVING,h=30,late=True,early=True):
    n=counts(h=h,roles=roles);m=n['m'];H=h*h;B=n['v']**2*roles
    blocks=[dict(name='stage_1_3_join_middle',copies=B,chunk_digits=m-4*h),
            dict(name='stage_3_data_middle',copies=2*n['N'],chunk_digits=m-2*H-2*h+2),
            dict(name='source_frame_stage_2_exit_middle',copies=B,chunk_digits=m-2*h)]
    if late:blocks.append(dict(name='stage_3_data_corner_middle',copies=2*n['N'],chunk_digits=H-2*h+2))
    if early:blocks.append(dict(name='stage_2_data_entrance_middle',copies=2*n['N'],chunk_digits=H-4*h+2))
    # Rebuild from rank mass. The former auxiliary entrance/sink blocks do NOT survive.
    S=n['original_rank_sum']-sum(b['copies']*b['chunk_digits'] for b in blocks)
    assert S>0 and all(0<b['chunk_digits']<m for b in blocks)
    ratios=[Q(1,m)]+[Q(b['chunk_digits'],m) for b in blocks]
    weights=[Q(S,n['W']*m)]+[Q(b['copies']*b['chunk_digits'],n['W']*m) for b in blocks]
    assert sum(weights)==1-n['eta']
    logs=[log_upper(1/r) for r in ratios]
    assert all(0<a*x<1 for x in logs)
    upper=sum(w/(1-a*x) for w,x in zip(weights,logs))
    assert upper<1,'Unsupported bit saving'
    return dict(counts=n,blocks=blocks,singleton_calls=S,bit_saving=a,ratios=ratios,
                weights=weights,log_upper_bounds=logs,moment_upper=upper,strict_gap=1-upper)


def assembly(kappa=KAPPA):
    p=Parameters(tau=1-BIT_SAVING,sigma=1-COMPLEX_SAVING,
        epsilon=Q(499999,10**6),c=Q(1),beta=Q(1,1000),delta=Q(1,10**10),
        lam=1-BIT_SAVING+Q(1,10**16),lamp=1-BIT_SAVING+Q(2,10**16),
        C1=Q(11999,10000),kappa=kappa)
    g=pr13.source_frame_guard(pr13.complex_counts(),p.beta,Q(1,10000))
    assert g['C1']==p.C1
    ex=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=fast_constraints(p);cs['packed_overhead']=p.lam-ex['internal'];cs['reserved_axes']=p.lamp-ex['preprocessing']
    gs=fast_margins(p)
    assert all(v>0 for v in cs.values())
    assert min(gs.values())>kappa>pr13.KAPPA
    return dict(parameters=asdict(p),guard=g,recurrence=ex,constraints=cs,margins=gs,
                minimum_margin=min(gs.values()),absorption_gap=min(gs.values())-kappa)


def certificate():
    previous=json.loads((ROOT/'research/batched-followup/certificate.json').read_text())
    roles=previous['bit']['counts']['roles_per_invocation']
    return dict(status='UNREVIEWED CONDITIONAL COMBINATION OF PR13 AND H30 DATA-CORNER BATCHING',
                bit=bit(roles),complex=pr13.complex_certificate(COMPLEX_SAVING),assembly=assembly(),
                ratio_to_pr13=KAPPA/pr13.KAPPA,pr13_commit='3ef246fa4f69c87ebfed78376418afa9ffcad145',
                pr12_commit='35d31e30f28bc5da0ae6a88e7b03d75ebc855534',
                scope='Exact finite witnesses and arithmetic; not formal verification of the general simultaneous-basis argument or inherited multiplication theorem.')


def main():
    oldpath=ROOT/'research/batched-followup/certificate.json'
    old=json.loads(oldpath.read_text())
    for name,digest in old['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    manifest=json.loads((HERE/'pr13/manifest.json').read_text())
    for name,digest in manifest['sha256'].items():
        assert sha256((HERE/'pr13'/name).read_bytes()).hexdigest()==digest,name
    inherited=pr13.certificate()
    assert inherited['assembly']['parameters']['kappa']==Q(7699,10**10)
    result=certificate();roles=result['bit']['counts']['roles_per_invocation']
    for label,action in [
        ('no late data block',lambda:bit(roles,late=False)),
        ('no early data block',lambda:bit(roles,early=False)),
        ('oversized bit saving',lambda:bit(roles,Q(1821,10**9))),
        ('oversized complex saving',lambda:pr13.complex_certificate(Q(1818,10**9))),
        ('zero final gap',lambda:assembly(result['assembly']['minimum_margin']))]:
        try:action()
        except (AssertionError,ValueError):pass
        else:raise AssertionError('Negative control accepted: '+label)
    spec=importlib.util.spec_from_file_location('source_corner_matrix_checks',HERE/'matrix_checks.py')
    controls=importlib.util.module_from_spec(spec);spec.loader.exec_module(controls)
    result['rational_matrix_checks']=[controls.check(h) for h in (3,4)]
    result['retained_producer_certificate_sha256']=sha256(oldpath.read_bytes()).hexdigest()
    paths=list(HERE.glob('*.py'))+list(HERE.glob('*.tex'))+[HERE/'pr13/manifest.json',ROOT/'research/controlled-corners/proof.tex',ROOT/'research/controlled-corners/matrix_checks.py']
    result['source_sha256']={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    (HERE/'certificate.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS retained PR13 arithmetic, source hashes and h30 producer certificate')
    print('PASS simultaneous exact-Q factorization of all six profiles at h3,h4')
    print('PASS missing-block, overclaimed-exponent and absorption negative controls')
    print('Conditional kappa',KAPPA,'ratio to PR13',float(result['ratio_to_pr13']))
    print('Bit gap',float(result['bit']['strict_gap']),'complex gap',float(result['complex']['strict_gap']))
    print('Absorption gap',result['assembly']['absorption_gap'])


if __name__=='__main__':main()

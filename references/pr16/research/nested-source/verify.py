#!/usr/bin/env python3
"""Exact nested-source moments, guard, and conditional assembly.

Retains PR7's finite producers and PR10's mixed-width tape interfaces.
Use --full to also run complete h28 complex frames/map and finite controls.
"""
from dataclasses import asdict, replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse, json, subprocess, sys
FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bit
import complex_all
from certify import Parameters
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints,fast_margins
from batched_bit_rank_moment import serializable
BIT_SAVING=Q(196,10**8)
COMPLEX_SAVING=Q(4,10**6)
KAPPA=Q(9799,10**10)


def parameters():
    return Parameters(tau=1-BIT_SAVING,sigma=1-COMPLEX_SAVING,
        epsilon=Q(499999,10**6),c=Q(1),beta=Q(1,1000),delta=Q(1,10**10),
        lam=1-BIT_SAVING+Q(1,10**16),lamp=1-BIT_SAVING+Q(2,10**16),
        C1=Q(3749,2500),kappa=KAPPA)


def assembly(p=None):
    p=parameters() if p is None else p
    assert p.tau==1-BIT_SAVING and p.sigma==1-COMPLEX_SAVING
    assert p.C1==Q(3,2)-Q(1,2)*p.beta+Q(1,10000)
    ex=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=fast_constraints(p)
    cs['packed_overhead']=p.lam-ex['internal']
    cs['reserved_axes']=p.lamp-ex['preprocessing']
    assert len(cs)==29 and all(v>0 for v in cs.values())
    margins=fast_margins(p)
    assert len(margins)==7 and min(margins.values())>p.kappa>Q(1,2**20)
    return dict(parameters=asdict(p),recurrence=ex,constraints=cs,margins=margins,
        minimum_margin=min(margins.values()),absorption_gap=min(margins.values())-p.kappa,
        dyadic_gap=p.kappa-Q(1,2**20),
        ratio_to_pr10=p.kappa/Q(6149999,5*10**13),ratio_to_pr12=p.kappa/Q(12649,10**11),ratio_to_pr13=p.kappa/Q(7699,10**10))


def certificate(full=False):
    b=bit.certificate(a=BIT_SAVING)
    c=complex_all.run(full=full)
    assert c['complex_saving_moments'][str(COMPLEX_SAVING)]['passed']
    assert c['guard']['C1']==parameters().C1
    w=assembly()
    controls={}
    if full:
        import nested_controls,geometry
        controls['nested_basis']=nested_controls.main()
        controls['h32_geometry']=geometry.run()
        producer=json.loads((FOLDER/'producer-certificate.json').read_text())
        assert producer['producer']['checked']['role_upper_bound']==b['counts']['roles_per_invocation']
        for name,digest in producer['source_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest
        controls['h32_producer']=producer
        result=subprocess.run([sys.executable,str(FOLDER/'complex_controls.py')],check=True,capture_output=True,text=True)
        controls['complex']=json.loads(result.stdout)
    rejected=[]
    for name,f in [('inflated_bit_saving',lambda:bit.certificate(a=Q(2,10**6))),
                   ('inflated_roles',lambda:bit.certificate(a=BIT_SAVING,roles=27000000))]:
        try:f()
        except AssertionError:rejected.append(name)
        else:raise AssertionError('negative control failed: '+name)
    bad=replace(parameters(),kappa=Q(1,2**19))
    try:assembly(bad)
    except AssertionError:rejected.append('unsupported_2_minus19')
    else:raise AssertionError('negative assembly control failed')
    paths=['bit.py','complex_all.py','complex_controls.py','verify.py','producer.py','geometry.py','nested_controls.py']
    return dict(status='CONDITIONAL 9799/10^10 > 2^-20 WITNESS; NOT FORMAL VERIFICATION',
        baseline_main='6e564879f51ae16f23d392e9e196c605f36d90df',
        retained_pr7='6725c6a17b17871a35353fd29157f4ed851bc114',
        batching_pr10='62691e395a0458ce089a1c7b5d89e74291e95e29',
        source_frames_pr13='3ef246fa4f69c87ebfed78376418afa9ffcad145',
        dimensions_pr12='35d31e30f28bc5da0ae6a88e7b03d75ebc855534',
        bit=b,complex=c,assembly=w,controls=controls,negative_controls=rejected,
        source_sha256={p:sha256((FOLDER/p).read_bytes()).hexdigest() for p in paths},
        proof_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in (ROOT/'notes/nested-bit.tex',ROOT/'notes/nested-complex.tex')},
        scope='Written new simultaneous-basis profiles and all-edge complex recursion, '
              'with exact arithmetic and retained finite checks. PR7 scalar producers, '
              'PR10 arbitrary-width tape interfaces and Gaussian correction, compact '
              'controls and original analytic framework remain conditional dependencies. '
              'This strictly exceeds 2^-20; it does not imply linear time.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');p.add_argument('--output',type=Path,default=FOLDER/'certificate.json');args=p.parse_args()
    result=certificate(args.full);args.output.write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+' > 2^-20')
    print('bit saving='+str(BIT_SAVING)+'; complex saving='+str(COMPLEX_SAVING))
    print('29 strict constraints; 7 strict margins; gap='+str(result['assembly']['absorption_gap']))
if __name__=='__main__':main()

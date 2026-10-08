#!/usr/bin/env python3
"""Exact composition of PR15's h30 producer with PR16's nested basis."""
from dataclasses import asdict, replace
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import argparse, contextlib, importlib.util, io, json, sys
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'references/pr10/scripts'))
from source_frame_stream_network import validate_hashes, parameters as old_parameters
from experiments.complex_all_residuals import certificate as complex_certificate
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints, fast_margins
from prepare_layers import serializable

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result
bit=module('nested_bit','references/pr16/research/nested-source/bit.py')
controls=module('nested_controls','references/pr16/research/nested-source/nested_controls.py')
BIT_SAVING=Q(2496689,10**12)
COMPLEX_SAVING=Q(4,10**6)
KAPPA=Q(1248342,10**12)
H,ROLES=30,13056812

def parameters():
    tau=1-BIT_SAVING
    epsilon=Q(((1-Q(1,10**10))/(2+BIT_SAVING)*10**12).__floor__(),10**12)
    return replace(old_parameters(),tau=tau,sigma=1-COMPLEX_SAVING,epsilon=epsilon,
        lam=tau+Q(1,10**16),lamp=tau+Q(2,10**16),kappa=KAPPA)

def assembly(p=None):
    p=parameters() if p is None else p
    assert p.tau==1-BIT_SAVING and p.sigma==1-COMPLEX_SAVING
    assert p.C1==Q(3,2)-p.beta/2+Q(1,10000)
    ex=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=fast_constraints(p)
    cs.update(packed_overhead=p.lam-ex['internal'],reserved_axes=p.lamp-ex['preprocessing'])
    assert len(cs)==29 and all(v>0 for v in cs.values())
    margins=fast_margins(p);minimum=min(margins.values())
    assert len(margins)==7 and minimum>p.kappa>Q(1,2**20)
    return dict(parameters=asdict(p),recurrence=ex,constraints=cs,margins=margins,
        minimum_margin=minimum,absorption_gap=minimum-p.kappa,
        ratio_to_pr14=p.kappa/Q(90799,10**11),ratio_to_pr15=p.kappa/Q(1076678,10**12),
        ratio_to_pr16=p.kappa/Q(9799,10**10))

def run(full=False):
    refs={}
    for pr in ('pr10','pr12','pr13','pr16'):
        folder=ROOT/'references'/pr
        refs[pr]=json.loads((folder/'SOURCE.json').read_text())
        for path,digest in refs[pr]['sha256'].items():
            assert sha256((folder/path).read_bytes()).hexdigest()==digest,(pr,path)
    producer=json.loads((HERE/'producer.json').read_text())
    validate_hashes(producer)
    assert producer['h']==H
    assert producer['global_roles']==dict(current=ROLES,center_loss=12180,extra_frame_loss=0)
    assert producer['matching']['every_intersection_two'] and producer['matching']['distinct_images']==142506
    b=bit.certificate(a=BIT_SAVING,h=H,roles=ROLES)
    # The imported computation is dimension-parametric; overwrite its historical
    # h32-only descriptive metadata with the actually checked inputs.
    b['status']='EXACT H30 NESTED-BASIS BIT MOMENT'
    b['dependencies']=['PR15 h30 stream producer with unchanged D0/D1 and data endpoints',
        'PR13 source frames','PR14/PR16 data corners','PR16 nested-basis lemma for h>=4',
        'PR10 mixed-width finite-tape interface']
    assert b['counts']['roles_per_invocation']==ROLES
    c=complex_certificate()
    assert c['complex_saving']>=COMPLEX_SAVING and c['moment_upper']<1
    assert c['guard']['C1']==parameters().C1
    # For every 0<r<1, r**(1-a) increases with a; the stronger
    # PR15 certificate therefore certifies our conservative a_c=4e-6.
    rejected=[]
    checks=[('next_bit_gridpoint',lambda:bit.certificate(a=BIT_SAVING+Q(1,10**12),h=H,roles=ROLES)),
            ('old_h30_role_count',lambda:bit.certificate(a=BIT_SAVING,h=H,roles=17515487)),
            ('remove_nested_corner',lambda:bit.certificate(a=BIT_SAVING,h=H,roles=ROLES,nested=False)),
            ('overstated_final_kappa',lambda:assembly(replace(parameters(),kappa=Q(125,10**8))))]
    for name,fn in checks:
        try:fn()
        except AssertionError:rejected.append(name)
        else:raise AssertionError('negative control unexpectedly passed: '+name)
    ctl=None
    if full:
        with contextlib.redirect_stdout(io.StringIO()):ctl=controls.main()
    paths=['research/nested-stream/verify.py','research/nested-stream/proof.tex',
           'research/nested-stream/make_patch.py','research/nested-stream/producer.json',
           'tests/test_nested_stream.py','research/nested-stream/README.md']
    return dict(status='CONDITIONAL COMPOSITION; NOT FORMAL VERIFICATION',
        producer=producer,bit=b,complex=c,assembly=assembly(),nested_controls=ctl,
        negative_controls=rejected,references=refs,
        proof_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        scope='Fresh exact h30 producer rebuild, rank moments and final assembly. '
              'Finite-field controls supplement the written general rational-basis argument. '
              'Inherited multiplication, mixed-width, source-frame and precision proofs '
              'remain mathematical dependencies requiring independent review.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');args=p.parse_args()
    result=run(args.full)
    (HERE/'certificate.json').write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+'; 29 constraints; 7 margins; gap='+str(result['assembly']['absorption_gap']))

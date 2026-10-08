#!/usr/bin/env python3
"""PR18 partial-swap frames on the independently audited PR17 ternary network."""
from dataclasses import asdict,replace
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import argparse,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'research/nested-stream'))
import verify as prior
sys.path.insert(0,str(HERE))
BIT_SAVING=Q(4187,10**9)
COMPLEX_SAVING=Q(4191487,10**12)
KAPPA=Q(2093495,10**12)

def bit_certificate(a=BIT_SAVING,remove_source=True):
    n=prior.bit.counts(prior.H,prior.ROLES)
    old_s=n['original_rank_sum'];old_S=n['singleton_calls']
    if remove_source:n['original_rank_sum']-=n['N'];n['singleton_calls']-=n['N']
    assert n['original_rank_sum']==n['W']*n['m']-(2 if remove_source else 1)*n['N']+2*n['decreasing_dimension']
    n['deficit']=n['W']*n['m']-n['original_rank_sum'];n['eta']=Q(n['deficit'],n['W']*n['m'])
    widths=[1]+[r['chunk_digits'] for r in n['recursive_blocks']]
    masses=[n['singleton_calls']]+[r['chunk_digits']*r['copies'] for r in n['recursive_blocks']]
    assert sum(masses)==n['original_rank_sum'] and all(0<x<n['m'] for x in widths)
    logs=[prior.bit.log_bounds(Q(n['m'],x))[1] for x in widths]
    weights=[Q(x,n['W']*n['m']) for x in masses]
    assert all(0<a*e<1 for e in logs)
    upper=sum((w/(1-a*ell) for w,ell in zip(weights,logs)),Q(0))
    assert upper<1
    return dict(counts=n,bit_saving=a,old_rank_sum=old_s,old_singletons=old_S,
        removed_source_calls=n['N'] if remove_source else 0,
        normalized_widths=[Q(x,n['m']) for x in widths],rank_mass_weights=weights,
        logarithm_upper_bounds=logs,moment_upper=upper,strict_gap=1-upper)

def parameters():
    tau=1-BIT_SAVING
    epsilon=Q(((1-Q(1,10**10))/(2+BIT_SAVING)*10**12).__floor__(),10**12)
    return replace(prior.parameters(),tau=tau,sigma=1-COMPLEX_SAVING,epsilon=epsilon,
        lam=tau+Q(1,10**16),lamp=tau+Q(2,10**16),kappa=KAPPA)

def assembly(p=None):
    p=parameters() if p is None else p
    assert p.tau==1-BIT_SAVING and p.sigma==1-COMPLEX_SAVING
    assert p.C1==Q(3,2)-p.beta/2+Q(1,10000)
    ex=prior.layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=prior.fast_constraints(p);cs.update(packed_overhead=p.lam-ex['internal'],reserved_axes=p.lamp-ex['preprocessing'])
    assert len(cs)==29 and all(x>0 for x in cs.values())
    margins=prior.fast_margins(p);minimum=min(margins.values())
    assert len(margins)==7 and minimum>p.kappa>Q(1,2**19)
    return dict(parameters=asdict(p),recurrence=ex,constraints=cs,margins=margins,
        minimum_margin=minimum,absorption_gap=minimum-p.kappa,
        ratio_to_pr17=p.kappa/prior.KAPPA,ratio_to_pr18=p.kappa/Q(942293,500000000000))

def run(full=False):
    # The prior producer and geometric profile proofs are immutable dependencies.
    saved=json.loads((ROOT/'research/nested-stream/certificate.json').read_text())
    for name,digest in saved['proof_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    producer=saved['producer'];prior.validate_hashes(producer)
    assert producer['h']==prior.H and producer['global_roles']['current']==prior.ROLES
    references=dict(saved['references'])
    references['pr18']=json.loads((ROOT/'references/pr18/SOURCE.json').read_text())
    for pr,manifest in references.items():
        for name,digest in manifest['sha256'].items():assert sha256((ROOT/'references'/pr/name).read_bytes()).hexdigest()==digest,(pr,name)
    b=bit_certificate();c=prior.complex_certificate()
    assert c['complex_saving']==COMPLEX_SAVING and c['moment_upper']<1
    assert c['guard']['C1']==parameters().C1
    negatives=[]
    for name,fn in [('retain_source_rank_penalty',lambda:bit_certificate(remove_source=False)),
                    ('unsupported_final_kappa',lambda:assembly(replace(parameters(),kappa=Q(21,10**7)))),
                    ('complex_leaf_too_slow',lambda:assembly(replace(parameters(),beta=Q(1,10))))]:
        try:fn()
        except AssertionError:negatives.append(name)
        else:raise AssertionError('negative control passed: '+name)
    controls=None
    if full:
        import controls as finite
        controls=finite.run()
    paths=['witness.py','proof.tex','make_patch.py','controls.py']
    return dict(status='CONDITIONAL PARTIAL-SWAP TERNARY COMPOSITION; NOT FORMAL VERIFICATION',
        producer=producer,bit=b,complex=c,assembly=assembly(),finite_controls=controls,
        references=references,negative_controls=negatives,
        proof_sha256={str((HERE/p).relative_to(ROOT)):sha256((HERE/p).read_bytes()).hexdigest() for p in paths},
        scope='Uses the fully rebuilt PR17/PR15 physical producer. New exact-Q identities and complete small framed F3 dirty-scratch controls supplement the general written transfer. Inherited basis, tape and multiplication arguments remain unreviewed mathematical dependencies.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');args=p.parse_args()
    result=run(args.full);(HERE/'certificate.json').write_text(json.dumps(prior.serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+' > 2^-19; 29 constraints; 7 margins; gap='+str(result['assembly']['absorption_gap']))

#!/usr/bin/env python3
"""A retained A5 block with PR23's semantic/bulk transfer.

Rohan Arun, with OpenAI Codex assistance. The assembly formula is adapted
from Zhihao Chen's PR23; RaD/PR20 analytic/tape interfaces remain dependencies.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
    return obj
base=module('a5_semantic_PR23','research/semantic-bulk/verify.py')
prior=module('a5_semantic_PR21','research/translated-partial/verify.py')
controls=module('a5_semantic_controls','research/a5-semantic/controls.py')
BIT_SAVING=Q(1144733,10**11)
COMPLEX_SAVING=Q(18,10**6)
KAPPA=Q(11447067,10**12)


def bit_counts(use_block=True):
    old,original=prior.bit_counts();n=dict(old);rows=Counter(original)
    if use_block:
        rows[1]-=42*n['N'];rows[21]+=2*n['N']
    n['singletons']=rows[1]
    assert rows[1]>=0 and sum(r*c for r,c in rows.items())==n['s']
    assert max(rows)==max(original) and all(0<r<n['m'] for r in rows)
    assert n['W']*n['m']-n['s']==2*n['N']-2*n['L']
    return n,rows


def bit_certificate(saving=BIT_SAVING,use_block=True):
    n,rows=bit_counts(use_block)
    value=prior.retained.moment(n['m'],n['W'],rows,saving,True)
    return dict(counts=n,**value,A5_profile=dict(copies=2*n['N'],singletons=26 if use_block else 47,
        blocks=[21,481] if use_block else [481],rank_per_copy=528),
        scope='Same PR21 common basis and physical network; one contiguous21 block replaces21 singleton pivots per A5 macro.')


def assembly(f,kappa=KAPPA,old_guard=False,old_exposures=False):
    # Parameterized transcription of Zhihao Chen's PR23 assembly. Only a changes.
    a,b=BIT_SAVING,COMPLEX_SAVING;h=Q(1,10**8);beta=Q(1,4)
    tau,sigma=1-a,1-b;q=a*(1-2*h);lp=1-q;lam=(tau+lp)/2
    c=q*(1+h);eps=(1-h)/(1+c+q);G=eps*q
    r=(G+1-eps)/2;delta=h/8
    C1=Q(19991,10000) if old_guard else Q(1)
    margins=dict(g1=1-eps*(1+c),g2=a,g3=G,g4=a,
        g5=min(1-eps-delta,r-delta),g6=1-eps-delta,g7=eps)
    if old_exposures:margins.update(g2=eps*c*a,g4=a*(1-eps))
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    slacks=dict(a_positive=a,a_below_b=b-a,b_below_one_over32=Q(1,32)-b,
        beta_positive=beta,beta_below_one=1-beta,phase_leaf_above_bit=(1-beta)*b-a,
        q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
        c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
        lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,
        lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
        compact_leaf=lp-leaf,compact_reservations=lp-(1-c),lambda_prime_below_one=q,
        epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps*C1,
        K_geometry=1-eps*(1+c),K_dominates_log=eps*c,
        record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=r-delta,
        gamma_sublinear=1-eps-r,cell_above_band=eps-(1-r)/2,
        prime_interval_packing=1-eps,alpha_positive=r,alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r,delta_positive=delta,
        delta_below_one_eighth=Q(1,8)-delta,short_record_fallback=eps-a,
        small_field_exposure=1-eps-G,artificial_boundary=8-eps+r-delta-G,
        literal_scalar_guard=Q(f['semantic']['strict_literal_gap']),
        row_product_gap=f['rows']['degree_gap'])
    slacks.update({name+'_above_kappa':value-kappa for name,value in margins.items()})
    assert len(slacks)==47 and all(x>0 for x in slacks.values()),{k:str(v) for k,v in slacks.items() if v<=0}
    assert len(margins)==7 and min(margins.values())==G and margins['g1']-G==h
    assert kappa>Q(1,2**17)
    p=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,q=q,c=c,
        epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,
        delta=delta,C0=f['semantic']['C0'],C1=C1,kappa=kappa)
    return dict(parameters=p,constraints=slacks,margins=margins,minimum_margin=G,
        absorption_gap=G-kappa,gap_above_2_minus17=kappa-Q(1,2**17),
        ratio_to_PR23=kappa/base.KAPPA,
        recurrence=dict(internal=internal,leaf=leaf,reservations=1-c))


def run():
    old,ref=base.pinned_inputs();f=base.finite_bridge(old)
    inherited=json.loads((ROOT/'research/semantic-bulk/certificate.json').read_text())
    for name,digest in inherited['input_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    bit=bit_certificate();n=bit['counts']
    assert (n['W'],n['m'],max(r for r,c in bit['child_width_multiplicities']))==(f['bit']['W'],f['bit']['m'],f['bit']['maxchild'])
    assert f['semantic']['C1']==1 and f['rows']['degree']==89000
    a=assembly(f);cutoffs=base.cutoffs(f,a);finite=controls.run()
    rejected=[]
    for name,fn in [('omit_A5_block',lambda:bit_certificate(use_block=False)),
        ('next_bit_grid_not_certified',lambda:bit_certificate(BIT_SAVING+Q(1,10**12))),
        ('old_quadratic_guard',lambda:assembly(f,old_guard=True)),
        ('old_separate_exposures',lambda:assembly(f,old_exposures=True)),
        ('next_kappa_grid_rejected',lambda:assembly(f,kappa=KAPPA+Q(1,10**12)))]:
        try:fn()
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Negative control passed: '+name)
    files=[HERE/'witness.py',HERE/'controls.py',HERE/'a5-block.tex',HERE/'make_patch.py',
           ROOT/'notes/a5-semantic-note.tex',ROOT/'tests/test_a5_semantic.py',HERE/'SOURCE.json']
    return dict(status='CONDITIONAL A5 BLOCK SAVING 11447067/10^12 > 2^-17; NOT FORMAL VERIFICATION',
        bit=bit,finite_bridge=f,assembly=a,eventual_bounds=cutoffs,controls=finite,
        negative_controls=rejected,PR20_source=ref['commit'],
        inherited_PR23_input_sha256=inherited['input_sha256'],
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files},
        scope='One previously unbatched contiguous A5 block is exposed in the retained basis. PR21 physical producers and frames, PR23 complex semantic guard and joint row budgets remain unchanged. Exact controls supplement written inherited mathematical proofs.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=HERE/'certificate.json');args=parser.parse_args()
    result=run();args.output.write_text(json.dumps(base.js(result),indent=2,sort_keys=True)+'\n')
    print('PASS conditional kappa='+str(KAPPA)+';47 strict constraints;7 margins;gap='+str(result['assembly']['absorption_gap']))

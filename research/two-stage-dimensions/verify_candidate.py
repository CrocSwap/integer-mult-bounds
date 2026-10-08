#!/usr/bin/env python3
"""Exact certificate for the PR29 two-stage construction at re-optimized factor dimensions.

Reuses, unchanged and source-pinned, Zhihao Chen's PR29 profile, basis prescriptions,
modular corner control and PR23 assembly logic; only the factor dimensions (a,b)
and the two rational savings change. Run: python3 research/two-stage-dimensions/verify_candidate.py
"""
import sys,json,importlib.util
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];TS=ROOT/'research/two-stage'
sys.path[:0]=[str(TS),str(ROOT/'scripts')]
from two_stage_unequal import profile,prescriptions
from check_unequal_corners import control
from partial_swap_network import moment
from prepare_layers import serializable
from assembly import assembly as inherited_assembly
from difflib import unified_diff

A_DIM,B_DIM,AB_NUM,K_NUM=47,45,16039,16038
AB=Q(AB_NUM,10**9);KAPPA=Q(K_NUM,10**9)

def halving(m,r):
    k=1
    while m**k<=2*r**k:k+=1
    return k

def assembly(f,a,kappa,old_guard=False,old_exposures=False):
    """research/two-stage/assembly.py (Zhihao Chen, PR29) with the bit saving a as a parameter."""
    b=Q(18,10**6);h=Q(1,10**8);beta=Q(1,10)
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
    slacks.update({name+'_above_kappa':val-kappa for name,val in margins.items()})
    assert all(x>0 for x in slacks.values()),{k:str(v) for k,v in slacks.items() if v<=0}
    assert min(margins.values())==G and margins['g1']-G==h
    p=dict(a_bit=a,a_complex=b,tau=tau,sigma=sigma,beta=beta,q=q,c=c,
        epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,
        delta=delta,C0=f['semantic']['C0'],C1=C1,kappa=kappa)
    return dict(parameters=p,constraints=slacks,margins=margins,minimum_margin=G,
        absorption_gap=G-kappa,recurrence=dict(internal=internal,leaf=leaf,reservations=1-c))

def run():
    a_dim,b_dim=A_DIM,B_DIM
    # Every PR29 source used here is pinned to the hashes recorded by PR29.
    manifest=json.loads((TS/'SOURCE.json').read_text())
    for name,digest in manifest['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    spec=importlib.util.spec_from_file_location('semantic_predecessor',ROOT/'research/semantic-bulk/verify.py')
    predecessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(predecessor)
    predecessor.pinned_inputs()
    old=json.loads((ROOT/'research/semantic-bulk/certificate.json').read_text())
    for name,digest in old['input_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    original=json.loads((TS/'certificate.json').read_text())
    original['finite_bridge']['rows']['degree_gap']=Q(original['finite_bridge']['rows']['degree_gap'])
    replay=assembly(original['finite_bridge'],Q(15537,10**9),Q(15536,10**9))
    inherited=inherited_assembly(original['finite_bridge'])
    for key,value in replay.items():
        assert serializable(value)==serializable(inherited[key]), 'Assembly replay: '+key
    axes=[]
    for h in [a_dim,b_dim]:
        record=json.loads((HERE/f'producer-{h}.json').read_text());x=record['matched']
        assert record['scalar']['h']==h and x['h']==h
        assert record['scalar']['all_additions_disjoint'] and record['scalar']['all_partial_outputs_exact']
        assert record['scalar']['every_node_has_common_point']
        assert x['q']==3*x['v']+h and x['R']==x['c']+x['q']-x['matched']
        assert x['loss']==h*(h-1) and sum(r*n for r,n in enumerate(x['histogram']))==h*x['R']+2*x['loss']
        labels=json.loads((HERE/f'labels-{h}.json').read_text())
        assert labels['h']==h and labels['complement_orientation_by_exact_duality']
        assert labels['exact_envelopes']==x['c'] and labels['exact_dependency_inclusions']==2*x['c']
        assert labels['output_frames']==x['q']
        axes.append(x)
    p=profile(*axes)
    assert p['deficit']==p['N']-2*p['L'] and sum(t*n for t,n in p['rows'].items())==p['s']
    exact=moment(p['m'],p['W'],p['rows'],AB,True)
    assert exact['strict_gap']>0
    # Saving one part in 10^9 larger must fail with the same enclosure (sharpness record only).
    try:moment(p['m'],p['W'],p['rows'],AB+Q(1,10**9),True);next_fails=False
    except ValueError:next_fails=True
    basis=[control(b_dim,seed) for seed in (1,2,3)];prescriptions(a_dim,b_dim)
    f=old['finite_bridge']
    f['semantic']['strict_literal_gap']=Q(f['semantic']['strict_literal_gap'])
    f['semantic']['C0']=int(f['semantic']['C0'])
    mb,Wb,Mb=p['m'],p['W'],max(p['rows']);db=halving(mb,Mb);wb=Wb.bit_length()
    f['bit']=dict(m=mb,W=Wb,maxchild=Mb,halving_degree=db,wire_bits=wb)
    coefficient=db*wb+f['complex']['halving_degree']*f['complex']['wire_bits']
    degree=1000*((coefficient*51+24999)//25000)
    f['rows']=dict(coefficient=coefficient,degree=degree,suffix_slope=4*degree,
                   degree_gap=degree-Q(coefficient*51,25),contract='PR23 product Wc^Dc Wb^Db; parked correction uses existing role stream, no new row index')
    assembled=assembly(f,AB,KAPPA)
    assert assembled['absorption_gap']>0
    rejected=[]
    for name,kwargs in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True))]:
        try:assembly(f,AB,KAPPA,**kwargs)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    try:assembly(f,AB,KAPPA+Q(1,10**9))
    except AssertionError:rejected.append('kappa_plus_1e-9')
    else:raise AssertionError('next kappa unexpectedly passes')
    no_local=profile(*axes,local=False)
    try:moment(no_local['m'],no_local['W'],no_local['rows'],AB,True)
    except ValueError:rejected.append('unbatched_local_profile')
    else:raise AssertionError('Unbatched local profile unexpectedly certified')
    source_paths=[HERE/'verify_candidate.py',HERE/'producer.py',HERE/'README.md',ROOT/'notes/two-stage-47-45-note.tex']
    return dict(source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in source_paths},
                label_records={str(h):sha256((HERE/f'labels-{h}.json').read_bytes()).hexdigest() for h in [a_dim,b_dim]},
                status=f'CONDITIONAL kappa={K_NUM}/10^9 at PR29 two-stage dims ({a_dim},{b_dim}); not formal verification',
                dims=[a_dim,b_dim],bit=dict(**p,**exact),next_bit_saving_fails=next_fails,basis=basis,
                finite_bridge=f,assembly=assembled,negative_controls=rejected,
                producer_records={str(h):sha256((HERE/f'producer-{h}.json').read_bytes()).hexdigest() for h in [a_dim,b_dim]},
                references=dict(PR29='9d963275075fa98f1da821e27757b238dafd6b3c',PR23='661ebabc1076c9f525d7ce4967c876b203fa9827',PR24='ed90fd940279c336ebc45968631bdebfb087b505'))

if __name__=='__main__':
    r=run();out=HERE/f'certificate-{A_DIM}-{B_DIM}.json'
    out.write_text(json.dumps(serializable(r),indent=2,sort_keys=True)+'\n')
    original=(ROOT/'notes/two-stage-16-note.tex').read_text()
    updated=(ROOT/'notes/two-stage-47-45-note.tex').read_text()
    patch=''.join(unified_diff(original.splitlines(keepends=True),updated.splitlines(keepends=True),fromfile='a/notes/two-stage-16-note.tex',tofile='b/notes/two-stage-16-note.tex'))
    (ROOT/'patches/two-stage-dimensions.patch').write_text(patch)
    print('PASS dims',r['dims'],'kappa',K_NUM,'/10^9;',len(r['assembly']['constraints']),'constraints; 7 margins')
    print('bit moment gap',float(r['bit']['strict_gap']),'final gap',float(r['assembly']['absorption_gap']),'next saving fails',r['next_bit_saving_fails'])
    print('m',r['bit']['m'],'W',r['bit']['W'],'N',r['bit']['N'],'deficit',r['bit']['deficit'],'stock',r['finite_bridge']['rows'],'bit',r['finite_bridge']['bit'])

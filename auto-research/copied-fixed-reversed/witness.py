#!/usr/bin/env python3
"""Exact copied-center reversed-corner witness with fixed middle basis I+J.

Credits: icekylinx PR32/36 fixed-basis and copied-center constructions;
James Chang PR34 reversed geometry/balanced parameters; PR37 integration;
Zhihao Chen, RaD/hipotures, Paureel, Dominik Scholz, Swapnil Jain and earlier
contributors. General common-basis/CRT/tape proofs are explicit dependencies.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prior=load('fixed25_prior_copied_reversed',ROOT/'research/copied-reversed/witness.py')
balanced=load('fixed25_balanced_assembly',HERE/'balanced_assembly.py')
js,read,moment=prior.js,prior.read,prior.moment
AB=Q(3886826921,10**14);KAPPA=Q(971668963,25000000000000);AC=prior.AC
INHERITED='2f7578affce416ad4b6c41f3438ebb734f66a899'
PR38_KAPPA=Q(3886224,10**11)

def verify_sources():
    manifest=read(HERE/'producer-source.json')
    assert manifest['parent_commit']==INHERITED
    for name,digest in manifest['sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Source pin mismatch: '+name
    return manifest

def counts():
    axes,_,_=prior.inputs();p=prior.counts(list(reversed(axes)))
    rec=read(HERE/'producer-input-25.json');prof=read(HERE/'profile-25.json')
    original,positive=rec['original'],rec['matched']
    assert rec['scalar']['all_additions_disjoint'] and rec['scalar']['all_partial_outputs_exact'] and rec['scalar']['every_node_has_common_point']
    h=25;assert prof['h']==h and prof['v']==2300
    for key in ['h','v','c','q','R','matched','loss','rank_sum']:assert original[key]==positive[key]
    axis=next(r for r in axes if r['h']==h)
    for key in ['h','v','c','q','R','loss','histogram']:assert positive[key]==axis[key]
    assert positive['matched']==axis['matching']
    assert prof['R']==positive['R']==51299 and prof['loss']==600
    assert prof['distinct_matrices']==prof['crt_matrices']==96273
    assert prof['rank_sum']==sum(t*n for t,n in enumerate(prof['blocks']))==h*prof['R']+2*prof['loss']
    assert original['histogram'][h]==h and prof['blocks'][h]>=h
    copied=list(prof['blocks']);copied[h]-=h;copied[1]+=h
    assert all(n>=0 for n in copied)
    assert sum(t*n for t,n in enumerate(copied))==h*prof['R']+prof['loss']
    copies=p['N']//prof['v'];replacement=Counter({t:n*copies for t,n in enumerate(copied) if t and n})
    before=p['parts']['internal_25'];assert sum(t*n for t,n in before.items())==sum(t*n for t,n in replacement.items())
    p['parts']['internal_25']=replacement;hist=sum(p['parts'].values(),Counter())
    assert sum(t*n for t,n in hist.items())==p['total_rank']==p['W']*p['m']-p['N']+p['L']
    assert all(0<t<p['m'] and n>0 for t,n in hist.items())
    p['child_multiplicities']=dict(sorted(hist.items()));p['maxchild']=max(hist)
    assert len(hist)==27
    p.update(fixed_middle=dict(basis='I+J',h=h,profile=prof,copied_blocks=copied,copies=copies,
        original_generic_internal=before,scope='Entire original fixed-basis internal profile replaces generic-positive internal25 once. Exactly25 identity cleanup calls become25 rank-one complements; all retained rank24 transform profiles stay.'))
    return p

def run():
    assert not sys.flags.optimize
    verify_sources();baseline=prior.run();bit=counts()
    exact=moment(bit['m'],bit['W'],bit['child_multiplicities'],AB);assert exact['upper']<1
    old_at_new=moment(bit['m'],bit['W'],baseline['bit']['counts']['child_multiplicities'],AB);assert old_at_new['lower']>1
    next_bit=moment(bit['m'],bit['W'],bit['child_multiplicities'],AB+Q(1,10**14));assert next_bit['lower']>1
    _,phase_row,_=prior.inputs();phase=prior.inherited.profile([phase_row,phase_row])
    f=prior.inherited.finite_bridge(bit,phase,[phase_row,phase_row]);assert js(f)==js(baseline['finite_bridge'])
    final=balanced.assembly(f,AB,KAPPA,a_complex=AC);eventual=balanced.cutoffs(f,final)
    negatives=[]
    for name,kwargs in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True)),('original_prefix',dict(original_prefix=True)),('next_kappa_grid',dict(kappa=KAPPA+Q(1,10**14)))]:
        try:balanced.assembly(f,AB,kwargs.pop('kappa',KAPPA),a_complex=AC,**kwargs)
        except AssertionError:negatives.append(name)
        else:raise AssertionError('Negative control accepted: '+name)
    sources=dict(baseline['source_sha256']);sources.update(verify_sources()['sha256'])
    sources[str((HERE/'producer-source.json').relative_to(ROOT))]=sha256((HERE/'producer-source.json').read_bytes()).hexdigest()
    return dict(status='Conditional copied fixed-middle reversed-corner witness; exact finite arithmetic, written proof dependencies retained',parent_commit=INHERITED,
        bit=dict(counts=bit,**exact),complex=baseline['complex'],finite_bridge=f,assembly=final,eventual_bounds=eventual,
        previous=dict(kappa=prior.KAPPA,bit=prior.AB,old_profile_at_new_bit_lower=old_at_new['lower']),
        next_bit_grid=next_bit,negative_controls=negatives,ratio_to_PR37=KAPPA/prior.KAPPA,
        PR38_comparison=dict(commit='cc794077f6c103e24ec0939be765cd1521239aab',kappa=PR38_KAPPA,ratio=KAPPA/PR38_KAPPA),source_sha256=sources,
        scope='Fixed L25=I+J original envelopes plus generic positive first-axis23. Source/copy/auxiliary/data simultaneous-basis proof, full CRT bound and inherited copied-stream/tape/analytic hypotheses remain separate checked obligations; no global optimality claim.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();result=run()
    if a.output:a.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('PASS bit='+str(AB)+';kappa='+str(KAPPA)+';47constraints;7margins;27classes;p^2000')

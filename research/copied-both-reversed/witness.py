#!/usr/bin/env python3
"""Both fixed I+J factors, copied centers and reversed23/25 arithmetic.

Credits: icekylinx PR32/36 fixed bases/copied centers, Dominik Scholz PR38
both-fixed composition, James Chang PR34
reversed geometry, PR37/39 integration, Zhihao Chen and RaD/hipotures semantic
assembly, Paureel, Dominik Scholz, Swapnil Jain and preceding contributors.
Full pairwise fixed-basis compatibility is a separate proof gate.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
prior=load('bothfixed_parent_PR39',ROOT/'research/copied-fixed-reversed/witness.py')
crt=load('bothfixed_dimension_crt',HERE/'crt_bounds.py')
js,read,moment=prior.js,prior.read,prior.moment
AB=Q(783777693,20000000000000);KAPPA=Q(1959367447,50000000000000);AC=prior.AC
INHERITED='70ae24129649f6d6d4ec6360962a80c3c42a38f1'

def verify_sources():
    manifest=read(HERE/'producer-source.json');assert manifest['parent_commit']==INHERITED
    for name,digest in manifest['sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Source pin mismatch: '+name
    return manifest

def counts():
    p=prior.counts();axes,_,_=prior.prior.inputs();rec=read(HERE/'producer-input-23.json');prof=read(HERE/'profile-23.json')
    original,positive=rec['original'],rec['matched'];h=23;assert prof['h']==h and prof['v']==1771
    assert rec['scalar']['all_additions_disjoint'] and rec['scalar']['all_partial_outputs_exact'] and rec['scalar']['every_node_has_common_point']
    for key in ['h','v','c','q','R','matched','loss','rank_sum']:assert original[key]==positive[key]
    axis=next(r for r in axes if r['h']==h)
    for key in ['h','v','c','q','R','loss','histogram']:assert positive[key]==axis[key]
    assert positive['matched']==axis['matching']
    assert prof['R']==positive['R']==38776 and prof['loss']==506
    assert prof['distinct_matrices']==prof['crt_matrices']==71547
    assert prof['rank_sum']==sum(t*n for t,n in enumerate(prof['blocks']))==h*prof['R']+2*prof['loss']
    assert original['histogram'][h]==h and prof['blocks'][h]>=h
    copied=list(prof['blocks']);copied[h]-=h;copied[1]+=h
    assert all(n>=0 for n in copied) and sum(t*n for t,n in enumerate(copied))==h*prof['R']+prof['loss']
    copies=p['N']//prof['v'];replacement=Counter({t:n*copies for t,n in enumerate(copied) if t and n})
    before=p['parts']['internal_23'];assert sum(t*n for t,n in before.items())==sum(t*n for t,n in replacement.items())
    p['parts']['internal_23']=replacement;hist=sum(p['parts'].values(),Counter())
    assert all(0<t<p['m'] and n>0 for t,n in hist.items())
    assert sum(t*n for t,n in hist.items())==p['total_rank']==p['W']*p['m']-p['N']+p['L']
    p['child_multiplicities']=dict(sorted(hist.items()));p['maxchild']=max(hist)
    p['fixed_first']=dict(basis='I+J',h=h,profile=prof,copied_blocks=copied,copies=copies,original_generic_internal=before,
        scope='Replace entire internal23 once;23 width23 cleanup calls become23 rank-one complements. Retained rank22 transform profiles remain. Fixed-middle25 and all other classes unchanged.')
    return p

def run():
    assert not sys.flags.optimize
    verify_sources();baseline=prior.run();bit=counts();bounds=crt.run()
    exact=moment(bit['m'],bit['W'],bit['child_multiplicities'],AB);assert exact['upper']<1
    old_at_new=moment(bit['m'],bit['W'],baseline['bit']['counts']['child_multiplicities'],AB);assert old_at_new['lower']>1
    next_bit=moment(bit['m'],bit['W'],bit['child_multiplicities'],AB+Q(1,10**14));assert next_bit['lower']>1
    _,phase_row,_=prior.prior.inputs();phase=prior.prior.inherited.profile([phase_row,phase_row])
    f=prior.prior.inherited.finite_bridge(bit,phase,[phase_row,phase_row]);assert js(f)==js(baseline['finite_bridge'])
    final=prior.balanced.assembly(f,AB,KAPPA,a_complex=AC);eventual=prior.balanced.cutoffs(f,final)
    negatives=[]
    for name,kw in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True)),('original_prefix',dict(original_prefix=True)),('next_kappa_grid',dict(kappa=KAPPA+Q(1,10**14)))]:
        try:prior.balanced.assembly(f,AB,kw.pop('kappa',KAPPA),a_complex=AC,**kw)
        except AssertionError:negatives.append(name)
        else:raise AssertionError('Negative control accepted: '+name)
    sources=dict(baseline['source_sha256']);sources.update(verify_sources()['sha256']);sources[str((HERE/'producer-source.json').relative_to(ROOT))]=sha256((HERE/'producer-source.json').read_bytes()).hexdigest()
    return dict(status='EXACT BOTHFIXED FINITE ARITHMETIC; FULL PAIRWISE GEOMETRY IS A SEPARATE REQUIRED PROOF GATE',parent_commit=INHERITED,
        bit=dict(counts=bit,**exact),complex=baseline['complex'],finite_bridge=f,assembly=final,eventual_bounds=eventual,crt_bound=bounds,
        previous=dict(kappa=prior.KAPPA,bit=prior.AB,old_profile_at_new_bit_lower=old_at_new['lower']),next_bit_grid=next_bit,
        negative_controls=negatives,ratio_to_PR39=KAPPA/prior.KAPPA,source_sha256=sources,
        scope='Both factors fixed I+J. Finite profiles/CRT/cost arithmetic cannot establish simultaneous data geometry. Full actual triple-pair nonvanishing, common physical interfaces, copied-stream scheduling and inherited analytic/tape transfer remain written proof obligations; no global optimality claim.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();result=run()
    if a.output:a.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
    print('PASS finite bit='+str(AB)+';kappa='+str(KAPPA)+';47constraints;7margins;p^2000;geometry gate separate')

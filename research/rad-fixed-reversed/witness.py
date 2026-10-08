#!/usr/bin/env python3
"""RaD alternating producers with complete I+J profiles and reversed corners.
RaD/hipotures authors changed DAGs and point orders; icekylinx supplies fixed
projector/copied-center primitives. James Chang, Zhihao Chen, Paureel,
Dominik Scholz, Rohan Arun, Swapnil Jain and earlier authors retain credits.
"""
from collections import Counter
from fractions import Fraction as Q
from math import comb
from hashlib import sha256
from pathlib import Path
import argparse,importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=load('rad_fixed_copied_base',ROOT/'research/copied-reversed/witness.py')
js,read,moment=base.js,base.read,base.moment
AB=Q(819932517,20000000000000);KAPPA=Q(4099494519,10**14);AC=base.AC
PR41=Q(1008542031,25000000000000)

def verify_sources():
    s=read(HERE/'source-manifest.json');assert s['pr41_source_commit']=='d9c96297d455053b795ee58ba108d5cf892e1c04'
    for name,digest in s['sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Source pin mismatch: '+name
    return s

def counts():
    inputs={h:read(HERE/f'input-{h}.json') for h in (23,25)};rows={h:x['original'] for h,x in inputs.items()};profiles={h:read(HERE/f'profile-{h}.json') for h in rows}
    m=23*25;N=comb(23,3)*comb(25,3);banks={h:N//r['v']*r['R'] for h,r in rows.items()};W=2*N+sum(banks.values());L=sum(N//r['v']*r['loss'] for h,r in rows.items());parts={};copied={}
    for h,r in rows.items():
        assert r['h']==h and r['v']==comb(h,3) and r['q']==3*r['v']+h and r['R']==r['c']+r['q']-r['matched']
        assert r['loss']==h*(h-1) and r['histogram'][h]==h
        assert all(inputs[h]['scalar'][k] for k in ['all_additions_disjoint','all_partial_outputs_exact','every_node_has_common_point'])
        f=profiles[h];assert f['h']==h and f['v']==r['v'] and f['R']==r['R'] and f['loss']==r['loss']
        assert f['crt_matrices']==f['distinct_matrices']>0
        assert sum(t*n for t,n in enumerate(f['blocks']))==f['rank_sum']==r['rank_sum']==h*r['R']+2*r['loss']
        hist=list(f['blocks']);assert hist[h]>=h;hist[h]-=h;hist[1]+=h;assert all(n>=0 for n in hist)
        assert sum(t*n for t,n in enumerate(hist))==h*r['R']+r['loss'];copied[h]=hist
        copies=N//r['v'];parts[f'internal_{h}']=Counter({t:n*copies for t,n in enumerate(hist) if t and n})
        parts[f'exterior_{h}']=Counter({h:banks[h],m-2*h:banks[h]});parts[f'growth_{h}']=Counter({1:2*N,h-2:2*N})
    parts['data']=Counter({1:9*2*N,21:2*N,17:2*N,481:2*N});parts['paid_correction']=Counter({1:N})
    z=sum(parts.values(),Counter());s=W*m-N+L;assert sum(t*n for t,n in z.items())==s and len(z)==26
    assert all(0<t<m and n>0 for t,n in z.items())
    return dict(dimensions=[23,25],m=m,N=N,W=W,L=L,total_rank=s,deficit=N-L,maxchild=max(z),banks=banks,parts=parts,child_multiplicities=dict(sorted(z.items())),inputs=inputs,original_profiles=profiles,copied_blocks=copied)

def run():
    assert not sys.flags.optimize
    verify_sources();b=counts();bm=moment(b['m'],b['W'],b['child_multiplicities'],AB);assert bm['upper']<1
    nxt=moment(b['m'],b['W'],b['child_multiplicities'],AB+Q(1,10**14));assert nxt['lower']>1
    _,pr,_=base.inputs();phase=base.inherited.profile([pr,pr]);cm=base.inherited.moment(phase['m'],phase['W'],phase['child_multiplicities'],AC,True)
    bridge=base.inherited.finite_bridge(b,phase,[pr,pr]);final=base.balanced.assembly(bridge,AB,KAPPA,a_complex=AC);cuts=base.balanced.cutoffs(bridge,final)
    negative=[]
    for name,kw in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True)),('original_prefix',dict(original_prefix=True)),('next_kappa_grid',dict(kappa=KAPPA+Q(1,10**14)))]:
        try:base.balanced.assembly(bridge,AB,kw.pop('kappa',KAPPA),a_complex=AC,**kw)
        except AssertionError:negative.append(name)
        else:raise AssertionError('Negative accepted: '+name)
    sources=dict(verify_sources()['sha256']);sources[str((HERE/'source-manifest.json').relative_to(ROOT))]=sha256((HERE/'source-manifest.json').read_bytes()).hexdigest()
    return dict(status='Conditional RaD changed-DAG fixed-basis witness; finite arithmetic and written transfer dependencies',bit=dict(counts=b,**bm),complex=dict(counts=phase,**cm),finite_bridge=bridge,assembly=final,eventual_bounds=cuts,next_bit_grid=nxt,negative_controls=negative,
        comparison=dict(PR41_source_commit='d9c96297d455053b795ee58ba108d5cf892e1c04',PR41_readme_commit='03bde70c0c2a453f1ceae20c619b602841405467',PR41_alternating_kappa=PR41,ratio=KAPPA/PR41),source_sha256=sources,
        scope='Actual alternating DAG original-envelope roles and complete fixed-I+J profiles, not positive-histogram substitution. Full copied schedules, simultaneous bases and inherited analytic/tape obligations remain separate proof dependencies; no global optimality claim.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args();r=run()
    if a.output:a.output.write_text(json.dumps(js(r),sort_keys=True,indent=2)+'\n')
    print('PASS bit='+str(AB)+'; kappa='+str(KAPPA)+';47constraints;7margins;26classes;p^2000')

#!/usr/bin/env python3
"""Exact finite certificate for split-pair skip-prefix networks.

Reuses PR53's exact transcendental enclosures, PR43/46/48 data recovery,
PR34/37 balanced assembly and PR36 copied-center/complex interfaces.
This finite check does not discharge the inherited all-size proof obligations.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import argparse,importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PARENT=ROOT/'research/skip-strips'
sys.path[:0]=[str(HERE),str(PARENT),str(ROOT/'scripts')]
from graph import graph
spec=importlib.util.spec_from_file_location('split_skip_base',PARENT/'verify.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
read,require,moment,js=base.read,base.require,base.moment,base.js
PR54=Q(4529040672,10**14)
GRID=10**14

def integer(x):
    require(type(x) is int and x>=0,'Nonnegative exact integer required')
    return x

def profile():
    m=575;N=4073300;L=2226400
    data=base.data_corners();require(data['good']==N and data['fallback']==0,'Data coverage')
    parts={'data':Counter({1:18*N,21:2*N,17:2*N,481:2*N}),
           'paid_endpoint_copy':Counter({1:N})}
    W=2*N
    for h in (23,25):
        r=read(HERE/f'original-{h}.json');f=read(HERE/f'profiles-{h}.json')
        for k in ('h','v','R','c','q','matched','rank_sum','loss'):integer(r[k])
        require(r['h']==h and r['v']==comb(h,3),'Axis dimensions')
        require(r['R']==r['c']+r['q']-r['matched'],'Role identity')
        require(r['loss']==h*(h-1),'Center loss')
        require(sum(t*integer(n) for t,n in enumerate(r['histogram']))==r['rank_sum']==h*r['R']+2*r['loss'],'Original mass')
        for k in ('h','v','R','rank_sum','loss'):require(f[k]==r[k],'Profile mismatch '+k)
        blocks=list(f['blocks']);require(len(blocks)==h+1 and blocks[0]==0 and blocks[h]==h,'Cleanup accounting')
        require(sum(t*integer(n) for t,n in enumerate(blocks))==r['rank_sum'],'Fixed mass')
        require(f['crt_disagreements']==0 and f['field_prime']==2**61-1,'CRT replay');base.exactness(h)
        blocks[h]-=h;blocks[1]+=h
        require(sum(t*n for t,n in enumerate(blocks))==h*r['R']+r['loss'],'Copied mass')
        rep=N//r['v'];bank=rep*r['R'];W+=bank
        parts[f'internal_{h}']=Counter({t:n*rep for t,n in enumerate(blocks) if t and n})
        parts[f'exterior_{h}']=Counter({h:bank,m-2*h:bank})
        parts[f'data_growth_{h}']=Counter({1:2*N,h-2:2*N})
    hist=sum(parts.values(),Counter());mass=sum(t*n for t,n in hist.items())
    require(mass==W*m-N+L,'Whole rank accounting')
    require(max(hist)==529 and all(0<t<m and n>0 for t,n in hist.items()),'Proper child widths')
    return dict(m=m,N=N,L=L,W=W,total_rank=mass,deficit=N-L,maxchild=529,
                child_multiplicities=dict(sorted(hist.items())),parts=parts)

def parameters():
    d=read(HERE/'parameters.json')
    require(d['grid_denominator']==GRID,'Parameter grid')
    return Q(integer(d['bit_numerator']),GRID),Q(integer(d['kappa_numerator']),GRID)

def bridge(p):
    prior=base.baseline.certificate();phase=prior['complex']['counts']
    row=read(ROOT/'certificates/copied-centers-complex-input.json')
    return base.baseline.finite_bridge(p,phase,[row,row]),prior

def search():
    p=profile();rows=p['child_multiplicities'];lo=1;hi=10**10
    while lo+1<hi:
        mid=(lo+hi)//2
        if moment(p['m'],p['W'],rows,Q(mid,GRID))['upper']<1:lo=mid
        else:hi=mid
    ab=Q(lo,GRID)
    require(moment(p['m'],p['W'],rows,Q(hi,GRID))['lower']>1,'Grid unresolved by enclosures')
    f,_=bridge(p);a=base.assembly(f,ab,Q(1,10**10),a_complex=base.AC)
    k=(a['minimum_margin']*GRID).__floor__()
    if Q(k,GRID)==a['minimum_margin']:k-=1
    d=dict(bit_numerator=lo,kappa_numerator=k,grid_denominator=GRID)
    (HERE/'parameters.json').write_text(json.dumps(d,indent=2)+'\n');return d

def pin():
    paths=[p for p in HERE.rglob('*') if p.is_file() and p.suffix in ('.py','.cpp','.uses','.json','.md')
           and p.name not in ('SOURCE.json','certificate.json','producer-receipt.json','validation.json')]
    paths += [p for p in PARENT.rglob('*') if p.is_file() and p.suffix in ('.py','.cpp','.uses','.json','.md')]
    paths += [p for p in (ROOT/'scripts').rglob('*') if p.is_file() and p.suffix in ('.py','.cpp','.hpp')]
    value={'parent_pr':53,'parent_commit':'3ffd4021995c959ac02d12920e0279ae97dd03c7',
           'PR54':{'consumed_commit':'7210de7d0f9ccaeb64c3f60f188419e02be08d95','latest_observed_commit':'84eb0b067741dc2690da837743fda06d133da865','difference':'Only validation.json changed; claim and replay sources unchanged','contribution':'Chafik Boukhalfa original-envelope paid-clone replay, deriving from RaD / hipotures PR51'},
           'files':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}}
    (HERE/'SOURCE.json').write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')

def run():
    require(not sys.flags.optimize,'Assertions required');base.check_sources()
    pins=read(HERE/'SOURCE.json')['files']
    required=[p for p in HERE.rglob('*') if p.is_file() and p.suffix in ('.py','.cpp','.uses','.json','.md') and p.name not in ('SOURCE.json','certificate.json','producer-receipt.json','validation.json')]
    require(all(str(p.relative_to(ROOT)) in pins for p in required),'Missing input source pin')
    for name,digest in pins.items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==digest,'Source pin: '+name)
    for h in (23,25):
        require(graph(h).verify()==read(HERE/f'scalar-{h}.json'),'Scalar graph replay mismatch')
        r=read(HERE/f'original-{h}.json');t=read(HERE/f'timeline-{h}.json')
        require(t['roles']==r['R'] and t['retained_links']==r['matched'],'Timeline allocation')
        require(t['copied_rank_sum']==h*r['R']+r['loss'],'Timeline mass')
        d=t['complete_dirty_basis']
        require(d['all_dirty_restore'] is True and d['auxiliary_basis_vectors']==r['R'] and
                d['total_basis_vectors']==2*r['v']+r['R'] and
                d['orientations']==['forward','reverse-complement'],'Dirty basis coverage')
    p=profile();ab,k=parameters();require(k>PR54,'Live PR54 comparison')
    exact=moment(p['m'],p['W'],p['child_multiplicities'],ab);require(exact['upper']<1,'Bit moment')
    nxt=moment(p['m'],p['W'],p['child_multiplicities'],ab+Q(1,GRID));require(nxt['lower']>1,'Next bit grid')
    f,prior=bridge(p);assembly=base.assembly(f,ab,k,a_complex=base.AC);cutoffs=base.cutoffs(f,assembly)
    require(len(assembly['constraints'])==47 and len(assembly['margins'])==7,'Assembly completeness')
    require(assembly['minimum_margin']<=k+Q(1,GRID),'Next final grid')
    old=base.profile();old_moment=moment(old['m'],old['W'],old['child_multiplicities'],ab)
    require(old_moment['lower']>1,'Old network exclusion')
    if (HERE/'comparison-pr54.json').exists():
        old54=read(HERE/'comparison-pr54.json');children={int(t):n for t,n in old54['child_multiplicities'].items()}
        comparison54=moment(old54['m'],old54['W'],children,ab)
        require(comparison54['lower']>1,'PR54 network exclusion')
    else: comparison54=None
    return dict(kappa=k,bit=dict(counts=p,**exact),next_bit_grid_lower=nxt['lower'],
        complex=prior['complex'],assembly=assembly,eventual_bounds=cutoffs,
        comparison=dict(PR53=base.KAPPA,PR54=PR54,ratio_PR54=k/PR54,
                        PR53_at_new=old_moment,PR54_at_new=comparison54),
        scope='Conditional on inherited analytic and finite-alphabet multitape framework; finite verification is not a full formal proof.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--search',action='store_true');ap.add_argument('--pin',action='store_true');ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    if args.search:print(search())
    if args.pin:pin()
    if not args.search:
        result=run()
        if args.output:args.output.write_text(json.dumps(js(result),sort_keys=True,indent=2)+'\n')
        print('PASS kappa='+str(result['kappa'])+' = '+str(float(result['kappa']))+'; 47 constraints; seven margins')

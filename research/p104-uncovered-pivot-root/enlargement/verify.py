"""Exact finite mask-enlargement exclusion. Standard library only.
By @CubeJerry with substantial OpenAI GPT-6 assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
import types
HERE=Path(__file__).resolve().parent
SCALE=10**18

def need(ok,message):
    if not ok:raise RuntimeError(message)

def load_source(name,path,digest):
    raw=path.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==digest,'root dependency SHA256')
    mod=types.ModuleType(name);mod.__file__=str(path);sys.modules[name]=mod
    exec(compile(raw,str(path),'exec'),mod.__dict__)
    return mod

def basis(rows,gcd):
    out=[];pivots=[]
    for source in rows:
        v=source[:]
        for w,j in zip(out,pivots):
            if v[j]:
                x,y=w[j],v[j];v=[x*a-y*b for a,b in zip(v,w)]
                divisor=0
                for z in v:divisor=gcd(divisor,z)
                if divisor:v=[z//divisor for z in v]
        j=next((j for j,z in enumerate(v) if z),None)
        if j is not None:
            out.append(v);pivots.append(j)
            if len(out)==len(v):break
    return out

def capacity(rows_a,rows_b,dimension,root):
    if not dimension:return 0
    a=basis(rows_a,root.gcd)
    if len(a)==dimension:return 0
    b=basis(rows_b,root.gcd)
    if len(b)==dimension:return 0
    product=root.mm(a,list(zip(*b))) if a and b else []
    return dimension-len(a)-len(b)+(root.rank(product) if product else 0)

def geometry(root):
    r=root.family(18,8);u=root.eye(18);v=root.eye(18)
    aa=[];bb=[];old=[];prefixes=[]
    for e in r['events']:
        if e['site'] is not None:
            aa.append([root.dot(e['y'],col) for col in zip(*u)])
            bb.append([root.dot(row,e['x']) for row in v])
            old.append(set(e['mask']));prefixes.append(u)
        inv=[[int(i==j)+2*e['x'][i]*e['y'][j] for j in range(18)] for i in range(18)]
        u=root.mm(root.query(e),u);v=root.mm(v,inv)
    return r,aa,bb,old,prefixes

def mask_family(kl,kr,r,old):
    masks=[s.copy() for s in old]
    left=[r['names'].index(f'F{i}') for i in range(8-kl,8)]
    right=[r['names'].index(f'F{i}') for i in range(9,9+kr)]
    for i in range(8):masks[i].update(right)
    for i in range(9,18):masks[i].update(left)
    return masks

def feasible_jobs(masks,a,b,root):
    """All positive-capacity supports in the query-only relaxation.

    Exact cache keys retain common coordinates and both normalized row sets;
    row order/multiplicity and nonzero row scaling do not change any rank.
    """
    jobs=[];coordinate_cache={};rank_cache={}
    mask_bits=[sum(1<<c for c in mask) for mask in masks]
    def normalized(row):
        divisor=0
        for x in row:divisor=root.gcd(divisor,x)
        if not divisor:return tuple(row)
        if next(x for x in row if x)<0:divisor=-divisor
        return tuple(x//divisor for x in row)
    def cap(sites):
        common=(1<<18)-1
        for i in sites:common &= mask_bits[i]
        if not common:return 0
        if common not in coordinate_cache:
            cols=[c for c in range(18) if common>>c&1]
            ar=[normalized([a[i][c] for c in cols]) for i in range(18)]
            br=[normalized([b[i][c] for c in cols]) for i in range(18)]
            av=sorted(set(ar));bv=sorted(set(br))
            coordinate_cache[common]=(len(cols),av,bv,[1<<av.index(v) for v in ar],[1<<bv.index(v) for v in br])
        dimension,av,bv,ai,bi=coordinate_cache[common]
        ak=bk=0
        for i in sites:ak |= ai[i];bk |= bi[i]
        key=(common,ak,bk)
        if key not in rank_cache:
            ra=[list(v) for j,v in enumerate(av) if ak>>j&1]
            rb=[list(v) for j,v in enumerate(bv) if bk>>j&1]
            rank_cache[key]=capacity(ra,rb,dimension,root)
        return rank_cache[key]
    def grow(sites,start):
        for i in range(start,18):
            new=sites+(i,)
            if cap(new):jobs.append(new);grow(new,i+1)
    grow((),0)
    for i in range(18):need(cap((i,))==len(masks[i])-2,'single-site rank demand')
    return jobs

def dual_lower(weights,jobs,costs,demand):
    need(len(weights)==18 and all(isinstance(x,int) and x>=0 for x in weights),'integer prices')
    for job in jobs:
        need(sum(weights[i] for i in job)<=costs[len(job)],'infeasible site-price certificate')
    return sum(x*y for x,y in zip(weights,demand))

@lru_cache(None)
def derivative_terms(r,audit):
    lo,hi=audit.log_bounds(r)
    return r*hi,r*audit.exp_negative(Fraction('0.01')*hi)[0]*lo

def derivative_upper(target,demand,native_t,native_p,audit):
    ferrers=[sum(x>=j for x in demand) for j in range(1,max(demand)+1)]
    paid=Counter({r:18*c for r,c in native_p.items()})
    paid.update({8*m:104*ferrers.count(m) for m in set(ferrers)})
    targets=Counter({r:18*c for r,c in native_t.items()})
    targets.update({r:104*c for r,c in target.items()})
    positive=sum(c*derivative_terms(r,audit)[0] for r,c in paid.items())
    negative=sum(c*derivative_terms(r,audit)[1] for r,c in targets.items())
    return positive-negative

def rejected(action,name):
    try:action()
    except RuntimeError:return name
    raise RuntimeError('negative control accepted: '+name)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root-package',type=Path,default=HERE.parent)
    parser.add_argument('--write-receipt',action='store_true');args=parser.parse_args()
    pins=json.loads((HERE/'SOURCE-PINS.json').read_text())['files']
    root=load_source('pivot_root',args.root_package/'check.py',pins['check.py'])
    audit=load_source('pivot_accounting',args.root_package/'accounting/verify.py',pins['accounting/verify.py'])
    native_t,native_p=audit.source_census()
    cert=json.loads((HERE/'DUALS.json').read_text())
    need(cert['scale']==SCALE and cert['kappa']=='0.00337180' and cert['pivot']==8,'certificate parameters')
    rows=cert['cases'];need([(z['kl'],z['kr']) for z in rows]==[(i,j) for i in range(9) for j in range(10)],'exact90case coverage')
    kappa=Fraction(cert['kappa']);costs=[0]+[(audit.power_bounds(8*m,kappa)[0]*SCALE).__floor__() for m in range(1,19)]
    r,a,b,old,prefixes=geometry(root);reports=[];total_jobs=0
    for row in rows:
        kl,kr=row['kl'],row['kr'];masks=mask_family(kl,kr,r,old)
        for mask,u in zip(masks,prefixes):
            need(all(not u[i][j] or ((i in mask)==(j in mask)) for i in range(18) for j in range(18)), 'enlarged mask not prefix invariant')
        demand=[len(s)-2 for s in masks]
        jobs=feasible_jobs(masks,a,b,root);total_jobs+=len(jobs)
        need(len(jobs)==row['feasible_jobs'],'feasible-job count')
        value=dual_lower(row['weights'],jobs,costs,demand)
        need(value==row['paid_lower_units'],'site price objective')
        target=Counter(8*sum(c in s for s in masks)+1 for c in range(18))
        _,_,signed=audit.complete(target,Counter({1:1,8:sum(demand)}),native_t,native_p)
        signed[8]+=104*sum(demand)
        upper=audit.moment(signed,kappa)[1]-104*Fraction(value,SCALE)
        upper_units=(upper*SCALE).__ceil__()
        need(upper_units==row['margin_upper_units'] and upper_units<0,'complete margin sign/binding')
        derivative=derivative_upper(target,demand,native_t,native_p,audit)
        derivative_units=(derivative*SCALE).__ceil__()
        need(derivative_units<0,'uniform derivative bound')
        reports.append(dict(kl=kl,kr=kr,feasible_jobs=len(jobs),margin_upper_units=upper_units,derivative_upper_units=derivative_units))
    controls=[]
    need(capacity([[1,0]],[[1,0]],2,root)==1,'pairing product term necessary')
    need(capacity([[1,0]],[[0,1]],2,root)==0,'dual annihilation necessary')
    first=rows[0];masks=mask_family(0,0,r,old);jobs=feasible_jobs(masks,a,b,root)
    bad=first['weights'][:];bad[8]=costs[1]+1
    controls.append(rejected(lambda:dual_lower(bad,jobs,costs,[len(s)-2 for s in masks]),'price exceeds singleton cost'))
    controls.append(rejected(lambda:dual_lower([costs[1]]*18,jobs,costs,[len(s)-2 for s in masks]),'unpriced multi-site merge'))
    need(capacity([[a[1][0]],[a[9][0]]],[[b[1][0]],[b[9][0]]],1,root)==0,'original opposite-arm obstruction')
    need(max(z['derivative_upper_units'] for z in reports)<-166817*SCALE,'reported uniform derivative bound')
    result=dict(status='PASS_PIVOT_ENLARGED_MASKS',cases=90,scale=SCALE,kappa='0.00337180',
        derivative_interval=['0','0.01'],total_feasible_jobs=total_jobs,
        largest_margin_upper_units=max(z['margin_upper_units'] for z in reports),
        largest_derivative_upper_units=max(z['derivative_upper_units'] for z in reports),
        negative_controls=controls,case_bounds=reports,
        scope='Finite90 minimal-root mask enlargements; ordinary data-independent whole-field carriers, literal query transport, unchanged native profile; no new kappa')
    path=HERE/'RESULT.json'
    if args.write_receipt:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    need(path.exists() and json.loads(path.read_text())==result,'stored receipt')
    print(json.dumps({k:v for k,v in result.items() if k!='case_bounds'},indent=2,sort_keys=True))
    print('PASS_PIVOT_ENLARGED_MASKS')

if __name__=='__main__':main()

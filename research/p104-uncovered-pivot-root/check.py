"""Exact uncovered-pivot roots, stdlib only. By @CubeJerry with substantial
OpenAI GPT-6 assistance. Credit DreamingOfClouds #6833/#6868. Apache-2.0.
"""
from copy import deepcopy
from decimal import Decimal, localcontext
from math import gcd
import hashlib
import json
import sys
from pathlib import Path

def require(ok, message):
    if not ok: raise RuntimeError(message)

def dot(a, b): return sum(x*y for x,y in zip(a,b))
def eye(n): return [[int(i==j) for j in range(n)] for i in range(n)]
def mm(a,b): return [[dot(row,col) for col in zip(*b)] for row in a]

def rank(a):
    a=[row[:] for row in a]; r=0
    for j in range(len(a[0])):
        k=next((k for k in range(r,len(a)) if a[k][j]),None)
        if k is None: continue
        a[r],a[k]=a[k],a[r]
        for k in range(r+1,len(a)):
            if a[k][j]:
                v,w=a[r][j],a[k][j]
                a[k]=[v*x-w*y for x,y in zip(a[k],a[r])]
                d=0
                for x in a[k]: d=gcd(d,x)
                if d: a[k]=[x//d for x in a[k]]
        r+=1
    return r

def family(n,p):
    require(n>=2 and n%2==0 and 0<=p<n,'bad family parameters')
    names=['A']+[f'F{i}' for i in range(n) if i!=p]
    f={i:names.index(f'F{i}') for i in range(n) if i!=p}; events=[]
    for i in range(n):
        x,y=[0]*n,[0]*n; y[0]=1
        if i<p:
            x[0],x[f[i]],y[f[i]]=1,-1,1
            for j in range(i): x[f[j]]=-2
            mask=[0]+[f[j] for j in range(i+1)]
        elif i>p:
            x[0],x[f[i]],y[f[i]]=-1,1,1
            for j in range(i+1,n): x[f[j]]=2
            mask=[0]+[f[j] for j in range(i,n)]
        else:
            for j,c in f.items(): x[c]=-1 if j<p else 1
            mask=list(range(n))
        events.append(dict(site=i,x=x,y=y,mask=mask))
        if i==p:
            x,y=[0]*n,[0]*n; x[0]=-1; u=2 if p%2==0 else 0; y[0]=u
            for j,c in f.items():
                if j>p: x[c]=2
                y[c]=(u-1)*(-1)**(j if j<p else n-1-j)
            events.append(dict(site=None,x=x,y=y,mask=[]))
    return dict(length=n,pivot=p,names=names,events=events)

def query(e):
    n=len(e['x'])
    return [[int(i==j)-2*e['x'][i]*e['y'][j] for j in range(n)] for i in range(n)]

def root_check(r):
    n,es=r['length'],r['events']
    for i,a in enumerate(es):
        for j,b in enumerate(es):
            require(dot(a['y'],b['x'])==(i>j)-(i<j),'sign Gram')
    prod=eye(n)
    for e in es:
        prod=mm(query(e),prod)
        if e['site'] is not None:
            require(all(not v or i in e['mask'] for z in (e['x'],e['y']) for i,v in enumerate(z)), 'query outside mask')
    require(prod==[[-int(i==j) for j in range(n)] for i in range(n)],'-I endpoint')
    suffix=eye(n)
    for e in reversed(es):
        if e['site'] is not None:
            m=set(e['mask'])
            require(all(not suffix[i][j] or ((i in m)==(j in m)) for i in range(n) for j in range(n)), 'D-factor commutation')
        suffix=mm(suffix,query(e))

def add(dst,src,factor):
    for power,value in src.items():
        v=dst.get(power,0)+factor*value
        if v: dst[power]=v
        else: dst.pop(power,None)

def polynomial_check(r,s):
    # Independently multiply literal maps over Z[D_0,...,D_(n-1)].
    # Monomials are bitsets; all input columns remain independent.
    n=r['length']; a=[[{0:1} if i==j else {} for j in range(n)] for i in range(n)]
    targets=[0]*n
    for e in r['events']:
        for col in range(n):
            v={}
            for row,c in enumerate(e['y']):
                if c: add(v,a[row][col],c)
            for row,c in enumerate(e['x']):
                if c: add(a[row][col],v,(s-1)*c)
        if e['site'] is not None:
            bit=1<<e['site']
            for row in e['mask']:
                targets[row]|=bit
                for col in range(n):
                    require(not any(m&bit for m in a[row][col]),'repeated variable')
                    a[row][col]={m|bit:c for m,c in a[row][col].items()}
    expected=[[{targets[i]:s} if i==j else {} for j in range(n)] for i in range(n)]
    require(a==expected,'arbitrary-input polynomial endpoint')

def transport_check(r):
    # Independent exact nullspace test, not the endpoint proof.
    n,p,es=r['length'],r['pivot'],r['events']; checks=0
    for source,a in enumerate(es):
        if a['site'] is None or a['site']>=p: continue
        h=eye(n)
        for target in range(source+1,len(es)):
            b=es[target]
            if b['site'] is not None and b['site']>p:
                cols=a['mask']; constraints=[[a['y'][k] for k in cols]]
                constraints += [[h[row][k] for k in cols] for row in range(n) if row not in b['mask']]
                require(rank(constraints)==len(cols),'nonzero cross-side idle carrier')
                checks+=1
            h=mm(query(b),h)
    return checks

def masks(r):
    return {name:[e['site'] for e in r['events'] if e['site'] is not None and c in e['mask']] for c,name in enumerate(r['names'])}

def rejected(action,name):
    try: action()
    except RuntimeError: return name
    raise RuntimeError('negative control accepted: '+name)

def verify_source(data,row):
    require(hashlib.sha256(data).hexdigest()==row['sha256'],'retained SHA256')
    framed=b'blob '+str(len(data)).encode()+b'\0'+data
    require(hashlib.sha1(framed).hexdigest()==row['git_blob'],'retained Git blob')

def main():
    package=Path(__file__).parent
    source_rows=json.loads((package/'PROVENANCE.json').read_text())['sources']
    for row in source_rows: verify_source((package/row['retained_path']).read_bytes(),row)
    roots=transports=0
    for n in range(2,21,2):
        for p in range(n):
            r=family(n,p); root_check(r); polynomial_check(r,-1); polynomial_check(r,1)
            transports+=transport_check(r); fm=masks(r)
            for i in range(n):
                if i!=p: require(fm[f'F{i}']==list(range(min(i,p),max(i,p)+1)),'field interval')
            roots+=1
    require(25**25<16**16*9**18,'L4 proxy sign')
    require(33**33<24**24*9**18,'L6 proxy sign')
    require(41**41>32**32*9**18,'L8 proxy sign')
    require(81**81>72**72*9**18,'L18 proxy sign')
    r=family(18,8); controls=[]
    first=source_rows[0]
    controls.append(rejected(lambda:verify_source((package/first['retained_path']).read_bytes()+b' ',first),'corrupted retained source'))
    bad=deepcopy(r); next(e for e in bad['events'] if e['site'] is None)['y'][0]+=1
    controls.append(rejected(lambda:root_check(bad),'wrong thin coefficient'))
    controls.append(rejected(lambda:polynomial_check(bad,-1),'wrong thin polynomial'))
    bad=deepcopy(r); next(e for e in bad['events'] if e['site']==8)['mask'].remove(1)
    controls.append(rejected(lambda:polynomial_check(bad,-1),'omitted pivot D'))
    bad=deepcopy(r); next(e for e in bad['events'] if e['site']==0)['mask'].append(10)
    # Enlarging this prefix mask is legal: the altered target must change too.
    root_check(bad); polynomial_check(bad,-1)
    bad=deepcopy(r); bad['events']=[e for e in bad['events'] if e['site'] is not None]
    controls.append(rejected(lambda:polynomial_check(bad,-1),'deleted thin query'))
    pivot=next(e for e in r['events'] if e['site']==8)
    for col in range(1,18):
        gamma=[0]*18; gamma[0],gamma[col]=2,1
        require(dot(gamma,pivot['x']) in (-1,1),'naive field idle crosses pivot')
    with localcontext() as ctx:
        ctx.prec=60; f=lambda x:Decimal(x)*Decimal(x).ln() if x else Decimal(0)
        c=lambda m:f(8*m+1)-f(8*m-8)
        deltas={str(n):str(c(n//2+1)-2*c(1)) for n in range(4,19,2)}
    fm=masks(r)
    target_mass=sum(8*len(m)+1 for m in fm.values())
    proxy_paid=1+sum(8*(len(m)-1) for f,m in fm.items() if f!='A')
    physical_paid=1+8*sum(len(e['mask'])-2 for e in r['events'] if e['site'] is not None)
    require(target_mass-proxy_paid==297,'proxy mass calculation')
    require(target_mass-physical_paid==305,'physical mass calculation')
    result=dict(status='PASS_UNCOVERED_PIVOT_ROOT',roots_checked=roots,retained_sources=len(source_rows),
        polynomial_replays=2*roots,cross_side_nullspaces=transports,negative_controls=controls,
        l18_pivot=8,l18_field_masks=masks(r),proxy_delta_vs_chain=deltas,
        proxy_rank_surplus=target_mass-proxy_paid,physical_rank_surplus=target_mass-physical_paid,
        scope='Root algebra, exact query transport and proxy accounting; no kappa claim')
    path=Path(__file__).with_name('RESULT.json')
    if '--write-receipt' in sys.argv:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    require(path.exists(),'missing receipt: regenerate with --write-receipt')
    require(json.loads(path.read_text())==result,'receipt mismatch')
    print(json.dumps(result,indent=2,sort_keys=True)); print('PASS_UNCOVERED_PIVOT_ROOT')

if __name__=='__main__': main()

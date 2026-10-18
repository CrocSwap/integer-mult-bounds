"""Independent exact rational brackets and Git provenance for the scoped #2847 audit.
No imported producer arithmetic is used for the interval computations.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib, importlib.util, json, subprocess, sys
P=Path('/tmp/pr-efficient1800'); root=P/'sources/2847'; pkg=root/'research/t74-retired7-increment-audit'; repo=Path('/tmp/integer-mult-efficient1100-20261015')
spec=importlib.util.spec_from_file_location('increment_audit',pkg/'increment_audit.py'); A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
rows=[]; data={}
for key,(ck,path,sha) in sorted(A.PINS.items()):
    commit=A.COMMIT[ck]
    blob=subprocess.check_output(['git','rev-parse',commit+':'+path],cwd=repo,text=True).strip()
    raw=subprocess.check_output(['git','cat-file','blob',blob],cwd=repo)
    assert hashlib.sha256(raw).hexdigest()==sha,(key,path)
    rows.append(dict(key=key,commit=commit,path=path,git_blob=blob,sha256=sha))
    if key in ('K2766_own','CLAIM'): data[key]=json.loads(raw)
sources=json.loads((pkg/'SOURCES.json').read_text())
for item in sources['files']:
    blob=subprocess.check_output(['git','rev-parse',sources['base_commit']+':'+item['path']],cwd=repo,text=True).strip()
    raw=subprocess.check_output(['git','cat-file','blob',blob],cwd=repo)
    assert blob==item['git_blob'] and hashlib.sha256(raw).hexdigest()==item['sha256']
    rows.append(dict(item,commit=sources['base_commit']))
# For 1 <= q <= 2, log(q)=2 sum z^(2j+1)/(2j+1), z=(q-1)/(q+1).
# Tail <= 2*z^(2N+1)/((2N+1)*(1-z*z)). Every operation below is rational.
def log_small(q,N=50):
    z=(q-1)/(q+1); assert 0<=z<=F(1,3)
    s=sum((2*z**(2*j+1)/F(2*j+1) for j in range(N)),F(0))
    return s,s+2*z**(2*N+1)/((2*N+1)*(1-z*z))
log2=log_small(F(2))
def log_bounds(q):
    k=0
    while q>=2:q/=2;k+=1
    lo,hi=log_small(q)
    return lo+k*log2[0],hi+k*log2[1]
Q=10**45
def rounded(v,up):
    n=v.numerator*Q; d=v.denominator
    return F((n+d-1)//d if up else n//d,Q)
def exp_bounds(x,N=24):
    assert 0<=x<1
    term=F(1);s=term
    for j in range(1,N+1):term=term*x/j;s+=term
    nxt=term*x/(N+1)
    return s,s+nxt/(1-x/(N+2))
def moment(profile,a):
    lo=hi=F(0)
    for r,n in profile.items():
        r=int(r); n=int(n); assert 0<r<73 and n>=0
        l,u=log_bounds(F(73,r));l=rounded(a*l,False);u=rounded(a*u,True)
        lo+=F(n*r,73)*exp_bounds(l)[0]
        hi+=F(n*r,73)*exp_bounds(u)[1]
    return lo,hi
receipt=json.loads((pkg/'RECEIPT.json').read_text());r5=receipt['rules']['ATTRIBUTION-RETIRED5']['info']
items=[('retired7',data['CLAIM']['profile'],F(A.CLAIMED['C'])),('retired5',r5['retired5_complete'],F(r5['retired5_root_in'][0])),('PR2766',data['K2766_own']['profile'],F(data['K2766_own']['complex_lower']))]
results=[]
for name,profile,a in items:
    low=moment(profile,a);high=moment(profile,a+F(1,10**24))
    assert low[1]<66304<high[0],name
    assert low[1]-low[0]<F(1,10**30) and high[1]-high[0]<F(1,10**30)
    results.append(dict(name=name,profile=profile,root_low=str(a),root_high=str(a+F(1,10**24)),lower_endpoint_below=True,upper_endpoint_above=True,interval_width_below='1e-30'))
# Test the exact replay's word reduction independently of its interned representation.
import random
rng=random.Random(2847);words=A.Words();checks=0
for _ in range(500):
    wid=0; plain=[]
    for _ in range(30):
        op=rng.choice((-3,-2,-1,1,2,3));wid=words.lmul(op,wid)
        plain=plain[1:] if plain and plain[0]==-op else [op]+plain
        got=[];q=wid
        while q:got.append(words.first[q]);q=words.rest[q]
        assert got==plain;checks+=1
out=dict(status='passed',git_bindings=rows,exact_rational_brackets=results,independent_free_word_steps=checks,scope='Input authentication, three exact rational moment brackets and free-word cancellation controls. Full circuit/controls replay required separately; no native or outer theorem admission.')
(P/'provenance-2847.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(rows),'Git bindings;',len(results),'exact rational brackets;',checks,'free-word checks')

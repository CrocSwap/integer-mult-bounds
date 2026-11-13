"""Fixed-grid signed Laurent replay with exact caller odd denominators."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
from math import prod

root=Path(__file__).resolve().parent
cpath=root/"ODD-TYPE-AB-CALLER.json"
C=json.loads(cpath.read_bytes())
primes=(2,3,5)
def debt(q):
    d=Q(q).denominator
    out=[]
    for p in primes:
        n=0
        while d%p==0:d//=p;n+=1
        out.append(n)
    assert d==1
    return out
def plus(a,b):return [x+y for x,y in zip(a,b)]
def vmax(a,b):return list(map(max,a,b))
def valuation_budget():
    D=[[0]*len(primes) for _ in range(C["roles"])]
    peak=[0]*len(primes)
    for e in C["events"]:
        if e[0]=="J":
            _,_,(u,v,x,y),(s,t,al,be)=e
            assert al=="-1" and be=="1/2" and abs(Q(C["types"]["A"]["alpha2"]))==1
            D[v]=vmax(D[u],D[v]);D[x]=vmax(D[x],D[y])
            tmp=vmax(D[s],D[t]);D[s],D[t]=tmp,plus(tmp,[1,0,0])
        else:
            _,op,r,*a=e
            if op=="SWAP":D[r],D[a[0]]=D[a[0]],D[r]
            elif op=="QUERY":D[r]=vmax(D[r],D[a[0]])
            elif op=="LAMBDA":D[r]=plus(D[r],[1,0,0])
            elif op=="ADD":
                d=plus(D[a[0]],debt(a[1]))
                peak=vmax(peak,d)
                D[r]=vmax(D[r],d)
            elif op=="SCALE":D[r]=plus(D[r],debt(a[0]))
            else:assert op in ("IDLE_ONE","IDLE_ODD")
        for d in D:peak=vmax(peak,d)
    return peak

def replay(ds):
    M=prod(p**e for p,e in zip(primes,ds))
    rows=[{(j,0,0):(M,0)} for j in range(C["roles"])]
    peak=0
    checks=0
    def field_add(out,x,ar=1,ai=0,den=1,q=0,m=0):
        nonlocal checks
        for (j,k,s),(a,b) in x.items():
            u,v=a*ar-b*ai,a*ai+b*ar
            if den!=1:
                u,ru=divmod(u,den);v,rv=divmod(v,den)
                if ru or rv:raise ArithmeticError("Nonintegral caller coefficient")
                checks+=1
            key=(j,(k+q)%4,s+m)
            c,d=out.get(key,(0,0))
            uv=(c+u,d+v)
            if uv==(0,0):out.pop(key,None)
            else:out[key]=uv
    def mapped(x,ar=1,ai=0,den=1,q=0,m=0):
        y={};field_add(y,x,ar,ai,den,q,m);return y
    def mulrank(j):
        return 1<<(8*(j-1))
    for e in C["events"]:
        if e[0]=="J":
            _,j,(u,v,x,y),(s,t,al,be)=e
            m=mulrank(j)
            field_add(rows[v],rows[u],q=-1)
            field_add(rows[x],rows[y],int(C["types"]["A"]["alpha2"]),q=1)
            for r in (u,v,x,y):rows[r]=mapped(rows[r],m=m)
            A=mapped(rows[s],m=m);field_add(A,rows[t],-1,q=1,m=m)
            B=mapped(rows[t],den=2,m=m);field_add(B,rows[s],den=2,q=-1,m=m)
            rows[s],rows[t]=A,B
        else:
            _,op,r,*a=e
            if op=="SWAP":rows[r],rows[a[0]]=rows[a[0]],rows[r]
            elif op=="QUERY":field_add(rows[r],rows[a[0]],q=a[1])
            elif op=="LAMBDA":
                x=rows[r];rows[r]=mapped(x,1,a[0],2)
                field_add(rows[r],x,1,-a[0],2,q=2)
            elif op=="ADD":
                q=Q(a[1]);field_add(rows[r],rows[a[0]],q.numerator,den=q.denominator)
            elif op=="SCALE":
                q=Q(a[0]);rows[r]=mapped(rows[r],q.numerator,den=q.denominator)
            else:
                assert op in ("IDLE_ONE","IDLE_ODD")
                rows[r]=mapped(rows[r],q=a[1] if op=="IDLE_ODD" else 0,m=sum(map(mulrank,a[0])))
        peak=max(peak,sum(map(len,rows)))
    for ty,t in C["types"].items():
        for j,(q,z,*bits) in enumerate(t["diagonal"],t["offset"]):
            assert z==0
            assert rows[j]=={(j,q%4,sum(v<<(8*k) for k,v in enumerate(bits))):(M,0)}
    return checks,peak

ds=valuation_budget()
checks,peak=replay(ds)
odd=prod(p**e for p,e in zip(primes[1:],ds[1:]))
assert odd>1
# Locate the least exact odd-scale exponents on this interpreter. Since
# the coefficient grid requirements are per prime, monotonicity permits
# independent integer binary searches while holding the other primes fixed.
bound=ds.copy()
for i in range(1,len(ds)):
    lo,hi=-1,ds[i]
    while hi-lo>1:
        mid=(lo+hi)//2
        test=ds.copy();test[i]=mid
        try:replay(test)
        except ArithmeticError:lo=mid
        else:hi=mid
    ds[i]=hi
checks,peak=replay(ds)
odd=prod(p**e for p,e in zip(primes[1:],ds[1:]))
assert odd>1
for i in range(1,len(ds)):
    if ds[i]:
        short=ds.copy();short[i]-=1
        try:replay(short)
        except ArithmeticError:pass
        else:raise AssertionError("odd-grid rejection control")
rec={"caller_sha256":sha256(cpath.read_bytes()).hexdigest(),"prime_order":list(primes),
     "safe_valuation_bound":bound,"grid_exponents":ds,"caller_odd_scale":str(odd),
     "caller_odd_scale_bits":odd.bit_length(),"preproduct_exact_divisions":checks,
     "peak_terms":peak,
     "scope":"Independent integer Laurent caller endpoint and pre-product divisibility. Valuation bound propagates complete field operators whose Gaussian coefficients have only power-of-two denominators, so odd factors are sourced only from the charged scalar operations. Fixed conversion and storage bounds still needed."}
with (root/"ODD-CALLER-EXACT-GRID.json").open("x") as f:json.dump(rec,f,indent=2)
print("PASS odd caller grid",bound,ds,"scale bits",odd.bit_length(),"checked",checks,flush=True)

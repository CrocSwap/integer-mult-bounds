import sys,re
from math import gcd
from functools import reduce
from fractions import Fraction as Fr
A=[[2,0,-1,0,0,0,0,0],[0,2,0,-1,0,0,0,0],[-1,0,2,-1,0,0,0,0],[0,-1,-1,2,-1,0,0,0],[0,0,0,-1,2,-1,0,0],[0,0,0,0,-1,2,-1,0],[0,0,0,0,0,-1,2,-1],[0,0,0,0,0,0,-1,2]]
def inv(Mx):
    n=8;a=[[Fr(x) for x in r]+[Fr(int(i==j)) for j in range(n)] for i,r in enumerate(Mx)]
    for c in range(n):
        p=next(r for r in range(c,n) if a[r][c]!=0);a[c],a[p]=a[p],a[c]
        pv=a[c][c];a[c]=[x/pv for x in a[c]]
        for r in range(n):
            if r!=c and a[r][c]!=0:
                f=a[r][c];a[r]=[x-f*y for x,y in zip(a[r],a[c])]
    return [r[n:] for r in a]
Ai=inv(A)
def nullspace(M,ncol):
    M=[r[:] for r in M];piv=[];r=0
    for c in range(ncol):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r];pv=M[r][c];M[r]=[x/pv for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0:
                f=M[i][c];M[i]=[x-f*y for x,y in zip(M[i],M[r])]
        piv.append(c);r+=1
    free=[c for c in range(ncol) if c not in piv];ns=[]
    for f in free:
        v=[Fr(0)]*ncol;v[f]=Fr(1)
        for i,c in enumerate(piv): v[c]=-M[i][f]
        ns.append(v)
    return ns

def canon(v):
    g=reduce(gcd,[abs(int(x)) for x in v]);v=[int(x)//g for x in v]
    for x in v:
        if x: 
            if x<0: v=[-y for y in v]
            break
    return tuple(v)
def refl(i,v): # s_i in root coords
    k=sum(A[i][j]*v[j] for j in range(8)); w=list(v); w[i]-=k; return tuple(w)
roots=[]
_q=[tuple(int(i==j) for j in range(8)) for i in range(8)];_s=set(_q)
while _q:
    r=_q.pop()
    roots.append(r)
    for i in range(8):
        y=canon(refl(i,r))
        if y not in _s:_s.add(y);_q.append(y)
roots=sorted(roots)
assert len(roots)==120
def ipf(x,y): return sum(x[i]*A[i][j]*y[j] for i in range(8) for j in range(8))
def mask(x): return frozenset(t for t,r in enumerate(roots) if ipf(r,x)!=0)
Ss=[0x01,0x02,0x40,0x81,0xc0,0x80];gen=[0,0,0,1,1,0]
D4=[];typ=[]
for k,S in enumerate(Ss):
    v=[0]*8
    for i in range(8):
        if S>>i&1:
            for j in range(8): v[j]+=int(Ai[i][j])*(1 if True else 1)*(1+ (0))
    # generic point: weights 1 each (fine for support S)
    o=[canon(v)];seen={mask(o[0])}
    q=0
    while q<len(o):
        for i in range(8):
            y=canon(refl(i,o[q]));my=mask(y)
            if my not in seen: seen.add(my);o.append(y)
        q+=1
    D4+=o;typ+=[k]*len(o)
print("nd4",len(D4),file=sys.stderr)
def check(line):
    m=re.search(r'b (\d+) c (\d+) d (\d+) \| hab (\d+) hac (\d+) had (\d+) hbc (\d+) hbd (\d+) hcd (\d+)',line)
    b,c,d,hab,hac,had,hbc,hbd,hcd=map(int,m.groups())
    t=[typ[x] for x in (hab,hac,had,hbc,hbd,hcd)]
    if any(gen[x] for x in t): return 'GEN',t
    Av,Cv,Kv,Bc,Bd,Cd=[[Fr(y) for y in D4[x]] for x in (hab,hac,had,hbc,hbd,hcd)]
    M=[[Fr(0)]*6 for _ in range(24)]
    for i in range(8):
        M[i][0]=Av[i];M[i][1]=-Cv[i];M[i][3]=-Bc[i]
        M[8+i][0]=Av[i];M[8+i][2]=-Kv[i];M[8+i][4]=-Bd[i]
        M[16+i][1]=Cv[i];M[16+i][2]=-Kv[i];M[16+i][5]=-Cd[i]
    ns=nullspace(M,6)
    if not ns: return 'NOSOL',t
    import random
    for _ in range(5):
        w=[sum(random.randint(1,7)*v[k] for v in ns) for k in range(6)]
        if all(x!=0 for x in w): return 'OK',t,[str(x) for x in w]
    return 'ZEROCOMP',t
if __name__=='__main__':
    res={}
    for fn in sys.argv[1:]:
        for line in open(fn):
            if line.startswith('SURV'):
                r=check(line); res.setdefault(r[0],0); res[r[0]]+=1
                if r[0]=='OK' : print(line.strip()[:200],r[1:])
    print(res)

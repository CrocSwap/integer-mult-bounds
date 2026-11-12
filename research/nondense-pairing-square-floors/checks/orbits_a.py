# Orbit code A (IDEAL implementation): W-orbits of the 8 fundamental coweights (440880 root-spanned hyperplanes), then
# Stab(omega_j)=W_J orbits of second normals by union-find over the 7 simple reflections of J; usage: orbits_a.py OUT.json.gz
# Enumerate all root-spanned hyperplanes of E8 (normals = W-orbits of fundamental coweights), save normals (x2 integer coords) + R masks
import numpy as np, itertools, sys, json, gzip
from lib import *
L=lines(e8_roots()); v=len(L)
Lm=np.array([[float(x) for x in l] for l in L])
h=F(1,2)
simple=[(h,-h,-h,-h,-h,-h,-h,h)]+[tuple(F(c) for c in r) for r in
 [(1,1,0,0,0,0,0,0),(-1,1,0,0,0,0,0,0),(0,-1,1,0,0,0,0,0),(0,0,-1,1,0,0,0,0),(0,0,0,-1,1,0,0,0),(0,0,0,0,-1,1,0,0),(0,0,0,0,0,-1,1,0)]]
import sympy
A=sympy.Matrix([[sympy.Rational(x.numerator,x.denominator) for x in r] for r in simple])
Wt=A.inv()  # columns = fundamental weights (A * w_j = e_j)
S2=[tuple(int(2*x) for x in r) for r in simple]  # 2*alpha, integer
def refl(w,a2):  # w integer = 2*vector; reflect in alpha: w - (w.alpha)*alpha*... a2=2alpha, alpha.alpha=2
    d=sum(x*y for x,y in zip(w,a2))//4   # (2w).(2a)/4 = w.a *... -> (w2.a2)/4 = w.a ; w2 = 2w
    # new w2 = w2 - 2*(w.a)/ (a.a) * 2a/... : w - (w.a) a  -> w2 - (w.a) a2
    return tuple(x-d*y for x,y in zip(w,a2))
allN=[]; typ=[]
for j in range(8):
    w=tuple(int(2*Wt[i,j]) for i in range(8))  # 2*omega_j  (check integrality)
    assert all(2*Wt[i,j]==int(2*Wt[i,j]) for i in range(8))
    seen={w}; fr=[w]
    while fr:
        nf=[]
        for u in fr:
            for a in S2:
                z=refl(u,a)
                if z not in seen: seen.add(z); nf.append(z)
        fr=nf
    # keep one of +-
    rep=[u for u in seen if tuple(-x for x in u) not in seen or u>tuple(-x for x in u)]
    print(j+1,len(seen),len(rep),file=sys.stderr)
    allN+=rep; typ+=[j]*len(rep)
N=np.array(allN,dtype=np.int64)
dots=(N@(2*Lm).T.round().astype(np.int64))  # 4 * n.l
masks=[]
for row in dots:
    m=0
    for k in np.nonzero(row)[0]: m|=1<<int(k)
    masks.append(m)
idx={}
for k,u in enumerate(allN): idx[u]=k; idx[tuple(-x for x in u)]=k
h=F(1,2)
simple=[(h,-h,-h,-h,-h,-h,-h,h)]+[tuple(F(c) for c in r) for r in
 [(1,1,0,0,0,0,0,0),(-1,1,0,0,0,0,0,0),(0,-1,1,0,0,0,0,0),(0,0,-1,1,0,0,0,0),(0,0,0,-1,1,0,0,0),(0,0,0,0,-1,1,0,0),(0,0,0,0,0,-1,1,0)]]
A=sympy.Matrix([[sympy.Rational(x.numerator,x.denominator) for x in r] for r in simple]); Wt=A.inv()
S2=[tuple(int(2*x) for x in r) for r in simple]
def refl(w,a2):
    d=sum(x*y for x,y in zip(w,a2))//4
    return tuple(x-d*y for x,y in zip(w,a2))

n=len(allN); out={}
G=[[int(dot(a,b)) for b in L] for a in L]
types=[]
for j in range(8):
    w=tuple(int(2*Wt[i,j]) for i in range(8)); i1=idx[w]
    gens=[S2[i] for i in range(8) if i!=j]
    assert all(refl(w,a)==w for a in gens)
    par=list(range(n))
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for k in range(n):
        for a in gens:
            k2=idx[refl(allN[k],a)]
            ra,rb=find(k),find(k2)
            if ra!=rb: par[ra]=rb
    orb={}
    for k in range(n): orb.setdefault(find(k),[]).append(k)
    N1=np.array(w)
    for r,mem in sorted(orb.items(),key=lambda kv:min(kv[1])):
        k=mem[0]; nonorth=int(np.dot(N1,allN[k]))!=0
        Dm=masks[i1]&masks[k]; D=[t for t in range(v) if Dm>>t&1]
        types.append(dict(j=j,k=k,orbit=len(mem),nonorth=nonorth,D=D,orth=[sum(1<<c for c,s in enumerate(D) if G[t][s]==0) for t in D]))
    print(j+1,'orbits',len(orb),file=sys.stderr,flush=True)
print('hyperplanes',n,'types',len(types),'nonorth',sum(t['nonorth'] for t in types),'orth',sum(not t['nonorth'] for t in types),
      'min|D| nonorth',min(len(t['D']) for t in types if t['nonorth']))
json.dump(types,gzip.open(sys.argv[1],'wt'))
print('PASS orbit table written')

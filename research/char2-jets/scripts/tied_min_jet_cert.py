"""Theorem T' certificate, built from the hand formula (no nullspace, no random z): cost(tied_min) >= 12 for every B.
phi(tied_min) = Fano collapse over F2 (all entries +-1 -> 1). Choose h = 1: G_k(side of M_k through point a0) = 0, other side = 1.
f_k(t) = G_k(side_k(p(t))); X(t) = (f1, f0, 0) so X.l0 = f0, X.l1 = f1, X.l2 = f0+f1 = f2;  g(s) = G_k(side carried by q(s)), Y(s) = g in one
coordinate of sigma(s).  Checks (J1) on all 72 incidences and (J2) on all 12 lines exactly over F2; then N = B o (P~ Q~^T) with
P~ = phiP + eps X, Q~ = phiQ + eps Y at a random eps in GF(2^16) (a specialisation, so rank can only drop) has rank 12 for the 217
optima, the full B and 300 random B."""
import sys, random
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from satlib import enumerate_B; from gr import mul, rank, Q as FQ
P,Q=load_cfg('tied_min.json'); v=12; R,A,free=setup(P,Q)
cls=[next(j for j in range(3) if q[j]==0) for q in Q]
a0=P[0]
def side(k,x):  # the class-k line (as a primitive vector, up to sign) through e_k and x
    i,j=[y for y in range(3) if y!=k]; q=[0,0,0]; q[i]=x[j]; q[j]=-x[i]; return q
def same(q1,q2): return all(q1[i]*q2[j]==q1[j]*q2[i] for i in range(3) for j in range(3))
G=lambda k,q: 0 if same(q, side(k,a0)) else 1
f=[[G(k,side(k,P[t])) for k in range(3)] for t in range(v)]
assert all((f[t][0]^f[t][1]^f[t][2])==0 for t in range(v)), 'sum-zero fails'
X=[[f[t][1],f[t][0],0] for t in range(v)]
g=[G(cls[s],Q[s]) for s in range(v)]
Y=[]
for s in range(v):
    y=[0,0,0]; y[next(j for j in range(3) if j!=cls[s])]=g[s]; Y.append(y)
phP=[[1 if x else 0 for x in p] for p in P]; phQ=[[1 if x else 0 for x in q] for q in Q]
d2=lambda a,b: (a[0]&b[0])^(a[1]&b[1])^(a[2]&b[2])
assert all(d2(phP[t],phQ[s])==0 for (t,s) in free), 'order-0 incidence'
assert all(d2(phP[t],phQ[t])==0 for t in range(v)), 'all harmonic'
assert all((d2(phP[t],Y[s])^d2(X[t],phQ[s]))==0 for (t,s) in free), '(J1) fails'
assert all((d2(phP[t],Y[t])^d2(X[t],phQ[t]))==1 for t in range(v)), '(J2) fails'
assert all(all(X[t][j]==0 for j in range(3) if P[t][j]==0) and all(Y[t][j]==0 for j in range(3) if Q[t][j]==0) for t in range(v))
print('(J1) on all %d incidences and (J2) on all 12 lines hold exactly over F2' % len(free))
random.seed(1); e=random.randrange(2,FQ)
Pt=[[phP[t][j]^mul(e,X[t][j]) for j in range(3)] for t in range(v)]; Qt=[[phQ[s][j]^mul(e,Y[s][j]) for j in range(3)] for s in range(v)]
dd=lambda a,b: mul(a[0],b[0])^mul(a[1],b[1])^mul(a[2],b[2])
M=[[dd(Pt[t],Qt[s]) for s in range(v)] for t in range(v)]
Bs=[]
for ent in enumerate_B(P,Q,(4,4,4)):
    B=[[int(t==s) for s in range(v)] for t in range(v)]
    for t,s in ent: B[t][s]=1
    Bs.append(B)
Bs.append(tomat((1<<len(free))-1,free,v)); Bs+=[tomat(random.getrandbits(len(free)),free,v) for _ in range(300)]
ok=sum(rank([[M[t][s] if B[t][s] else 0 for s in range(v)] for t in range(v)])==12 for B in Bs)
print('rank N = 12 for %d of %d matrices B (217 optima, full B, 300 random)' % (ok,len(Bs)))

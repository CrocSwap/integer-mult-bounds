# all-harmonic F2S configurations: q(t) = harmonic conjugate (w.r.t. the two sides through e_k) of the line e_k p(t).
# Test DEF: N1 = B o (phiP Y^T + X phiQ^T) nonsingular, on minimisers (exhaustive) and random B.
import sys, random, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit; kit.BIN=os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *; from phi import *; from gen import prim; from t12 import n1rank
def harm(p,k):
    i,j=[x for x in range(3) if x!=k]; q=[0,0,0]; q[i]=p[j]; q[j]=p[i]; return prim(q)
seed=int(sys.argv[1]); random.seed(seed); st=collections.Counter(); bad=[]
for it in range(int(sys.argv[2])):
    r=random.choice([2,3]); E=random.choice([1,2])
    pool=list({tuple(prim([1, random.choice([1,-1])*r**random.randint(0,E), random.choice([1,-1])*r**random.randint(0,E)])) for _ in range(random.randint(3,6))})
    v=random.randint(5,9); P=[];Q=[]
    for _ in range(v):
        p=list(random.choice(pool)); k=random.randrange(3); P.append(p); Q.append(harm(p,k))
    R,A,free=setup(P,Q)
    if len(free)>24: continue
    w,H=classify(P,Q); assert w==0 and len(H)==v
    pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    phi=make_phi(); Pt=[[phi(x) for x in p] for p in P]; Qt=[[phi(x) for x in q] for q in Q]
    best,ms=enum_raw(v,R,A,free,0)
    st[('cost-v',best-v)]+=1
    ok=all(n1rank(tomat(g,free,v),Pt,Qt,list(range(v)),pi,sig,trials=4)==v for c,g in ms)
    st[('DEF on minimisers',ok)]+=1
    rb=[n1rank(tomat(random.getrandbits(len(free)),free,v),Pt,Qt,list(range(v)),pi,sig,trials=4)==v for _ in range(30)]
    st[('DEF on random B',all(rb))]+=1
    if not ok or not all(rb): bad.append((P,Q))
print(seed, sorted(st.items(),key=str)); print('bad',bad[:3])

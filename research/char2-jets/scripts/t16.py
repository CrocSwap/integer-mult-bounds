import sys, itertools, collections, random
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from phi import *; from tangent import tangent_cr2; from gen import prim
def tcheck(P,Q):
    v=len(P); R,A,free=setup(P,Q)
    pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    w,H=classify(P,Q); phi=make_phi(); Pt=[[phi(x) for x in p] for p in P]; Qt=[[phi(x) for x in q] for q in Q]
    res,dim=tangent_cr2(Pt,Qt,pi,sig,free,H); return w, len(H), all(res.values())
st=collections.Counter()
P0,Q0=load_cfg('tied_min.json')
for m in range(1,13):
    for S in itertools.combinations(range(12),m):
        w,h,ok=tcheck([P0[i] for i in S],[Q0[i] for i in S]); st[('tied_min sub',ok)]+=1
print(sorted(st.items(),key=str), flush=True)
def harm(p,k):
    i,j=[x for x in range(3) if x!=k]; q=[0,0,0]; q[i]=p[j]; q[j]=p[i]; return prim(q)
random.seed(11); st=collections.Counter(); bad=[]
for it in range(1500):
    r=random.choice([2,3,5]); E=random.choice([1,2,3])
    pool=list({tuple(prim([random.choice([1,-1])*r**random.randint(0,E), random.choice([1,-1])*r**random.randint(0,E), random.choice([1,-1])*r**random.randint(0,E)])) for _ in range(random.randint(3,8))})
    v=random.randint(4,14); P=[];Q=[]
    for _ in range(v):
        p=list(random.choice(pool)); k=random.randrange(3); P.append(p); Q.append(harm(p,k))
    w,h,ok=tcheck(P,Q); st[('harmonic F2S', ok)]+=1
    if not ok: bad.append((P,Q))
print(sorted(st.items(),key=str)); print(bad[:2])

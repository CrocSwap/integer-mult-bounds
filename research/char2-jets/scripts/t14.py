# DEF on all sub-configurations of tied_min with f<=26: every minimiser (exhaustive) + 20 random B
import sys, random, collections, itertools
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit; kit.BIN=os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *; from phi import *; from t12 import n1rank
random.seed(7)
P0,Q0=load_cfg('tied_min.json'); st=collections.Counter(); bad=[]
phi=make_phi()
for m in range(2,13):
  for S in itertools.combinations(range(12),m):
    P=[P0[i] for i in S]; Q=[Q0[i] for i in S]; v=m; R,A,free=setup(P,Q)
    pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    Pt=[[phi(x) for x in p] for p in P]; Qt=[[phi(x) for x in q] for q in Q]
    if len(free)<=24:
        best,ms=enum_raw(v,R,A,free,0)
        ok=all(n1rank(tomat(g,free,v),Pt,Qt,list(range(v)),pi,sig,trials=3)==v for c,g in ms)
        st[(m,'tight' if best==v else 'slack','minimisers DEF',ok)]+=1
        if not ok: bad.append(S)
    else:
        ok=all(n1rank(tomat(random.getrandbits(len(free)),free,v),Pt,Qt,list(range(v)),pi,sig,trials=3)==v for _ in range(5))
        st[(m,'random-B DEF',ok)]+=1
        if not ok: bad.append(S)
print(sorted(st.items(),key=str)); print('bad',bad[:5])

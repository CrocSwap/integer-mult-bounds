# Theorem B2 check: on no-wild configurations, phi preserves all block incidences; diagonal is 0 exactly on harmonic lines
import sys, random, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
import kit; kit.BIN=os.environ.get('TTD_BIN') or PKG+'/c/bin'
from kit import *; from phi import *; from gen import randcfg, prim
random.seed(int(sys.argv[1])); st=collections.Counter()
def nowild_cfg(v,R):
    while True:
        P,Q=randcfg(v,R=R)
        # kill wild: give every line a zero coordinate with prob, or every point
        if random.random()<0.5:
            Q=[prim([0 if j==random.randrange(3) and False else x for j,x in enumerate(q)]) for q in Q]
        w,H=classify(P,Q)
        if w==0: return P,Q
for it in range(int(sys.argv[2])):
    v=random.randint(5,9); P,Q=nowild_cfg(v,random.choice([1,2,3]))
    w,H=classify(P,Q); R,A,free=setup(P,Q)
    phi=make_phi(); Pt=[[phi(x) for x in p] for p in P]; Qt=[[phi(x) for x in q] for q in Q]
    assert all(dot2(Pt[t],Qt[s])==0 for (t,s) in free), 'incidence broken'
    dz=[t for t in range(v) if dot2(Pt[t],Qt[t])==0]
    st[('diag0==H', dz==H)]+=1
    if len(free)<=20:
        best,ms=enum_raw(v,R,A,free,0)
        st[('cost>=v-|H|', best>=v-len(H))]+=1; st[('H', len(H)>0, 'cost-v', best-v)]+=1
print(sorted(st.items(), key=str))

import sys
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from phi import *; from tangent import tangent_cr2
for nm in sys.argv[1:]:
    P,Q=load_cfg(nm); v=len(P); R,A,free=setup(P,Q)
    pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    w,H=classify(P,Q); phi=make_phi(); Pt=[[phi(x) for x in p] for p in P]; Qt=[[phi(x) for x in q] for q in Q]
    res,dim=tangent_cr2(Pt,Qt,pi,sig,free,H)
    print(nm,'v',v,'wild',w,'|H|',len(H),'tangent dim',dim,'harmonic lines movable:',sum(res.values()),'/',len(H))

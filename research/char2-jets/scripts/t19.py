import sys, json
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from phi import *; from tangent import tangent_cr2
for i in range(3):
    P,Q=json.load(open(PKG+'/data/jf%d.json'%i)); v=len(P); R,A,free=setup(P,Q)
    pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    Pt=[[1 if x else 0 for x in p] for p in P]; Qt=[[1 if x else 0 for x in q] for q in Q]
    assert all(dot2(Pt[t],Qt[s])==0 for (t,s) in free)
    H2=[t for t in range(v) if dot2(Pt[t],Qt[t])==0]
    res,dim=tangent_cr2(Pt,Qt,pi,sig,free,H2)
    w,H=classify(P,Q)
    print('jf%d'%i,'harmonic',H,'zero diag under full collapse',H2,'movable',[t for t in H2 if res[t]],'tangent dim',dim)

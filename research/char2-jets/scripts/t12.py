# first-order char-2 deformation of the phi-realisation on harmonic lines: rank of N1_HH = B o (phiP Y'^T + X' phiQ^T) on H
import sys, random, collections
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from satlib import enumerate_B; from phi import *; from gr import rank, mul, Q as FQ
def n1rank(B,Pt,Qt,H,pi,sig,trials=3,modes=('XY',)):
    best=0
    for _ in range(trials):
        X={t:[random.randrange(1,FQ) if j in pi[t] else 0 for j in range(3)] for t in H}
        Y={t:[random.randrange(1,FQ) if j in sig[t] else 0 for j in range(3)] for t in H}
        M=[[ (dot2(Pt[t],Y[s])^dot2(X[t],Qt[s])) if B[t][s] else 0 for s in H] for t in H]
        best=max(best,rank(M))
    return best
if __name__=="__main__":
    P,Q=load_cfg('tied_min.json'); v=12; R,A,free=setup(P,Q)
    pi=[{j for j in range(3) if P[t][j]} for t in range(v)]; sig=[{j for j in range(3) if Q[t][j]} for t in range(v)]
    w,H=classify(P,Q); print('wild',w,'H',H)
    phi=make_phi(); Pt=[[phi(x) for x in p] for p in P]; Qt=[[phi(x) for x in q] for q in Q]
    c=collections.Counter()
    for ent in enumerate_B(P,Q,(4,4,4)):
        B=[[int(t==s) for s in range(v)] for t in range(v)]
        for t,s in ent: B[t][s]=1
        c[('opt',n1rank(B,Pt,Qt,H,pi,sig))]+=1
    random.seed(3)
    for _ in range(300):
        B=tomat(random.getrandbits(72),free,v); c[('rand',n1rank(B,Pt,Qt,H,pi,sig))]+=1
    c[('full',n1rank(tomat((1<<72)-1,free,v),Pt,Qt,H,pi,sig))]+=1
    print(sorted(c.items(),key=str))
    
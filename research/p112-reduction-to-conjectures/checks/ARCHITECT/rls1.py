# Check Theorem RL-s1 on witnesses: side with ONE outside direction; for every pivot pi: Delta(pi) = cost(retract_pi) - cost
# vs bound #unpaid (valid when |R_pi| <= 11). Exact.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from retract import *
def croot_prop(x):
    # return v if C'x ∝ C'c_v (x ∝ c_v), else None
    nz=[i for i in range(8) if x[i]!=0]
    for v in range(n):
        if set(nz)==supp8(v):
            r=x[nz[0]]/C[v][nz[0]]
            if all(x[i]==r*C[v][i] for i in range(8)): return v
    return None
def audit(tag,P,Q,side):
    if side=='Q': P,Q=Q,P
    X,E,X2=decomp(P); assert len(E)==1, 'need exactly one direction on this side'
    c0=cost_of(P,Q); m=len(P)
    for pi in range(m):
        if X2[0,pi]==0: continue
        h=-X[:,pi]/X2[0,pi]
        P2=rebuild(X,[Cp*h],X2); d=cost_of(P2,Q)-c0
        S=[t for t in range(n) if P[pi][t]!=0]
        V=[]
        for k in range(m):
            if k==pi or X2[0,k]==0: continue
            xk=[Fr(str(X[i,k]+X2[0,k]*h[i])) for i in range(8)]
            v=croot_prop(xk)
            if v is not None and v in S and P[k][v]==0: V.append((k,v))
        unpaid=[v for k,v in V if Q[pi][v]==0]
        ok = (d<=len(unpaid)) if len(S)<=11 else None
        print(f'{tag} side {side} pivot {pi}: |R_pi|={len(S)} swaps={V} unpaid={unpaid} Delta={d} bound_holds={ok}',flush=True)
if __name__=='__main__':
    src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../TWINSWAP/witness16.py')).read()
    src=src.replace("    P,Q=build(Xh,Yh,E,F)\n","    P,Q=build(Xh,Yh,E,F); STASH.append((mode,P,Q))\n")
    STASH=[]; here=os.getcwd(); os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'../TWINSWAP'))
    g={'STASH':STASH,'__name__':'w16'}; exec(src,g)
    for mode,P,Q in STASH:
        for side in 'PQ': audit('w16-'+mode,P,Q,side)
    import json
    d=json.load(open('decoder.json')); P=[[Fr(x) for x in p] for p in d['P']]; Q=[[Fr(x) for x in q] for q in d['Q']]
    audit('MS3a(2,1)',P,Q,'Q')

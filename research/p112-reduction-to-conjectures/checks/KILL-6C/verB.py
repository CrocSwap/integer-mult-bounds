# Impl B (independent of cert.py / scipy): exact Fraction check of each Farkas certificate, plus the closed-form symmetric bound.
# Claim checked: for every nonempty M subset [p]: sum_{K sup M} y_K + sum_{j in M} z_j >= 1, all y,z >= 0, |K| <= 3,
#   and  sum_K y_K*Nk(|K|) + sum_j z_j*gw(w_j) < NL.  (Nk: G2 = max E8 lines in a k-dim subspace, k<=3; gw: exact max lines in a w-flat.)
import json, sys
from fractions import Fraction as F
from itertools import combinations
Nk={1:1,2:3,3:6}; gw={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
C=json.load(open(sys.argv[1] if len(sys.argv)>1 else 'certs.json'))
allok=True
for name,c in C.items():
    ws=c['ws']; p=len(ws); NL=c['NL']
    y={}
    for K,v in c['K']:
        S=frozenset(j for j in range(p) if (K>>j)&1); assert 1<=len(S)<=3; y[S]=y.get(S,0)+F(v)
    z=[F(v) for v in c['z']]
    assert all(v>=0 for v in y.values()) and all(v>=0 for v in z)
    rhs=sum(v*Nk[len(S)] for S,v in y.items())+sum(z[j]*gw[ws[j]] for j in range(p))
    # coverage: only subsets M with |M|<=3 can be inside a K; larger M rely on z alone -> check min over all M by enumeration
    worst=None
    for m in range(1,p+1):
        for M in combinations(range(p),m):
            Ms=frozenset(M)
            cov=sum(z[j] for j in M)+sum(v for S,v in y.items() if Ms<=S)
            if worst is None or cov<worst: worst=cov
    ok = worst>=1 and rhs<NL
    allok&=ok
    print('%-12s p=%2d NL=%d min-cover=%s bound=%.4f <NL? %s  %s'%(name,p,NL,worst if worst<2 else '>=2',float(rhs),rhs<NL,'OK' if ok else 'FAIL'))
# closed form (Triple Count): sum_t |M_t| >= (2(p-2)NL - 2p(p-1))/(p-3) using only a<=..., a+b<=NL and N3=6
def B(p,NL): return F(2*(p-2)*NL-2*p*(p-1),p-3)
for name,c in C.items():
    s=sum(gw[w] for w in c['ws']); b=B(len(c['ws']),c['NL'])
    print('TC %-12s sum g=%d  TCbound=%.3f  %s'%(name,s,float(b),'KILL' if s<b else '-'))
print('ALL CERTS OK' if allok else 'SOME FAIL')

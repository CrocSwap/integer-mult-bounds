"""sigma(d) = max |P cap U| over d-dim subspaces U of F2^9 (exact: via codim enumeration of functionals)."""
from ncore import *
import pickle
F=pickle.load(open('ztight_F.pkl','rb'))
ms=[min(bin(k).count('1') for k in F[t]) for t in range(n)]
print('sum_t min|K_t| =',sum(ms),' histogram',{s:ms.count(s) for s in set(ms)})
hint=np.array([int(sum(int(H[t,i])<<i for i in range(9))) for t in range(n)])
par=np.array([[bin(a&b).count('1')&1 for b in range(512)] for a in range(512)],np.uint8)
# U of codim c = common kernel of c independent functionals; max |P cap U| by greedy exhaustive over functional subspaces
# codim 1,2 exhaustive; deeper: exhaustive over subspaces via spans of labels (U = span of a subset): use best-first
inP=lambda f: par[f][hint]==0
best={9:104}
b1=max(int(inP(f).sum()) for f in range(1,512)); best[8]=b1
b2=0
for f in range(1,512):
    a=inP(f)
    for g in range(f+1,512):
        if g==f or (f^g)==0: continue
        b2=max(b2,int((a&inP(g)).sum()))
best[7]=b2
print('sigma(9,8,7)=',best[9],best[8],best[7])

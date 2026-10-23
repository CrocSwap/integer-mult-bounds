# E8 lines (120, in the fixed order used by every card of this series), Gram matrix, orthogonality sets, frames (8 pairwise orthogonal lines), tetrads w.r.t. a frame.
# (Same order as BSTAR/blib.py of the working cards: the CNF regeneration in verify.sh is byte-identical only for this order.)
import itertools
from fractions import Fraction as F
def e8_roots():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for si in(1,-1):
            for sj in(1,-1):
                r=[F(0)]*8; r[i]=F(si); r[j]=F(sj); R.append(tuple(r))
    for s in itertools.product((1,-1),repeat=8):
        if s.count(-1)%2==0: R.append(tuple(F(x,2) for x in s))
    return R
def lines(R):
    seen=set();L=[]
    for r in R:
        n=tuple(-x for x in r)
        if n in seen: continue
        seen.add(r); L.append(r)
    return L
E=lines(e8_roots()); N=len(E)
assert N==120
dot=lambda x,y: sum(a*b for a,b in zip(x,y))
G=[[dot(E[i],E[j]) for j in range(N)] for i in range(N)]
O=[frozenset(s for s in range(N) if G[u][s]==0) for u in range(N)]
UNITS={'E8':frozenset(range(N))}
def frames(S=None):
    S=sorted(S if S is not None else range(N)); out=[]
    def rec(cur,cand):
        if len(cur)==8: out.append(tuple(cur)); return
        for i,c in enumerate(cand):
            if cur and c<cur[-1]: continue
            rec(cur+[c],[d for d in cand[i+1:] if G[c][d]==0])
    rec([],S); return out
def tetrads(Fr):
    T={}
    for u in range(N):
        if u in Fr: continue
        k=frozenset(f for f in Fr if G[u][f]!=0); T.setdefault(k,[]).append(u)
    return T

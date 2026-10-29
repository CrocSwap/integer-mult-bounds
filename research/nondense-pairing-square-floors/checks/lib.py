# Shared exact helpers: E8 root lines (Fractions), F2 rank, deterministic non-orthogonal clique search.
import itertools
from fractions import Fraction as F
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def e8_roots():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for si in (1,-1):
            for sj in (1,-1):
                r=[F(0)]*8; r[i]=F(si); r[j]=F(sj); R.append(tuple(r))
    for s in itertools.product((1,-1),repeat=8):
        if s.count(-1)%2==0: R.append(tuple(F(x,2) for x in s))
    return R
def lines(R):
    seen=set(); L=[]
    for r in R:
        if tuple(-x for x in r) in seen: continue
        seen.add(r); L.append(r)
    return L
def rank2(rows):
    piv={}; r=0
    for x in rows:
        while x:
            h=x.bit_length()-1
            if h in piv: x^=piv[h]
            else: piv[h]=x; r+=1; break
    return r
def dense_rank(G,D):
    return rank2([sum(1<<k for k,s in enumerate(D) if G[t][s]%2==0) for t in D])
def nonorth_clique(G,D,r):
    """deterministic backtracking: r pairwise non-orthogonal lines of D, or None"""
    D=list(D)
    def rec(cur,cand):
        if len(cur)==r: return cur
        if len(cur)+len(cand)<r: return None
        for i,c in enumerate(cand):
            out=rec(cur+[c],[d for d in cand[i+1:] if G[c][d]!=0])
            if out: return out
        return None
    return rec([],D)

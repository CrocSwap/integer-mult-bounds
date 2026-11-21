# Span-cached F2 ranks of Q[A,B]: depends only on row spaces R_A = span Q[A,:], R_B. Exact.
import numpy as np
def rref(vs):
    basis=[]
    for v in vs:
        for x in basis:
            if v^x<v: v^=x
        if v:
            lead=v.bit_length()-1
            basis=[x^v if (x>>lead)&1 else x for x in basis]
            basis.append(v); basis.sort(reverse=True)
    return tuple(basis)
def rank_ints(rows):
    b=[]
    for v in rows:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
class Labels:
    def __init__(self,Q):
        Q=np.array(Q,dtype=np.uint8); self.n=len(Q)
        self.row=[sum(int(Q[i,j])<<j for j in range(self.n)) for i in range(self.n)]
        self.h=len(rref(self.row)); self.cache={}; self.rep={}
    def span(self,idx):
        s=rref([self.row[i] for i in idx]); m=sum(1<<i for i in idx)
        self.rep.setdefault(s,m); return s
    def pair_rank(self,SA,SB):
        key=(SA,SB)
        if key not in self.cache:
            bm=self.rep[SB]; self.cache[key]=rank_ints([r&bm for r in SA])
        return self.cache[key]

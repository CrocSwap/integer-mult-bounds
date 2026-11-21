# NETATTR common (own code). Labels = odd vectors of F2^h as ints. Exact integer/rational only.
import itertools
def dot(x,y): return bin(x&y).count('1')&1
def span(g):
    s={0}
    for v in g: s|={x^v for x in s}
    return frozenset(s)
def dimof(S): return len(S).bit_length()-1
def rk2(vecs):
    basis=[]
    for x in vecs:
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
def perp(S,h): return frozenset(x for x in range(1<<h) if all(dot(x,y)==0 for y in S))
def price(Dl,Sl):
    # rank_F2 of Q[D,S] = rank of pairing span(D) x span(S)
    rows=[sum(dot(t,p)<<j for j,p in enumerate(Sl)) for t in Dl]
    return rk2(rows)
def subspaces(h):
    seen=set(); out=[]
    def rec(basis,S):
        if S in seen: return
        seen.add(S); out.append(S)
        for v in range(1,1<<h):
            if v not in S: rec(basis+[v],span(list(S)+[v]))
    rec([],frozenset({0}))
    return out

"""ORBITLP geo.py (own code): P104 labels, Q, frames, Aut (verified), orbits."""
import numpy as np, itertools, functools
D56='<research-tree>/cards/WILD/LUNCH/exchange/d56dir/mod4/'
LAB=[int(x) for x in open(D56+'labels.txt').read().split()]
n=len(LAB); assert n==104
dot=lambda a,b: bin(a&b).count('1')&1
Q=np.array([[dot(a,b) for b in LAB] for a in LAB],dtype=np.int64)
assert all(Q[i,i]==1 for i in range(n))
@functools.lru_cache(None)
def frames():
    # all 8-cliques of the odd graph (pairwise odd)
    adj=[set(j for j in range(n) if j!=i and Q[i,j]) for i in range(n)]
    out=[]
    def ext(cl,cand):
        if len(cl)==8: out.append(tuple(cl)); return
        for v in sorted(cand):
            if v>cl[-1]: ext(cl+[v],cand&adj[v])
    for i in range(n): ext([i],adj[i])
    return out
@functools.lru_cache(None)
def aut():
    raw=np.fromfile(D56+'b/aut.bin',dtype=np.uint8).reshape(-1,104)
    for p in raw:
        assert sorted(p)==list(range(n))
        assert (Q[np.ix_(p,p)]==Q).all()
    return raw
if __name__=='__main__':
    F=frames(); A=aut()
    print('frames',len(F),'aut',len(A))
    fs=set(F); 
    for p in A:
        for f in F: assert tuple(sorted(p[list(f)])) in fs
    # orbits
    seen=set(); po=[]
    for i in range(n):
        if i in seen: continue
        o=set(int(p[i]) for p in A); seen|=o; po.append(sorted(o))
    print('port orbits',[len(o) for o in po])
    seen=set(); fo=[]
    for f in F:
        if f in seen: continue
        o=set(tuple(sorted(p[list(f)])) for p in A); seen|=o; fo.append(len(o))
    print('frame orbits',fo)
    print('odd pairs offdiag', (Q.sum()-n)//2, 'deg', set(Q.sum(1)-1))
    print('rank_Q Q', np.linalg.matrix_rank(Q.astype(float)))

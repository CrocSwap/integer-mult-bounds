# G(w,u) = max over label w-flats F (P112 or E8 lines) and real u-dim V of #{t in F : c_t in V}.  Exact.
import json, itertools, numpy as np, sys
from collections import Counter
D=json.load(open('data.json'))
unit=sys.argv[1] if len(sys.argv)>1 else 'P112'
FC=[list(map(int,r)) for r in D['FC']]; LAB=list(D['LAB'])
if unit=='E8':
    for i in range(8):
        e=[0]*8; e[i]=2; FC.append(e); LAB.append(D['Z'][i])
v=len(FC); X=np.array(FC,float)
par=lambda x: bin(x).count('1')&1
mask={z:sum(1<<t for t in range(v) if not par(z&LAB[t])) for z in range(1,512)}
pc=lambda m: bin(m).count('1')
def lines(m): return [t for t in range(v) if m>>t&1]
def rk(ts): return 0 if not ts else int(np.linalg.matrix_rank(X[ts]))
def flats_of(ts):
    # all matroid flats of vectors X[ts], by rank; return dict rank->max size
    best={}
    ts=list(ts); n=len(ts)
    # closure-based BFS on flats
    def closure(S):
        if not S: return frozenset()
        B=X[list(S)]; r=np.linalg.matrix_rank(B)
        return frozenset(t for t in ts if np.linalg.matrix_rank(np.vstack([B,X[t]]))==r)
    level={frozenset()}; r=0
    while level and r<8:
        nxt=set()
        for Fl in level:
            for t in ts:
                if t in Fl: continue
                nxt.add(closure(Fl|{t}))
        r+=1
        if nxt: best[r]=max(len(f) for f in nxt)
        level=nxt
        if r>=7 or len(level)>200000: break
    return best
w=int(sys.argv[2])
cod=9-w
# enumerate label subspaces of dim w (as intersections of cod hyperplanes), dedupe line sets, keep maximal
sets=set()
if cod==2:
    for a in range(1,512):
        for b in range(a+1,512):
            m=mask[a]&mask[b]
            if pc(m)>=13: sets.add(m)
elif cod==3:
    for a in range(1,512):
        for b in range(a+1,512):
            mab=mask[a]&mask[b]
            if pc(mab)<9: continue
            for c in range(b+1,512):
                if c==a^b: continue
                m=mab&mask[c]
                if pc(m)>=9: sets.add(m)
# orbit reduce by sizes+invariant: just dedupe by (size, sorted rank profile) cheaply -> compute on all but cache by invariant
print(unit,'w',w,'candidate line sets',len(sets),Counter(pc(m) for m in sets).most_common(8),flush=True)
G={}
inv_cache={}
for m in sorted(sets,key=pc,reverse=True):
    ts=lines(m)
    # invariant: gram multiset of c-vectors (orbit invariant under W)
    Gm=X[ts]@X[ts].T
    key=(len(ts),tuple(sorted(Counter(np.abs(Gm).ravel().astype(int)).items())),tuple(sorted(np.abs(Gm).sum(1).astype(int))))
    if key in inv_cache: continue
    b=flats_of(ts); inv_cache[key]=b
    for r,s in b.items(): G[r]=max(G.get(r,0),s)
    print(len(ts),'rank',rk(ts),b,flush=True)
print('G(w=%d,u)='%w,G)

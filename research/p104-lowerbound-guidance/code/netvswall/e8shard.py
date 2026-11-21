# own reimplementation: E8 decoder rows on P104 (labels in F2^9) and restriction to shards P' (subsets of the 104 ports).
import json, numpy as np, itertools, random, sys
from fractions import Fraction as Fr
WD='<research-tree>/cards/WILD/'
G104=np.load(WD+'REBASET1/G104.npy').astype(int); Q104=json.load(open(WD+'REBASET1/lines104.json'))
dot=lambda a,b: bin(a&b).count('1')&1
ev,V=np.linalg.eigh(G104.astype(float)); R=V[:,ev>13]*np.sqrt(26.0)
key=lambda v: tuple(np.round(v*1e6).astype(np.int64))
seen={}
for v in R: seen[key(v)]=v; seen[key(-v)]=-v
fr=list(seen.values())
while fr:
    new=[]; allr=list(seen.values())
    for a in fr:
        for b in allr:
            w=b-(a@b)*a; k=key(w)
            if k not in seen: seen[k]=w; new.append(w)
    fr=new
assert len(seen)==240
lines=[R[i] for i in range(104)]
for v in seen.values():
    if not any(abs(abs(v@u)-2)<1e-6 for u in lines): lines.append(v)
L=np.array(lines); G=np.rint(L@L.T).astype(int)
U=list(Q104)
for l in range(104,120):
    sols=[u for u in range(512) if all(dot(u,Q104[t])==(G[l,t]+1)%2 for t in range(104))]
    assert len(sols)==1; U.append(sols[0])
idx={U[i]:i for i in range(120)}
n=104
Q=[[dot(U[t],U[s]) for s in range(n)] for t in range(n)]
pairs=[(137,127),(25,162),(7,104),(448,42),(67,97),(491,76),(52,266),(82,289)]
rows=[]
for (zp,z) in pairs:
    d,dp=idx[z],idx[zp]; c=int(G[d,dp])
    w=[Fr(int(G[p,d])) for p in range(n)]; u=[Fr(int(G[s,dp]),2*c) for s in range(n)]
    rows.append((w,u))
for t in range(n):
    for s in range(n):
        if Q[t][s]: assert sum(w[t]*u[s] for w,u in rows)==(1 if t==s else 0)
print('E8 decoder verified',flush=True)
def rk2(vecs):
    basis=[]
    for x in vecs:
        for b in basis: x=min(x,x^b)
        if x: basis.append(x)
    return len(basis)
def prices(Pset):
    out=[]
    for w,u in rows:
        D=[t for t in Pset if w[t]!=0]; S=[s for s in Pset if u[s]!=0]
        if not D or not S: continue
        out.append(rk2([sum(Q[t][s]<<j for j,s in enumerate(S)) for t in D]))
    return out
def dimspan(Pset): return rk2([U[t] for t in Pset])
def gain(Pset): return len(Pset)-sum(prices(Pset))
if __name__=='__main__':
    full=list(range(n)); print('full gain',gain(full),prices(full),dimspan(full))
    random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 0)
    # greedy deletion hill climb with random tie-break
    cur=full[:]
    best=(gain(cur),len(cur),dimspan(cur))
    while True:
        cands=[]
        for t in cur:
            nxt=[x for x in cur if x!=t]; cands.append((gain(nxt),t))
        g0=gain(cur); m=max(c[0] for c in cands)
        if m<g0 and len(cur)<60: break
        t=random.choice([c[1] for c in cands if c[0]==m]); cur=[x for x in cur if x!=t]
        if gain(cur)>0 and len(cur)<=40: pass
        if len(cur)<=1: break
    print('end',len(cur),gain(cur),prices(cur),dimspan(cur))

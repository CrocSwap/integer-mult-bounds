# G(w,u): max #lines of a label w-flat lying in a real u-dim subspace. Orbit-reduced, vectorised closures.
import json, numpy as np, sys, time
from collections import Counter
D=json.load(open('data.json'))
FC=[list(map(int,r)) for r in D['FC']]; LAB=list(D['LAB']); v=len(FC); X=np.array(FC,float)
gens=[list(map(int,l.split())) for l in open('gens.txt')]
par=lambda x: bin(x).count('1')&1
mask={z:sum(1<<t for t in range(v) if not par(z&LAB[t])) for z in range(1,512)}
pc=lambda m: bin(m).count('1')
def img(g,T):
    out=0; y=T
    while y:
        t=(y&-y).bit_length()-1; y&=y-1; out|=1<<g[t]
    return out
def orbit_reps(sets):
    seen=set(); reps=[]
    for T in sorted(sets,key=pc,reverse=True):
        if T in seen: continue
        orb={T}; st=[T]
        while st:
            x=st.pop()
            for g in gens:
                y=img(g,x)
                if y not in orb: orb.add(y); st.append(y)
        seen|=orb; reps.append((T,len(orb)))
    return reps
def profile(m):
    ts=[t for t in range(v) if m>>t&1]; Y=X[ts]; n=len(ts)
    def clo(idx):
        B=Y[idx]; U,s,Vt=np.linalg.svd(B); r=int((s>1e-9).sum()); Q=Vt[:r].T
        res=Y-(Y@Q)@Q.T
        return frozenset(np.nonzero((res*res).sum(1)<1e-9)[0].tolist()), r
    best={}; level={frozenset():[]}
    for r in range(1,8):
        nxt={}
        for Fl,B in level.items():
            for t in range(n):
                if t in Fl: continue
                c,_=clo(B+[t])
                if c not in nxt: nxt[c]=B+[t]
        if not nxt: break
        best[r]=max(len(c) for c in nxt); level=nxt
    return best, int(np.linalg.matrix_rank(Y))
w=int(sys.argv[1]); minsz=int(sys.argv[2])
sets=set()
if w==7:
    for a in range(1,512):
        for b in range(a+1,512):
            m=mask[a]&mask[b]
            if pc(m)>=minsz: sets.add(m)
else:
    for a in range(1,512):
        for b in range(a+1,512):
            mab=mask[a]&mask[b]
            if pc(mab)<minsz: continue
            for c in range(b+1,512):
                if c==a^b: continue
                m=mab&mask[c]
                if pc(m)>=minsz: sets.add(m)
reps=orbit_reps(sets)
print('w',w,'sets',len(sets),'orbits',len(reps),flush=True)
G={}
for T,n in reps:
    t0=time.time(); b,rr=profile(T)
    for r,s in b.items(): G[r]=max(G.get(r,0),s)
    print('size',pc(T),'orbit',n,'realrank',rr,b,round(time.time()-t0,1),'s',flush=True)
print('G(w=%d, u)='%w,G,flush=True)

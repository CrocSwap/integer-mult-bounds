"""PUNCT5: Theorem-45 template at p = P (default 46), case d_0 = 3 (all Q-roots d = 3).
Anchors = all d>=3 kernels A of root 0 with |A| <= P, mod Stab(0). For each anchor, options = (side, level, minimal extra set E ⊆ lines∖A,
|E| <= P-|A|): roots != 0 at level 2 (live co-flat labels in a coset of a 6-dim subspace) and level 3 (5-dim); D7 flats level 2.
Objective: max sum over hosted sides of (level-1) [bracket minus root 0's 2]. Exact: MILP for a candidate + exact brute-force check."""
import numpy as np, pickle, itertools, sys, time
sys.path.insert(0,'/Users/mason/repo_clones/intmult-work/cards/PUNCT4')
import os; os.chdir('/Users/mason/repo_clones/intmult-work/cards/PUNCT4')
from p4lib import *
from kernels import kernels
P=int(sys.argv[1]) if len(sys.argv)>1 else 46
labs=np.array(lab,dtype=np.int64)
def subspaces(k,n=8):
    for piv in itertools.combinations(range(n),k):
        free=[(i,j) for i in range(k) for j in range(piv[i]+1,n) if j not in piv]
        for bits in range(1<<len(free)):
            rows=[1<<piv[i] for i in range(k)]
            for b,(i,j) in enumerate(free):
                if bits>>b&1: rows[i]|=1<<j
            yield rows
def cosets(k):
    R=[]
    for rows in subspaces(k):
        Wv=np.zeros(1,dtype=np.int64)
        for r in rows: Wv=np.concatenate([Wv,Wv^r])
        reps=(labs[:,None]^Wv[None,:]).min(axis=1)
        u=np.unique(reps); R.append(np.searchsorted(u,reps).astype(np.int8))
    return np.array(R)
t0=time.time()
R6=cosets(6); R5=cosets(5); print('subspaces',len(R6),len(R5),round(time.time()-t0),flush=True)
D=pickle.load(open('kernels.pkl','rb')); PER=D['PER']
best,ks=kernels(0,3,slack=P-37)
ks=[k for k in ks if len(k)<=P]
stab=[PER[a] for a in range(120) if G[0,a]==0]
rem=set(ks); reps=[]
while rem:
    k=rem.pop(); orb={k}; fr=[k]
    while fr:
        nf=[]
        for x in fr:
            for P_ in stab:
                y=frozenset(P_[t] for t in x)
                if y not in orb: orb.add(y); nf.append(y)
        fr=nf
    rem-=orb; reps.append(k)
print('d3 kernels <=',P,':',len(ks),'classes',len(reps),sorted(len(r) for r in reps),flush=True)
sides=pickle.load(open('sides.pkl','rb'))
SIDES=[('E7',a,(G[a]!=0)) for a in range(1,120)]+[('D7',i,~m) for i,(nm,m) in enumerate(sides) if nm=='D7']
def minimal(ex):
    ex=sorted(set(ex),key=len); mins=[]
    for e in ex:
        if not any(m<=e for m in mins): mins.append(e)
    return mins
def opts_for(A,b):
    Am=np.zeros(120,bool); Am[list(A)]=True; opts=[]
    for si,(nm,key,C) in enumerate(SIDES):
        CA=np.flatnonzero(C&~Am)
        for lev,R,nc in ((2,R6,4),(3,R5,8)):
            if lev==3 and nm!='E7': continue
            need=len(CA)-b
            if need<=0: opts.append((si,lev,frozenset())); continue
            sub=R[:,CA]; ex=[]
            for c in range(nc):
                hit=(sub==c); ok=np.flatnonzero(hit.sum(axis=1)>=need)
                for w in ok: ex.append(frozenset(CA[~hit[w]].tolist()))
            opts+=[(si,lev,e) for e in minimal(ex)]
    return opts
def exact_max(opts,b):
    """exact: max sum_{sides}(lev-1), one option per side, union of extras <= b. DFS over sides with pruning."""
    sids=sorted(set(o[0] for o in opts)); by={s:[(l,e) for si,l,e in opts if si==s] for s in sids}
    ub={s:max(l for l,_ in by[s])-1 for s in sids}
    best=[0,None]
    def dfs(i,used,val,chosen):
        if val>best[0]: best[0]=val; best[1]=list(chosen)
        if i==len(sids): return
        if val+sum(ub[s] for s in sids[i:])<=best[0]: return
        s=sids[i]
        for l,e in sorted(by[s],key=lambda x:-x[0]):
            u=used|e
            if len(u)<=b: chosen.append((SIDES[s][:2],l)); dfs(i+1,u,val+l-1,chosen); chosen.pop()
        dfs(i+1,used,val,chosen)
    dfs(0,frozenset(),0,[])
    return best
out=[]
for ai,A in enumerate(sorted(reps,key=len)):
    b=P-len(A); opts=opts_for(A,b)
    t1=time.time(); bv,arg=exact_max(opts,b)
    print('anchor',ai,'|A|',len(A),'budget',b,'#opts',len(opts),'EXACT max other-bracket',bv,'(allowed 6)','OK' if bv<=6 else 'FAIL',arg,round(time.time()-t1,1),flush=True)
    out.append((sorted(A),b,bv,arg))
pickle.dump(out,open(f'/Users/mason/repo_clones/intmult-work/cards/PUNCT5/anch{P}_out.pkl','wb'))

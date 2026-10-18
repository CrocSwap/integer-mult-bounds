# exact relaxation lower bound for square decoders of a B-form realisation phat(u)=(D1 r_u, c_u) etc.
# candidates: all 1-dim deficiency spaces, pairwise intersections, and a generic member of each multi-dim space (duality-free).
import sys,pickle,itertools,random
from a2lib import *
import os
NDIM=int(os.environ.get('NDIM','9')); NT=int(os.environ.get('NT','9'))
def run(Zc,Zb,c,b,out,thresh=65,verbose=True,PH=None):
    ph=[list(map(Fr,L[u]))+[Fr(c[u])] for u in range(v)]; qh=[list(map(Fr,L[u]))+[Fr(b[u])] for u in range(v)]
    if PH: ph=[list(map(Fr,x)) for x in PH[0]]; qh=[list(map(Fr,x)) for x in PH[1]]
    def norm(x):
        i=next(k for k in range(NDIM) if x[k]!=0); return tuple(a/x[i] for a in x)
    def cands(side):
        sp=[(x[1] if side==0 else x[2]) for x in out.values()]; sp=[s for s in sp if s]
        one=set(); free=[]
        for s in sp:
            if len(s)==1: one.add(norm(s[0]))
            else: free.append(tuple(sum(random.randint(1,97)*vv[k] for vv in s) for k in range(NDIM)))
        # pairwise intersections of multi-dim spaces with everything
        for s1,s2 in itertools.combinations([s for s in sp if len(s)>1],2):
            ns=nullspace([*[ [a for a in w] for w in nullspace(s1,NDIM)], *nullspace(s2,NDIM)],NDIM)
            if len(ns)==1: one.add(norm(ns[0]))
        return [list(x) for x in one],[list(x) for x in free]
    random.seed(1)
    d1,dfree=cands(0); e1,efree=cands(1)
    def supp(vecs,x): return [u for u in range(v) if sum(a*b for a,b in zip(vecs[u],x))!=0]
    full=list(range(v))
    R=[supp(ph,d) for d in d1+dfree]; A=[supp(qh,e) for e in e1+efree]
    nd,ne=len(d1),len(e1)
    f=[[blk(Brows,R[i],A[j]) for j in range(len(A))] for i in range(len(R))]
    fr=[blk(Brows,R[i],full) for i in range(len(R))]; fc=[blk(Brows,full,A[j]) for j in range(len(A))]
    dot=lambda x,y: sum(a*b for a,b in zip(x,y))
    Pm=[[dot(e1[j],d1[i]) if (i<nd and j<ne) else None for j in range(len(A))] for i in range(len(R))]
    if os.environ.get('ROBUST'):
        # value-robust: a dot product x.x' + d9 e9 with both 9th coords and x-parts nonzero may vanish for special c,beta -> unconstrained
        nv=0
        for i in range(nd):
            for j in range(ne):
                d,e=d1[i],e1[j]
                if d[8]!=0 and e[8]!=0 and any(d[k]!=0 for k in range(8)) and any(e[k]!=0 for k in range(8)) and sum(d[k]*e[k] for k in range(8))!=0:
                    Pm[i][j]=None; nv+=1
        print('robust: variable pairs',nv,flush=True)
    vec_r=d1+dfree; vec_c=e1+efree
    LB=min(min(map(min,f)),min(fr),min(fc))
    if verbose: print('cands row',nd,'+',len(dfree),'col',ne,'+',len(efree),'min pair',LB,'row-only',sorted(fr)[:6],'col-only',sorted(fc)[:6],flush=True)
    best=[thresh]; found=[]
    def ok_pair(i,j,ui,uj):
        if i is not None and j is not None and Pm[i][j] is not None and Pm[i][j]==0: return False
        if i is not None and any(Pm[i][jj] not in (None,) and Pm[i][jj]!=0 for jj in uj): return False
        if j is not None and any(Pm[ii][j] not in (None,) and Pm[ii][j]!=0 for ii in ui): return False
        return True
    minrow=[min([fr[i]]+f[i]) for i in range(len(R))]; mincol=[min([fc[j]]+[f[i][j] for i in range(len(R))]) for j in range(len(A))]
    def rem(k,ui,uj):
        pool=sorted([minrow[i] for i in range(len(R)) if i not in ui]+[mincol[j] for j in range(len(A)) if j not in uj]+[9]*NT)
        return sum(pool[:NT-k])
    def dfs(k,cost,ui,uj,last):
        if cost+rem(k,ui,uj)>=best[0]: return
        if k==NT: best[0]=cost; found.append(cost); print('decoder',cost,last,flush=True); return
        opts=[]
        for i in [None]+[i for i in range(len(R)) if i not in ui]:
            for j in [None]+[j for j in range(len(A)) if j not in uj]:
                if not ok_pair(i,j,ui,uj): continue
                cst=9 if i is None and j is None else (fc[j] if i is None else (fr[i] if j is None else f[i][j]))
                key=(cst,-1 if i is None else i,-1 if j is None else j)
                if key<last: continue
                opts.append((key,i,j))
        opts.sort()
        for key,i,j in opts:
            ni=ui+([i] if i is not None else []); nj=uj+([j] if j is not None else [])
            if i is not None and not indr(tuple(sorted(ni))): continue
            if j is not None and not indc(tuple(sorted(nj))): continue
            dfs(k+1,cost+key[0],ni,nj,key)
    from functools import lru_cache
    @lru_cache(maxsize=None)
    def indr(t): return rank([vec_r[x] for x in t],NDIM)==len(t)
    @lru_cache(maxsize=None)
    def indc(t): return rank([vec_c[x] for x in t],NDIM)==len(t)
    dfs(0,0,[],[],(-1,-1,-1))
    return best[0] if found else None
if __name__=='__main__':
    T=pickle.load(open(sys.argv[1],'rb')); Zc,Zb,c,b,out=T[:5]
    r=run(Zc,Zb,c,b,out,int(sys.argv[2]) if len(sys.argv)>2 else 65,PH=T[5:7] if len(T)>5 else None)
    print(sys.argv[1],'relaxation min below threshold:',r)

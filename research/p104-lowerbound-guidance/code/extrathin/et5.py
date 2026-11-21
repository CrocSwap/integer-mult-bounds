# EXTRATHIN et5: general e=1 CLASS pattern LP.  Rank-3 K_hh = U W^T: stage s has point p_s (ker U_s) and line L (row space of W_s).
# Stages grouped by LINE CLASS (m classes, g stages each); inc[i][j]=1 iff points of class i lie on line L_j (j != i; never j = i).
# rank G_{s,T} = 2 unless all of T lies in ONE class j with inc[class(s)][j] = 1  (then 1).   [P: dim U_s(sum Pi_t)]
# Rows: count, MAINS>=2k, DEEP>=2k (each stage has an own-class partner => rank 2), SET-RC2_l for all compositions |T|<=X, leaf, F.
import os, sys, itertools
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from math import comb
from scipy.optimize import linprog
s=.99; pw=lambda x: x**s
def run(m,g,inc,X,e=1,maxit=300):
    k=m*g
    comps=[c for c in itertools.product(range(g+1),repeat=m) if 1<=sum(c)<=X]
    rows=[]
    for i in range(m):
        for c in comps:
            if c[i]>g-1: continue
            nz=[j for j in range(m) if c[j]>0]
            rk=1 if (len(nz)==1 and nz[0]!=i and inc[i][nz[0]]) else 2
            for l in range(2,k+1): rows.append((l,i,c,rk))
    rhs=np.r_[2*k,2*k,[rk*g*np.prod([comb(g-(1 if j==i else 0),c[j]) for j in range(m)]) for (l,i,c,rk) in rows]]
    masks=[a for a in itertools.product(range(g+1),repeat=m) if sum(a)>0]
    cache={}
    def pr(p,a):
        key=(p,a)
        if key in cache: return cache[key]
        D=sum(a); L=sum(p); out=np.zeros(len(rows)+2)
        if L==1: out[0]=1; out[1]=1 if D>=2 else 0
        for q,(l,i,c,rk) in enumerate(rows):
            if p[i]==0: continue
            av=1
            for j in range(m): av*=comb(g-p[j],c[j])
            if D>=l:
                if L<l: out[2+q]=p[i]*av
            else:
                av2=1
                for j in range(m): av2*=comb(g-a[j],c[j])
                out[2+q]=p[i]*(av-av2)
        cache[key]=out; return out
    def trow(a,P): return sum(pr(p,a) for p in P)
    def val(a,P): return pw(8*sum(a)+1)-sum(pw(8*sum(p)) for p in P)
    unit=lambda j: tuple(1 if t==j else 0 for t in range(m))
    def singles(a): return tuple(sorted([unit(j) for j in range(m) for _ in range(a[j])]))
    cols=list(dict.fromkeys([(a,singles(a)) for a in masks]+[(a,(a,)) for a in masks if sum(a)>1]))
    for it in range(maxit):
        A=np.array([trow(a,P) for a,P in cols]).T; cost=-np.array([val(a,P)-1 for a,P in cols])
        D1=np.array([1 if sum(a)==1 else 0 for a,P in cols])
        Aub=np.vstack([-A,-np.ones((1,len(cols))),-(k-D1)[None,:]]); bub=np.r_[-rhs,-(2*k-1),-k*(2*k-2-e)]
        r=linprog(cost,A_ub=Aub,b_ub=bub,method='highs')
        y=-r.ineqlin.marginals; lam=y[len(rhs)]; mu=y[len(rhs)+1]; yr=y[:len(rhs)]
        new=[]
        for a in masks:
            best={tuple([0]*m):(0.0,None)}
            for b in sorted(itertools.product(*[range(x+1) for x in a]),key=sum):
                if sum(b)==0: continue
                i0=next(j for j in range(m) if b[j]>0); bb=-1e18; arg=None
                for p in itertools.product(*[range(x+1) for x in b]):
                    if p[i0]==0: continue
                    v=best[tuple(b[j]-p[j] for j in range(m))][0]-pw(8*sum(p))+float(yr@pr(p,a))
                    if v>bb: bb=v; arg=p
                best[b]=(bb,arg)
            P=[]; b=a
            while sum(b)>0:
                p=best[b][1]; P.append(p); b=tuple(b[j]-p[j] for j in range(m))
            P=tuple(sorted(P)); red=pw(8*sum(a)+1)+best[a][0]-1+lam+mu*(k-(1 if sum(a)==1 else 0))
            if red>1e-9 and (a,P) not in cols: new.append((red,a,P))
        if not new: break
        cols+=[(a,P) for _,a,P in sorted(new,reverse=True)[:20]]
    F=-r.fun+2*k-2-e
    return F*104/k,[(round(x,4),a,P if len(P)<5 else str(P[:4])+'..') for x,(a,P) in zip(r.x,cols) if x>1e-7],len(rows)
PATTERNS={'tri':[[0,1,1],[1,0,1],[1,1,0]], 'two':[[0,1],[1,0]],
          'nearpencil3':[[0,1,1],[1,0,0],[1,0,0]],   # class0 point = common point c of L1,L2; classes 1,2 points on L0
          'path3':[[0,1,0],[1,0,1],[0,1,0]]}
if __name__=='__main__':
    name=sys.argv[1]; X=int(sys.argv[2]); inc=PATTERNS[name]; m=len(inc)
    for g in map(int,sys.argv[3:]):
        v,sup,nr=run(m,g,inc,X)
        print(f'{name} X{X} m{m} g{g} k{m*g} rows{nr}: chat {v:.4f}',flush=True)
        for x in sup[:6]: print('   ',x,flush=True)

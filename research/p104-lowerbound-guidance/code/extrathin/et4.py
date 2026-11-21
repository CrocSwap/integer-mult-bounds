# EXTRATHIN et4: two-cluster e=1 pattern (m=2, within rank 2, cross rank 1) with ALL SET-RC2 rows:
#   for stage s (group i), partner set T with x stages in own group, y in the other: rank G_{s,T} = 2 if x>=1 else (1 if y>=1).
#   [P, SET-RC2] #{deep(>=l) roles at s, |P|<l, P cap T empty} + #{shallow roles at s meeting T, P cap T empty} >= rank G_{s,T}.
#   averaged over T of composition (x,y): deep piece counts C(g-p_i,x)C(g-p_j,y); shallow counts that minus C(g-a_i,x)C(g-a_j,y).
import os, sys, itertools
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from math import comb
from scipy.optimize import linprog
s=.99; pw=lambda x: x**s
def setup(g,xymax):
    k=2*g; comps=[(x,y) for x in range(0,g) for y in range(0,g+1) if 1<=x+y<=xymax]
    rk=lambda x,y: 2 if x>=1 else 1
    rows=[(l,x,y) for l in range(2,k+1) for (x,y) in comps]
    rhs=np.array([rk(x,y)*k*comb(g-1,x)*comb(g,y) for (l,x,y) in rows],float)
    return k,rows,rhs
def piece_rows(p,a,g,k,rows):
    D=sum(a); L=sum(p); out=np.zeros(len(rows)+2)
    if L==1: out[0]=1; out[1]=1 if D>=2 else 0
    for q,(l,x,y) in enumerate(rows):
        t=0.0
        for i in (0,1):
            if p[i]==0: continue
            j=1-i; av=comb(g-p[i],x)*comb(g-p[j],y)
            if D>=l:
                if L<l: t+=p[i]*av
            else: t+=p[i]*(av-comb(g-a[i],x)*comb(g-a[j],y))
        out[2+q]=t
    return out
def solve(g,e=1,xymax=99,maxit=300):
    k,rows,rhs0=setup(g,xymax); rhs=np.r_[2*k,2*k,rhs0]
    masks=[a for a in itertools.product(range(g+1),repeat=2) if sum(a)>0 and a[0]>=a[1]]
    cache={}
    def pr(p,a):
        key=(p,a)
        if key not in cache: cache[key]=piece_rows(p,a,g,k,rows)
        return cache[key]
    def trow(a,P): return sum(pr(p,a) for p in P)
    def val(a,P): return pw(8*sum(a)+1)-sum(pw(8*sum(p)) for p in P)
    def singles(a): return tuple(sorted([(1,0)]*a[0]+[(0,1)]*a[1]))
    cols=list(dict.fromkeys([(a,singles(a)) for a in masks]+[(a,(a,)) for a in masks if sum(a)>1]))
    for it in range(maxit):
        A=np.array([trow(a,P) for a,P in cols]).T; cost=-np.array([val(a,P)-1 for a,P in cols])
        D1=np.array([1 if sum(a)==1 else 0 for a,P in cols])
        Aub=np.vstack([-A,-np.ones((1,len(cols))),-(k-D1)[None,:]]); bub=np.r_[-rhs,-(2*k-1),-k*(2*k-2-e)]
        r=linprog(cost,A_ub=Aub,b_ub=bub,method='highs')
        y=-r.ineqlin.marginals; lam=y[len(rhs)]; mu=y[len(rhs)+1]; yr=y[:len(rhs)]
        new=[]
        for a in masks:
            best={(0,0):(0.0,None)}
            for b in sorted(itertools.product(range(a[0]+1),range(a[1]+1)),key=sum):
                if sum(b)==0: continue
                i0=0 if b[0]>0 else 1; bb=-1e18; arg=None
                for p in itertools.product(range(b[0]+1),range(b[1]+1)):
                    if p[i0]==0: continue
                    v=best[(b[0]-p[0],b[1]-p[1])][0]-pw(8*sum(p))+float(yr@pr(p,a))
                    if v>bb: bb=v; arg=p
                best[b]=(bb,arg)
            P=[]; b=a
            while sum(b)>0:
                p=best[b][1]; P.append(p); b=(b[0]-p[0],b[1]-p[1])
            P=tuple(sorted(P)); red=pw(8*sum(a)+1)+best[a][0]-1+lam+mu*(k-(1 if sum(a)==1 else 0))
            if red>1e-9 and (a,P) not in cols: new.append((red,a,P))
        if not new: break
        cols+=[(a,P) for _,a,P in sorted(new,reverse=True)[:15]]
    F=-r.fun+2*k-2-e
    return F*104/k,[(round(x,4),a,P if len(P)<6 else str(P[:5])+'..') for x,(a,P) in zip(r.x,cols) if x>1e-7],len(rows)
if __name__=='__main__':
    for g in map(int,sys.argv[2:]):
        v,sup,nr=solve(g,xymax=int(sys.argv[1]))
        print(f'2-cluster e1 setRC2(|T|<={sys.argv[1]}) g{g} k{2*g} rows{nr}: chat {v:.4f}',flush=True)
        for x in sup: print('   ',x,flush=True)

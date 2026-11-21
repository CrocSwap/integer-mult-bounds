# EXTRATHIN et2: GROUPED LP. m groups of g stages (k=mg); pair-rank pattern: within-group pairs rank 2 (RC2 rhs 2),
# cross-group pairs rank c (rhs c in {0,1}).  e excess thins.  Rows: count, MAINS(all singletons)>=2k, DEEP>=2k,
# RC2_l within / cross (l=2..k, per-pair per-piece form of CallerRC2.rc2_pair), leaf d1 <= k T.  Types: mask vector a (sorted),
# pieces = compositions p <= a (column generation, DP pricing).  Symmetric (group/stage permutations) => averaged rows exact.
import os, sys, itertools
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from scipy.optimize import linprog
s=.99
def pw(x): return x**s
def piece_rows(p,a,g,m,k):
    D=sum(a); L=sum(p); r=[0.0]*(3+2*(k-1))
    if L==1: r[0]=1; r[1]=1 if D>=2 else 0
    for li,l in enumerate(range(2,k+1)):
        w=c=0.0
        for i in range(m):
            if p[i]==0: continue
            if D>=l:
                if L<l: w+=p[i]*(g-p[i]); c+=p[i]*sum(g-p[j] for j in range(m) if j!=i)
            else:
                w+=p[i]*(a[i]-p[i]); c+=p[i]*sum(a[j]-p[j] for j in range(m) if j!=i)
        r[2+li]=w; r[2+(k-1)+li]=c
    return np.array(r[:2+2*(k-1)])
def subvecs(b):
    return itertools.product(*[range(x+1) for x in b])
def type_rows(a,P,g,m,k):
    return sum(piece_rows(p,a,g,m,k) for p in P)
def val(a,P): return pw(8*sum(a)+1)-sum(pw(8*sum(p)) for p in P)
def price(a,y,g,m,k):
    # maximize sum_pieces [ -(8L)^s + y . piece_rows ] over partitions of vector a
    a=tuple(a); states=list(subvecs(a)); best={tuple([0]*m):(0.0,None)}
    sc={}
    for b in sorted(states,key=sum):
        if sum(b)==0: continue
        bb=-1e18; arg=None
        # pieces p<=b containing the first nonzero coordinate unit (canonical)
        i0=next(i for i in range(m) if b[i]>0)
        for p in subvecs(b):
            if p[i0]==0: continue
            if p not in sc: sc[p]=-pw(8*sum(p))+float(y@piece_rows(p,a,g,m,k))
            rest=tuple(b[i]-p[i] for i in range(m))
            v=best[rest][0]+sc[p]
            if v>bb: bb=v; arg=p
        best[b]=(bb,arg)
    P=[]; b=a
    while sum(b)>0:
        p=best[b][1]; P.append(p); b=tuple(b[i]-p[i] for i in range(m))
    return pw(8*sum(a)+1)+best[a][0], tuple(sorted(P))
def solve(m,g,c,e,maxit=400):
    k=m*g; nl=k-1
    rhs=np.r_[2*k,2*k,[2*k*(g-1)]*nl,[c*k*(k-g)]*nl]
    masks=[a for a in itertools.product(range(g+1),repeat=m) if sum(a)>0 and list(a)==sorted(a,reverse=True)]
    def singles(a): return tuple(sorted([tuple(1 if j==i else 0 for j in range(m)) for i in range(m) for _ in range(a[i])]))
    cols=[(a,singles(a)) for a in masks]+[(a,(a,)) for a in masks if sum(a)>1]
    cols=list(dict.fromkeys(cols))
    for it in range(maxit):
        A=np.array([type_rows(a,P,g,m,k) for a,P in cols]).T
        cost=-np.array([val(a,P)-1 for a,P in cols])
        D1=np.array([1 if sum(a)==1 else 0 for a,P in cols])
        Aub=np.vstack([-A,-np.ones((1,len(cols))),-(k-D1)[None,:]]); bub=np.r_[-rhs,-(2*k-1),-k*(2*k-2-e)]
        r=linprog(cost,A_ub=Aub,b_ub=bub,method='highs')
        if r.status!=0: return None,None
        y=-r.ineqlin.marginals; lam=y[len(rhs)]; mu=y[len(rhs)+1]
        yr=y[:len(rhs)]
        new=[]
        for a in masks:
            v,P=price(a,yr,g,m,k)
            red=v-1+lam+mu*(k-(1 if sum(a)==1 else 0))
            if red>1e-9 and (a,P) not in cols: new.append((red,a,P))
        if not new: break
        cols+=[(a,P) for _,a,P in sorted(new,reverse=True)[:15]]
    F=-r.fun+2*k-2-e
    sup=[(round(x,3),a,P if len(P)<5 else str(P[:4])+'..') for x,(a,P) in zip(r.x,cols) if x>1e-6]
    return F*104/k, sup
if __name__=='__main__':
    m,g,c,e=map(int,sys.argv[1:5])
    v,sup=solve(m,g,c,e)
    print(f'm{m} g{g} k{m*g} cross{c} e{e}: chat {v:.4f}',flush=True)
    for x in sup: print('   ',x)

# restricted cut families: S subset of {1..h} (0 not in S) with <= R runs
import sys, numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix
def runs(S,n):
    r=0;prev=0
    for i in range(n):
        b=(S>>i)&1
        if b and not prev: r+=1
        prev=b
    return r
def sets_upto(h,R):
    n=h+1
    return [S for S in range(1,1<<n,2*1) if False] 
def gen_sets(h,R):
    # enumerate subsets of {1..h} with <=R runs via boundary choices
    n=h+1
    out=[0]
    import itertools
    pos=list(range(1,n+1))  # boundaries between positions: run starts/ends at 1..n (end exclusive)
    for r in range(1,R+1):
        for bd in itertools.combinations(pos,2*r):
            S=0
            for k in range(r):
                a,b=bd[2*k],bd[2*k+1]
                for i in range(a,b): S|=1<<i
            out.append(S)
    return out
def minbeta(h,L,R):
    n=h+1
    sets=gen_sets(h,R)
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    sep=np.array([1.0 if (((S>>1)&1)==((S>>h)&1) and ((S>>0)&1)==((S>>(h-1))&1) and ((S>>1)&1)!=((S>>0)&1)) else 0.0 for S in sets])
    A=np.array([[1.0 if ((S>>i)&1)!=((S>>j)&1) else 0.0 for S in sets] for (i,j) in pairs])
    b=np.array([min(L,j-i) for (i,j) in pairs],float)
    Aeq=np.hstack([A,-np.ones((len(pairs),1))])
    Aub=np.hstack([-sep,[0.5]]).reshape(1,-1)
    c=np.zeros(len(sets)+1); c[-1]=1
    r=linprog(c,A_ub=Aub,b_ub=[-0.5],A_eq=Aeq,b_eq=b,bounds=[(0,None)]*(len(sets)+1),method='highs')
    return r.x[-1] if r.status==0 else None
if __name__=="__main__":
    h=int(sys.argv[1]);R=int(sys.argv[2])
    print(h,R,[ (L,None if (v:=minbeta(h,L,R)) is None else round(v,4)) for L in range(1,h-1)],flush=True)

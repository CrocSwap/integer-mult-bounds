# PRICEH lp1: per-L minimal helper beta_L (min1 slack) so that min(L,d)+beta*min(1,d) = sum w_S cut_S with sep weight >= (1+beta)/2. float screen.
import sys, itertools, numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
def run(h, Ls=None):
    n=h+1
    sets=[S for S in range(1<<n) if not (S&1)]  # 0 not in S
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    sep=np.array([1.0 if (((S>>1)&1)==((S>>h)&1) and ((S>>0)&1)==((S>>(h-1))&1) and ((S>>1)&1)!=((S>>0)&1)) else 0.0 for S in sets])
    A=np.array([[1.0 if ((S>>i)&1)!=((S>>j)&1) else 0.0 for S in sets] for (i,j) in pairs])
    res={}
    for L in (Ls or range(1,h-1)):
        # vars w (len sets), beta. eq: A w - beta*1 = min(L,d)
        b=np.array([min(L,j-i) for (i,j) in pairs],float)
        Aeq=np.hstack([A,-np.ones((len(pairs),1))])
        # sep: sum sep*w - beta/2 >= 1/2  ->  -sep w + beta/2 <= -1/2
        Aub=np.hstack([-sep,[0.5]]).reshape(1,-1)
        c=np.zeros(len(sets)+1); c[-1]=1
        r=linprog(c,A_ub=Aub,b_ub=[-0.5],A_eq=Aeq,b_eq=b,bounds=[(0,None)]*(len(sets)+1),method='highs')
        res[L]=r.x[-1] if r.status==0 else None
    return res
if __name__=="__main__":
    for h in range(int(sys.argv[1]),int(sys.argv[2])+1):
        print(h,{L:(None if v is None else round(v,4)) for L,v in run(h).items()},flush=True)

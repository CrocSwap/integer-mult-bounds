# LEANTHIN lt1: own reimplementation of the Q>=1, e=0 'one'-pattern LP (rows re-derived from TB.md/ET.md/TQ.md definitions):
#  roles x_{D,P} (D=degree=#stages met, P=partition of D into pieces).  Rows (all >=):
#   MAINS: sum x #singleton pieces >= 2k ; DEEP: sum x [D>=2] #singletons >= 2k ;
#   SETRC2(l,c) l=2..k, c=1..3: sum x sum_pieces p*cov >= 2k C(k-1,c) (cov = C(k-p,c) if D>=l and p<l; C(k-p,c)-C(k-D,c) if D<l; 0 else)
#   COUNT: sum x >= 2k-1 ; LEAFAVG: sum x (k-[D=1]) >= k(2k-2) ; LC: sum x [D>=2] >= k-2 ; TRIPLE: sum x (C(D,3)+C(D,2)(k-D)) >= 3C(k,3)
#  objective F = 2k-2 + sum x (val-1), val=(8D+1)^s - sum (8p)^s ; chat = 104F/k.  Float colgen (HiGHS, 1 thread) + exhaustive pricing.
import os,sys,pickle
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
import numpy as np
from math import comb
from scipy.optimize import linprog
s=.99
def rowlist(k,cmax=3):
    return [(l,c) for c in range(1,min(cmax,k-1)+1) for l in range(2,k+1)]
def piece_coef(k,rows,L,D):
    # vector over SETRC2 rows for one piece of size L in a role of degree D
    out=np.zeros(len(rows))
    for q,(l,c) in enumerate(rows):
        av=comb(k-L,c)
        if D>=l:
            if L<l: out[q]=L*av
        else: out[q]=L*(av-comb(k-D,c))
    return out
def role_vec(k,rows,D,P):
    nm=sum(1 for p in P if p==1)
    v=np.zeros(2+len(rows)+4)
    v[0]=nm; v[1]=nm if D>=2 else 0
    for p in P: v[2:2+len(rows)]+=piece_coef(k,rows,p,D)
    j=2+len(rows)
    v[j]=1; v[j+1]=k-(1 if D==1 else 0); v[j+2]=1 if D>=2 else 0; v[j+3]=comb(D,3)+comb(D,2)*(k-D)
    return v
def rhs(k,rows):
    return np.r_[2*k,2*k,[2*k*comb(k-1,c) for (l,c) in rows],2*k-1,k*(2*k-2),k-2,3*comb(k,3)]
def val(D,P): return (8*D+1)**s-sum((8*p)**s for p in P)
def solve(k,maxit=400,verbose=False):
    rows=rowlist(k); b=rhs(k,rows); nr=len(rows)
    cols=[]
    for D in range(1,k+1):
        cols+= [(D,tuple([1]*D)),(D,(D,))]
        if D>=2: cols.append((D,tuple([2]*(D//2)+[1]*(D%2))))
    cols=list(dict.fromkeys(cols))
    for it in range(maxit):
        A=np.array([role_vec(k,rows,D,P) for D,P in cols]).T; cost=-np.array([val(D,P)-1 for D,P in cols])
        r=linprog(cost,A_ub=-A,b_ub=-b,method='highs')
        y=-r.ineqlin.marginals
        new=price_float(k,rows,y)
        new=[(rc,D,P) for rc,D,P in new if rc>1e-10 and (D,P) not in cols]
        if verbose: print(it,len(cols),-r.fun+2*k-2,len(new),flush=True)
        if not new: break
        cols+=[(D,P) for _,D,P in sorted(new,reverse=True)[:30]]
    F=-r.fun+2*k-2
    return F*104/k,[(x,D,P) for x,(D,P) in zip(r.x,cols) if x>1e-9],y,rows
def price_float(k,rows,y):
    nr=len(rows); yr=y[2:2+nr]; ym,yd=y[0],y[1]; j=2+nr; yc,yl,ylc,yt=y[j:j+4]
    out=[]
    for D in range(1,k+1):
        g=[None]
        for L in range(1,D+1):
            t=-(8*L)**s+float(yr@piece_coef(k,rows,L,D))+(ym+(yd if D>=2 else 0) if L==1 else 0)
            g.append(t)
        best=[0.0]+[None]*D; arg=[None]*(D+1)
        for d in range(1,D+1):
            bb=-1e18
            for L in range(1,d+1):
                v=best[d-L]+g[L]
                if v>bb: bb=v; ar=L
            best[d]=bb; arg[d]=ar
        rc=(8*D+1)**s+best[D]-1+yc+yl*(k-(1 if D==1 else 0))+ylc*(1 if D>=2 else 0)+yt*(comb(D,3)+comb(D,2)*(k-D))
        P=[];d=D
        while d>0: P.append(arg[d]); d-=arg[d]
        out.append((rc,D,tuple(sorted(P))))
    return out
if __name__=='__main__':
    for k in map(int,sys.argv[1:]):
        v,sup,y,rows=solve(k,verbose=False)
        print(f'k{k}: chat {v:.4f}',flush=True)
        for x in sorted(sup,key=lambda t:-t[0])[:12]: print('   ',round(x[0],4),x[1],x[2] if len(x[2])<6 else (x[2][:3],'..',len(x[2])),flush=True)
        pickle.dump((k,v,sup,y,rows),open(f'lt1_k{k}.pkl','wb'))
        nz=[(i,round(float(t),6)) for i,t in enumerate(y) if t>1e-9]
        print('   duals',[(i if i<2 else ('R',rows[i-2]) if i<2+len(rows) else i-2-len(rows),t) for i,t in nz][:40])

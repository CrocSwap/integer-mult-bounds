# F' (Lemma-2 transplant: cost-0 terms dropped, value m(D)<=min(T,|D|)): need min over ALL k-sets D of meet(D) >= ratio*min(k,T)
import sys, numpy as np, time
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import lil_matrix
from geom import *
from units import units
name=sys.argv[1]; idx,T=units[name]
m=len(idx); sets,o=all_orth_sets(idx); mx=maximal(sets,o,m)
nf=len(mx)
# ratio from uniform witness
import fractions

def minmeet(k,fix0):
    # vars x (m binary), z (nf continuous [0,1]); min sum z ; z_F>=x_t
    nv=m+nf; c=np.r_[np.zeros(m),np.ones(nf)]
    rows=sum(bin(M).count('1') for M in mx)+1
    A=lil_matrix((rows,nv)); lb=[];ub=[]; r=0
    for f,M in enumerate(mx):
        for t in range(m):
            if M>>t&1: A[r,m+f]=1; A[r,t]=-1; lb.append(0); ub.append(np.inf); r+=1
    A[r,:m]=1; lb.append(k); ub.append(k); r+=1
    lo=np.zeros(nv); hi=np.ones(nv)
    if fix0: lo[0]=1
    integ=np.r_[np.ones(m),np.zeros(nf)]
    res=milp(c,constraints=LinearConstraint(A.tocsr(),lb,ub),integrality=integ,bounds=Bounds(lo,hi),options={'time_limit':1200,'mip_rel_gap':0})
    return res
for k in range(1,T+1):
    t0=time.time(); res=milp_res=minmeet(k,name in('E8','E7','E6'))
    print(name,'k',k,'status',res.status,'min meet',res.fun,'dual bound',getattr(res,'mip_dual_bound',None),'%.0fs'%(time.time()-t0),flush=True)

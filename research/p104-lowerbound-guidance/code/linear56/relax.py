"""LINEAR56 relax.py: mod-2 RELAXATION of the linear-decoder f problem, in polynomial coordinates.
Row r=(q,p) (points of F2^8, q=B^-1 xbar, p=B^-1 ybar).  Sum_r q p^T = B^-1 (mod 2) is the decoder law mod 2.
U' = sum_r l_q * A(p),  V' = sum_r l_p * A(q),  l_q(z)=B(q,z),  A(p)=Aff_0(p) if p in Z16 (could be tight) else R1 (loose).
Real decoder spaces contain these (monotone), so f(real) >= f(relaxed).  P0 coords: 8 linear + 28 quadratic monomials."""
import numpy as np, itertools
from lcore import *
PAIRS=list(itertools.combinations(range(8),2))
def poly_of_product(u,v,cu=0,cv=0):
    """coefficient vector (36) of (cu + <u,z>)(cv + <v,z>) minus constant term; u,v in F2^8 as linear-form vectors"""
    c=np.zeros(36,np.int64)
    # linear part: cu*v + cv*u + diag(u_i v_i) (z_i^2=z_i)
    c[:8]=(cu*v+cv*u+u*v)%2
    for idx,(i,j) in enumerate(PAIRS): c[8+idx]=(u[i]*v[j]+u[j]*v[i])%2
    return c
def ell(q): return (Bm@q)%2      # linear form z -> B(q,z) as vector
Zset=set(map(tuple,Z16))
def evalZ(c):
    """values of poly c on Z16 points"""
    lin=(Z16@c[:8])%2
    quad=np.zeros(16,np.int64)
    for idx,(i,j) in enumerate(PAIRS):
        if c[8+idx]: quad^=(Z16[:,i]*Z16[:,j])
    return (lin+quad)%2
def row_gens(q,p,tight):
    """generators of l_q * A(p)"""
    lq=ell(q); out=[]
    if tight:
        for w in np.eye(8,dtype=np.int64):
            out.append(poly_of_product(lq,w,0,int(w@p%2)))   # <w,z> + <w,p> vanishes at z=p
    else:
        out.append(poly_of_product(lq,np.zeros(8,np.int64),0,1))
        for w in np.eye(8,dtype=np.int64): out.append(poly_of_product(lq,w))
    return out
def f_relax(rows,tightU=None,tightV=None):
    Ug=[];Vg=[]
    for i,(q,p) in enumerate(rows):
        tu=(tuple(p) in Zset) if tightU is None else tightU[i]
        tv=(tuple(q) in Zset) if tightV is None else tightV[i]
        Ug+=row_gens(q,p,tu); Vg+=row_gens(p,q,tv)
    Ub=rref(np.array(Ug))[0].astype(np.int64); Vb=rref(np.array(Vg))[0].astype(np.int64)
    EU=np.array([evalZ(c) for c in Ub]); EV=np.array([evalZ(c) for c in Vb])
    r=f2rank((EU@EV.T)%2)
    return len(Ub)+len(Vb)-r,len(Ub),len(Vb),r
def law_ok(rows):
    S=np.zeros((8,8),np.int64)
    for q,p in rows: S^=np.outer(q,p)
    return (S==Binv).all()

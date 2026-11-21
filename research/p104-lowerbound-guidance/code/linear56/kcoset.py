"""LINEAR56 kcoset.py: [C] the Z4 solution set of  h_t^T K h_s = 2 delta_ts (mod 4) on odd cells of P104,
for h_t = c_t (8-dim, linear decoders) and h_t = (1,c_t) (9-dim, affine-linear decoders).
Outputs the affine F2-space of liftable Kbar = K mod 2 and its minimum F2 rank (exhaustive)."""
import numpy as np, itertools
from lcore import *
def rref(M):
    M=(np.array(M)%2).astype(np.uint8); r=0; piv=[]
    for c in range(M.shape[1]):
        p=np.nonzero(M[r:,c])[0]
        if len(p)==0: continue
        p=p[0]+r; M[[r,p]]=M[[p,r]]
        nz=np.nonzero(M[:,c])[0]; nz=nz[nz!=r]; M[nz]^=M[r]
        piv.append(c); r+=1
        if r==M.shape[0]: break
    return M[:r],piv
def kernel(M):
    R,piv=rref(M); n=M.shape[1]; free=[c for c in range(n) if c not in piv]; out=[]
    for f in free:
        v=np.zeros(n,np.uint8); v[f]=1
        for i,c in enumerate(piv): v[c]=R[i,f]
        out.append(v)
    return np.array(out,dtype=np.int64).reshape(-1,n)
def solve2(A,b):
    """one solution of A x = b mod 2 or None"""
    M=np.concatenate([A%2,(b%2)[:,None]],1); R,piv=rref(M)
    if A.shape[1] in piv: return None
    x=np.zeros(A.shape[1],np.int64)
    for i,c in enumerate(piv): x[c]=R[i,-1]
    return x
def f2rank(M): return len(rref(M)[1])
n=104
for name,Hh in (('linear d=8',C120[:n]),('affine d=9',np.concatenate([np.ones((n,1),np.int64),C120[:n]],1))):
    d=Hh.shape[1]
    cells=[(t,s) for t in range(n) for s in range(n) if Q[t,s]]
    A=np.array([np.outer(Hh[t],Hh[s]).ravel() for t,s in cells],dtype=np.int64)%4
    r=np.array([2 if t==s else 0 for t,s in cells],dtype=np.int64)
    K2=kernel(A)                      # mod-2 kernel basis
    # phi(k0) = (A k0)/2 mod 2 is linear on ker Abar modulo Im Abar. liftable iff A k0 = r mod 4 solvable in k1.
    # parametrise k0 = sum c_i K2_i ; condition: exists k1: Abar k1 = (r - A k0)/2. Build linear system in (c, k1).
    phis=[((A@k)%4)//2 for k in K2]
    # (r - A k0)/2 = r/2 - sum c_i phi_i  (mod 2, mod Im Abar corrections absorbed by k1)  -> linear in c
    M=np.concatenate([np.array(phis).T if len(phis) else np.zeros((len(A),0),np.int64), A%2],1)
    rhs=(r//2)%2
    base=solve2(M,rhs)
    print(name,'| mod2 kernel dim',len(K2), end=' ')
    if base is None: print('NO Z4 solution'); continue
    hom=kernel(M)   # homogeneous solutions (c,k1)
    cs=set()
    Kb0=(base[:len(K2)]@K2)%2 if len(K2) else np.zeros(d*d,np.int64)
    dirs=[(h[:len(K2)]@K2)%2 for h in hom]
    # span of dirs
    Rd,_=rref(np.array(dirs)) if len(dirs) else (np.zeros((0,d*d)),[])
    print('| liftable Kbar: affine space of dim',len(Rd))
    mr=99; cnt={}
    for coef in itertools.product([0,1],repeat=len(Rd)):
        Kb=(Kb0+np.array(coef)@Rd)%2 if len(Rd) else Kb0
        rk=f2rank(Kb.reshape(d,d)); cnt[rk]=cnt.get(rk,0)+1; mr=min(mr,rk)
    print('   rank distribution of liftable Kbar:',cnt)
    if d==8: print('   Kbar == B ?', len(Rd)==0 and (Kb0.reshape(8,8)==Bm).all())
    else:
        for coef in itertools.product([0,1],repeat=len(Rd)):
            Kb=((Kb0+np.array(coef)@Rd)%2 if len(Rd) else Kb0).reshape(d,d); print('   ',Kb[0].tolist(), 'Kbar[1:,1:]==B', (Kb[1:,1:]==Bm).all(), 'col0',Kb[:,0].tolist())

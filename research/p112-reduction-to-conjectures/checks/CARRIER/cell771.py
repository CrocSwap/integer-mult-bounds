# [7,7,1] root-swap cell: S = C + <q, delta_r>, q = p_r * 1_{Lambda_a}, (Va,Vb) = 127 covering pairs of N(r0).
# Compute V = <r> + sum_phi pi_g(W_phi), W_phi = {(g,c) in K^9 : <l,g> + c q(l) = 0 for all lines l in O_phi \ {r}}.
# n_8 = dim V - 1 ; cost = 78 - n_8 (if S_{<=7} = T).  Violation iff dim V = 8.
import pickle, sys, time
from fractions import Fraction as Fr
from lib import *
pairs=pickle.load(open('pairs771.pkl','rb'))
C=[[Fr(x) for x in l] for l in lines]
r0=0
ip8=lambda a,b: sum(Fr(x)*Fr(y) for x,y in zip(a,b))/4
def rref(rows,ncols):
    A=[list(r) for r in rows]; piv=[]; row=0
    for c in range(ncols):
        p=next((r for r in range(row,len(A)) if A[r][c]!=0),None)
        if p is None: continue
        A[row],A[p]=A[p],A[row]; inv=1/A[row][c]; A[row]=[x*inv for x in A[row]]
        for r in range(len(A)):
            if r!=row and A[r][c]!=0:
                f=A[r][c]; A[r]=[x-f*y for x,y in zip(A[r],A[row])]
        piv.append(c); row+=1
    return A[:row],piv
def nullspace(rows,ncols):
    R,piv=rref(rows,ncols); free=[c for c in range(ncols) if c not in piv]; out=[]
    for f in free:
        v=[Fr(0)]*ncols; v[f]=Fr(1)
        for r,c in enumerate(piv): v[c]=-R[r][f]
        out.append(v)
    return out
Opar=[[t for t in range(n) if par(phi&lab[t])] for phi in range(512)]
def analyse(Ma,Mb):
    # masks over E8 line index bits (bit t = line t)
    La=[t for t in range(n) if Ma>>t&1]
    q=[Fr(0)]*n
    for t in La: q[t]=ip8(lines[r0],lines[t])
    rowsall=[]
    Vg=[ [Fr(int(i==j)) for j in range(8)] for i in range(8)]   # placeholder
    gens=[list(C[r0])]   # r itself
    dimW={}
    for phi in range(1,512):
        L=[t for t in Opar[phi] if t!=r0]
        rows=[C[t]+[q[t]] for t in L]
        N=nullspace(rows,9)
        if N:
            dimW[phi]=len(N)
            for v in N: gens.append(v[:8])
    R,_=rref(gens,8)
    return len(R),dimW
if __name__=='__main__':
    c0,K=int(sys.argv[1]),int(sys.argv[2])
    res=[]
    for i,(Ma,Mb) in enumerate(pairs):
        if i%K!=c0: continue
        # try both assignments (q on Va or on Vb): by symmetry of roles q ~ p_r1_Va vs p_r1_Vb - Sum differ by T, same S. do one.
        d,dimW=analyse(Ma,Mb)
        print(i,'dimV',d,'nonzeroW',len(dimW),'maxdimW',max(dimW.values()) if dimW else 0,flush=True)

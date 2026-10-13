"""B14 decoder model (E8 roots, P112 = 120 root lines minus the 8 frame lines e_{2a} +- e_{2a+1}, labels in F2^9, Thm-C pairing-rank cost). Self-contained; unchanged apart from this docstring."""
import itertools, numpy as np
from fractions import Fraction

def e8_roots():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for si in (1,-1):
            for sj in (1,-1):
                v=[0]*8; v[i]=2*si; v[j]=2*sj; R.append(tuple(v))   # scaled by 2
    for s in itertools.product((1,-1),repeat=8):
        if s.count(-1)%2==0: R.append(tuple(s))
    return np.array(R)  # 240 x 8, scaled x2 ; ip = dot/4
# simple roots basis (Bourbaki-ish), scaled x2
def basis():
    B=[]
    B.append([1,-1,-1,-1,-1,-1,-1,1])  # (1/2)(e1+e8-e2..e7)
    B.append([2,2,0,0,0,0,0,0])
    B.append([-2,2,0,0,0,0,0,0])
    for k in range(1,6):
        v=[0]*8; v[k]=-2; v[k+1]=2; B.append(v)
    return np.array(B)
def build():
    R=e8_roots(); B=basis()
    Gb=(B@B.T)//4
    assert round(abs(np.linalg.det(Gb)))==1
    C=np.rint(np.linalg.solve(B.T.astype(float),R.T.astype(float))).T.astype(int) # coords of roots
    assert (C@B==R).all()
    # lines: pick one rep per +-
    seen={};lines=[]
    for i,r in enumerate(R):
        key=tuple(r) if tuple(r)>tuple(-r) else tuple(-r)
        if key not in seen: seen[key]=i; lines.append(i)
    assert len(lines)==120
    Rl=R[lines]; Cl=C[lines]%2
    # frame: e1+-e2 etc (scaled 2*(e_i+-e_j) -> (2,2,0..)):
    frame=[]
    for a in range(4):
        for s in (1,-1):
            v=[0]*8; v[2*a]=2; v[2*a+1]=2*s; frame.append(tuple(v))
    fidx=[]
    for f in frame:
        for k,r in enumerate(Rl):
            if tuple(r)==f or tuple(-r)==f: fidx.append(k)
    P=[k for k in range(120) if k not in fidx]
    assert len(P)==112
    return Rl,Cl,Gb%2,np.array(fidx),np.array(P)
Rl,Cl,Gb2,fidx,P=build()
RP=Rl[P]; Fr=Rl[fidx]
G=(RP@RP.T)//4            # integer E8 inner products
Ln=np.concatenate([Cl[P],np.ones((112,1),int)],1)   # labels in F2^9
S9=np.zeros((9,9),int); S9[:8,:8]=Gb2; S9[8,8]=1       # form
LS=(Ln@S9)%2            # row i: label_i S
DOT=(Ln@S9@Ln.T)%2      # label pairing
# 2G as integer target (N=G/2 -> 4N = 2G)
M4=2*G
X=(RP@Fr.T)//4          # 112x8, entries 0,+-1 : <r,f_j>
def rank2(rows):
    """F2 rank of list of ints (bitmask rows)"""
    rows=list(rows); r=0
    basis=[]
    for v in rows:
        for b in basis: v=min(v,v^b)
        if v: basis.append(v)
    return basis
def tomask(mat): return [int(''.join(map(str,row)),2) for row in mat]
LSm=[int(''.join(map(str,row)),2) for row in LS]    # label_i * S as bitmask
Lm =[int(''.join(map(str,row)),2) for row in Ln]
def span_basis(masks):
    basis=[]
    for v in masks:
        for b in basis: v=min(v,v^b)
        if v: basis.append(v)
    return basis
def pair_rank(Rset,Aset):
    """rank of pairing (span U(R)) x (span U(A)) over F2"""
    if len(Rset)==0 or len(Aset)==0: return 0
    vb=span_basis([LSm[i] for i in Rset])      # vectors u S
    wb=span_basis([Lm[i] for i in Aset])
    # matrix entries parity(vb & wb)
    rows=[]
    for v in vb:
        row=0
        for k,w in enumerate(wb):
            row|=(bin(v&w).count('1')&1)<<k
        rows.append(row)
    return len(span_basis(rows))
def cost(D,T):
    return sum(pair_rank(np.nonzero(D[:,k])[0],np.nonzero(T[:,k])[0]) for k in range(D.shape[1]))
def exact(D,T,scale=1):
    return (D@T.T==M4*scale).all()
if __name__=="__main__":
    print("G offdiag values",np.unique(G[~np.eye(112,dtype=bool)]),"orth pairs per row",(DOT[0]==0).sum()-0)
    print("L support = label-orth pairs?", ((G!=0)&~np.eye(112,dtype=bool) == ((DOT==0)&~np.eye(112,dtype=bool))).all())
    print("diag dot",set(DOT.diagonal()))
    print("stars",[int((X[:,j]!=0).sum()) for j in range(8)])
    D=X.copy(); T=X.copy()
    print("coord exact(4N=sum xx^T *?)",exact(D,T,1), "cost",cost(D,T),[pair_rank(np.nonzero(D[:,k])[0],np.nonzero(T[:,k])[0]) for k in range(8)])

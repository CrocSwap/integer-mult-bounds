# AUDIT-SC independent P112 model (D8 coordinates doubled; own lattice basis for labels; own frame code).
import itertools, numpy as np
R=[]
for i,j in itertools.combinations(range(8),2):
    for a in (2,-2):
        for b in (2,-2):
            v=[0]*8; v[i]=a; v[j]=b; R.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: R.append(s)
assert len(R)==240
def canon(v):
    for x in v:
        if x: return tuple(v) if x>0 else tuple(-y for y in v)
LINES=sorted({canon(r) for r in R}); NL=len(LINES); assert NL==120
LA=np.array(LINES,dtype=np.int64)
IP=(LA@LA.T)//4                                  # true inner products
assert (np.diag(IP)==2).all()
# lattice basis: first 8 roots (in a fixed pseudo-random order, seed 7) with Gram det 1 (unimodular => basis of E8)
import random
rng=random.Random(7); order=list(range(240)); rng.shuffle(order)
Bv=[]
for k in order:
    cand=Bv+[list(R[k])]
    M=np.array(cand,dtype=float); g=M@M.T/4
    if abs(np.linalg.det(g))>0.5: Bv=cand
    if len(Bv)==8:
        if round(np.linalg.det(np.array(Bv,dtype=float)@np.array(Bv,dtype=float).T/4))==1: break
        Bv=Bv[:7]
Bm=np.array(Bv,dtype=float)
assert round(np.linalg.det(Bm@Bm.T/4))==1
Binv=np.linalg.inv(Bm)
co=np.rint(LA@Binv).astype(np.int64); assert np.allclose(co@Bm,LA)
cls=(co%2)
LAB=np.array([1|int(sum(int(b)<<(k+1) for k,b in enumerate(c))) for c in cls])   # 9-bit labels, bit0 = affine 1
assert len(set(LAB.tolist()))==120
FRAME=[LINES.index(canon(tuple(v))) for v in ([2,2,0,0,0,0,0,0],[2,-2,0,0,0,0,0,0],[0,0,2,2,0,0,0,0],[0,0,2,-2,0,0,0,0],[0,0,0,0,2,2,0,0],[0,0,0,0,2,-2,0,0],[0,0,0,0,0,0,2,2],[0,0,0,0,0,0,2,-2])]
assert all(IP[a,b]==0 for a in FRAME for b in FRAME if a!=b)
P=[i for i in range(NL) if i not in FRAME]; NP=len(P); assert NP==112
PL=LAB[P]
def f2rank(vs):
    b=[]
    for x in vs:
        x=int(x)
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)

import json, numpy as np, itertools, random
from fractions import Fraction as Fr
import os
D=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'data.json')))
L=np.array(D['L']); v=112
L2=np.rint(L*2).astype(np.int64)            # 2*L integer
Gm=L2@L2.T                                   # 4*Gram
Bd=(Gm==0).astype(np.int64); np.fill_diagonal(Bd,1)
BD=[sum(int(Bd[t][s])<<s for s in range(v)) for t in range(v)]
def rho_mask(Rm,Am):
    b=[]
    t=0
    while Rm:
        low=Rm&-Rm; t=low.bit_length()-1; Rm^=low
        x=BD[t]&Am
        for y in b: x=min(x,x^y)
        if x: b.append(x)
    return len(b)
def mask(S):
    m=0
    for t in S: m|=1<<t
    return m
# E8 roots scaled by 2 (integer): D8 type (+-2,+-2) and spinor (+-1)^8 even minus
def e8roots():
    r=[]
    for i,j in itertools.combinations(range(8),2):
        for a in (1,-1):
            for b in (1,-1):
                x=[0]*8; x[i]=2*a; x[j]=2*b; r.append(tuple(x))
    for s in itertools.product((1,-1),repeat=8):
        if s.count(-1)%2==0: r.append(tuple(s))
    return np.array(r,dtype=np.int64)
E8=e8roots()
def frames():
    R=E8; n=len(R); G0=R@R.T
    rep=[i for i in range(n) if next(c for c in R[i] if c!=0)>0]
    out=set()
    def dfs(cur,cands):
        if len(cur)==8: out.add(tuple(cur)); return
        for k,j in enumerate(cands):
            dfs(cur+[j],[c for c in cands[k+1:] if G0[j,c]==0])
    dfs([],rep)
    return [list(f) for f in out]

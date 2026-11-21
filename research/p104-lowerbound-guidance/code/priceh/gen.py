# PRICEH gen.py: exact molecule certificates for label rank h.  Usage: gen.py h [h ...]  -> mol_h{h}.json
# For L=1..h-2: molecule M_L = D*min(L,d)+E*min(1,d), exact nonneg integer cut decomposition on heights 0..h (masks, bit i = height i in S, 0 not in S),
# separating weight (S∩{0,1,h-1,h} = {1,h} or {0,h-1}) with 2*sep >= D+E.   L=h-1: windows, sep 0.
# float LP (scipy HiGHS) only to FIND support; everything certified in Fractions (verify.py is the independent checker).
import sys, json, itertools, numpy as np
from fractions import Fraction as Fr
from math import lcm
from scipy.optimize import linprog
def gen_sets(h,R):
    n=h+1; out=[]
    pos=list(range(1,n+1))
    for r in range(1,R+1):
        for bd in itertools.combinations(pos,2*r):
            S=0
            for k in range(r):
                for i in range(bd[2*k],bd[2*k+1]): S|=1<<i
            out.append(S)
    return out
def issep(S,h):
    b=lambda i:(S>>i)&1
    return (b(1) and b(h) and not b(0) and not b(h-1)) or ((not b(1)) and (not b(h)) and b(0) and b(h-1))
def mats(h,sets):
    n=h+1
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    A=np.array([[1.0 if ((S>>i)&1)!=((S>>j)&1) else 0.0 for S in sets] for (i,j) in pairs])
    sep=np.array([1.0 if issep(S,h) else 0.0 for S in sets])
    return pairs,A,sep
def minbeta(h,L,sets,pairs,A,sep,fixed=None):
    b=np.array([min(L,j-i) for (i,j) in pairs],float)
    Aeq=np.hstack([A,-np.ones((len(pairs),1))]); Aub=np.hstack([-sep,[0.5]]).reshape(1,-1)
    c=np.zeros(len(sets)+1); c[-1]=1
    bnds=[(0,None)]*len(sets)+[(0,None) if fixed is None else (float(fixed),float(fixed))]
    r=linprog(c,A_ub=Aub,b_ub=[-0.5],A_eq=Aeq,b_eq=b,bounds=bnds,method='highs-ds')
    return r
def exact_solve(h,L,beta,sets,support):
    n=h+1
    pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
    cols=[sets[k] for k in support]
    rows=[]; rhs=[]
    for (i,j) in pairs:
        rows.append([Fr(1 if ((S>>i)&1)!=((S>>j)&1) else 0) for S in cols]); rhs.append(Fr(min(L,j-i))+beta)
    rows.append([Fr(1 if issep(S,h) else 0) for S in cols]); rhs.append((1+beta)/2)
    m=len(rows); k=len(cols)
    M=[rows[r]+[rhs[r]] for r in range(m)]
    piv=[]; r=0
    for c in range(k):
        p=next((x for x in range(r,m) if M[x][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        iv=1/M[r][c]; M[r]=[v*iv for v in M[r]]
        for x in range(m):
            if x!=r and M[x][c]!=0:
                f=M[x][c]; M[x]=[a-f*b for a,b in zip(M[x],M[r])]
        piv.append(c); r+=1
    for x in range(r,m):
        if M[x][k]!=0: return None
    w=[Fr(0)]*k
    for rr,c in enumerate(piv): w[c]=M[rr][k]
    if any(v<0 for v in w): return None
    return {cols[c]:w[c] for c in range(k) if w[c]!=0}
def windows(h):
    W={}
    for j in range(2,h): W[sum(1<<i for i in range(j,h+1))]=Fr(1)
    W[1]=Fr(1,2); W[1<<h]=Fr(1,2); W[1|(1<<h)]=Fr(1,2)   # {0}->bit0 ; sets here may contain 0 (checked by verify)
    return W
def to_int(W,beta_fr):
    D=lcm(*[v.denominator for v in W.values()],beta_fr.denominator)
    return D,[(S,int(v*D)) for S,v in sorted(W.items())]
def run(h):
    sets2=gen_sets(h,2); p2,A2,s2=mats(h,sets2)
    out={'h':h,'mol':{}}
    for L in range(1,h-1):
        if L==1:
            for R in (3,4,5):
                S_=gen_sets(h,R); P_,A_,sp_=mats(h,S_)
                r=minbeta(h,L,S_,P_,A_,sp_)
                if r.status==0: break
        else: S_,P_,A_,sp_=sets2,p2,A2,s2; r=minbeta(h,L,S_,P_,A_,sp_)
        assert r.status==0,(h,L,r.status)
        bf=r.x[-1]; beta=Fr(bf).limit_denominator(200)
        assert abs(float(beta)-bf)<1e-7,(h,L,bf)
        r2=minbeta(h,L,S_,P_,A_,sp_,fixed=beta)
        assert r2.status==0,(h,L,'fixed beta infeasible',beta)
        sup=[k for k,v in enumerate(r2.x[:-1]) if v>1e-10]
        W=exact_solve(h,L,beta,S_,sup)
        if W is None:  # fall back: all columns with positive weight plus try bigger support is not needed normally
            raise SystemExit(f'exact solve failed h={h} L={L} beta={beta}')
        D,lst=to_int(W,beta)
        E=int(beta*D)
        out['mol'][L]={'D':D,'E':E,'W':lst}
        print(h,L,'beta',beta,'D',D,'cuts',len(lst),flush=True)
    Wn=windows(h); D,lst=to_int(Wn,Fr(0))
    out['mol'][h-1]={'D':D,'E':0,'W':lst}
    json.dump(out,open(f'mol_h{h}.json','w'))
if __name__=="__main__":
    for h in sys.argv[1:]: run(int(h))

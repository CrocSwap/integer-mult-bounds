# phi_s refinement logic (p=3). w=(w0,w1,w2): line t's projection onto the A2 plane, in R^3/(1).
# t with pieces K (set of k with t in L_k) and (if t in E_S) small piece s: need w in span(1,e_k:k in K) + R*phi  (phi in R^3/1 = functional of the small piece)
from fractions import Fraction as Fr
def rank(rows):
    M=[[Fr(x) for x in r] for r in rows]; rk=0
    if not M: return 0
    for c in range(len(M[0])):
        p=next((i for i in range(rk,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[rk],M[p]=M[p],M[rk]
        for i in range(len(M)):
            if i!=rk and M[i][c]!=0:
                f=M[i][c]/M[rk][c]; M[i]=[a-f*b for a,b in zip(M[i],M[rk])]
        rk+=1
    return rk
def bad(w,K):   # pair-cover fails without small piece: w not constant on complement of K
    Kc=[k for k in range(3) if k not in K]
    return len({w[k] for k in Kc})>1
def compat(phi,w,K):   # w in span(1,e_K,phi) ?
    Kc=[k for k in range(3) if k not in K]
    if not Kc: return True
    one=[1]*len(Kc); ph=[phi[k] for k in Kc]; ww=[w[k] for k in Kc]
    return rank([one,ph])==rank([one,ph,ww])
def norm(w):   # direction of w mod 1 (and sign): subtract w0, scale
    v=[Fr(x-w[0]) for x in w]
    if all(x==0 for x in v): return None
    m=next(x for x in v if x!=0); return tuple(x/abs(m) for x in v)
def phis(ws):
    D={norm(w) for w in ws}-{None}
    D=sorted(D); D.append((Fr(0),Fr(1),Fr(1000003)))   # generic phi, last
    return D

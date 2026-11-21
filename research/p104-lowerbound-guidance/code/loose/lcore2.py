"""LOOSE lane core (own code). B-linear rows y in L4=Z4^8 (functional: v(s)=C[s].y mod 4).
price(y,D) = rank_F2 Q[D, S_y], S_y = mod-4 support. Z4 span membership via Howell-style reduction."""
import sys, numpy as np, itertools
sys.path.insert(0,'../linear56'); sys.path.insert(0,'../nonlin')
from ncore import *
hint=[int(sum(int(H[t,i])<<i for i in range(9))) for t in range(n)]
Yc=(C@G)%4          # Yc[t] = functional of port root c_t  (C G since G symmetric)
Yz=(Z@G)%4          # tight functionals
def S_of(y): return np.nonzero((C@y)%4)[0]
def price(y,D):
    D=list(D)
    if not D: return 0
    S=S_of(y)
    if len(S)==0: return 0
    return f2rank(Q[np.ix_(D,S)])
# ---- Z4 module membership by double annihilator (Z4 self-injective) ----
Xall=np.array(list(itertools.product(range(4),repeat=8)),np.int64)
def z4_in_span(rows,c):
    rows=np.atleast_2d(np.array(rows,np.int64))%4
    if rows.size==0: return not np.any(np.array(c)%4)
    ann=~(((Xall@rows.T)%4).any(1))
    return not ((Xall[ann]@np.array(c,np.int64))%4).any()
def z4_span_set(rows):
    S={tuple([0]*8)}
    for r in rows:
        r=np.array(r)%4; new=set()
        for s in S:
            for a in range(4): new.add(tuple((np.array(s)+a*r)%4))
        S=new
    return S

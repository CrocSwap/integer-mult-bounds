"""DEN4 deep.py (own code): DEEP-PORT LEMMA check. mu(t)=min_k v2 w_k(t), nu(t)=min_k v2 v_k(t); claim mu+nu<=e for all t and C >= #{mu+nu=e}.
Also the row/col-normalised P''_0 restricted to deep ports must be unitriangular in mu-order (forced part = I)."""
import numpy as np, sympy, sys
from qlib import *
def val(x,cap):
    if x==0: return cap
    k=0
    while x%2==0: x//=2; k+=1
    return k
def deepcheck(e,W,V,pr,Q,name):
    M=2**(e+1); n=len(Q)
    mu=[min(val(int(x)%M,e+1) for x in W[t]) for t in range(n)]
    nu=[min(val(int(x)%M,e+1) for x in V[t]) for t in range(n)]
    assert all(mu[t]+nu[t]<=e for t in range(n))
    deep=[t for t in range(n) if mu[t]+nu[t]==e]
    # forced part of P''_0 on deep x deep: entries with mu(t)+nu(s)<=e must equal delta_ts
    S=((W%M)@(V%M).T)*Q   # integer sum mod M suffices for the coefficient check below
    bad=0
    for t in deep:
        for s in deep:
            l=mu[t]+nu[s]
            if l<=e:
                # coefficient of x^l in P(t,s) = (sum_{i+j=l} digit products) mod 2 = bit l of S(t,s) because no lower terms exist
                if ((S[t,s]>>l)&1)!=(1 if t==s else 0): bad+=1
    print(name,'e',e,'C',sum(pr),'#deep',len(deep),'forced-entry violations',bad)
    assert sum(pr)>=len(deep) and bad==0

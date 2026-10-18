# CONJB CHECKED (exact): span facts used by Theorem G, for P112, P104, E8.
# S1: r(O_u) spans r_u^perp (rank 7) for every line u.  S2: r(O_u ∩ O_u') spans <r_u,r_u'>^perp (rank 6) for all u != u'.
# Ranks are GF(p) ranks of integer matrices = lower bounds over Q; the upper bounds 7 / 6 hold trivially.
import os, sys, itertools
from setup9 import load, E8
from fractions import Fraction as Fr
from modrank import rkp
for unit in ['P112','P104','E8']:
    L=list(E8) if unit=='E8' else load(unit)[0]
    R=[[Fr(x) for x in r] for r in L]; v=len(R)
    dot=lambda x,y: sum(a*b for a,b in zip(x,y))
    G=[[dot(R[i],R[j]) for j in range(v)] for i in range(v)]
    O=[set(s for s in range(v) if G[u][s]==0) for u in range(v)]
    s1=min(rkp([R[s] for s in O[u]]) for u in range(v))
    s2=min(rkp([R[s] for s in O[u]&O[w]]) for u,w in itertools.combinations(range(v),2))
    print(unit,'lines',v,'S1 min rank',s1,'(need 7)','S2 min rank',s2,'(need 6)')
    assert s1==7 and s2==6
    print('PASS spans',unit)

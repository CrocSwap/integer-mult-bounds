# CONJB (S1)/(S2) for E8: r(O_u) spans r_u^perp (rank 7) for every u; r(O_u cap O_u') spans <r_u,r_u'>^perp (rank 6) for u != u'.  Ranks mod 2^61-1 (lower bounds over Q; the upper bounds 7, 6 are trivial), hence over every field of characteristic 0.
import itertools
from e8lib import E,N,O
from modrank import rkp
from fractions import Fraction as Fr
R=[[Fr(x) for x in r] for r in E]
s1=min(rkp([R[s] for s in O[u]]) for u in range(N))
s2=min(rkp([R[s] for s in O[u]&O[w]]) for u,w in itertools.combinations(range(N),2))
print('E8 lines',N,'S1 min rank',s1,'(need 7)','S2 min rank',s2,'(need 6)')
assert s1==7 and s2==6
print('PASS spans E8')

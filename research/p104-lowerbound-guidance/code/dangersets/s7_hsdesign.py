# Exact half-spin decoder from the orthogonal D8 frame {e1+-e2, e3+-e4, e5+-e6, e7+-e8}: O = sum_k a_k b_k^T, a_k = E r_k, b_k = E r_k/|r_k|^2.
import numpy as np
from fractions import Fraction as F
from ds_lib import *; from ds_rank import *
L=e8_lines(); P=halfspin(L); n=len(P); Q=Qmat(P)
fr=[]
for i in range(0,8,2):
    for s in (1,-1):
        r=np.zeros(8,dtype=np.int64); r[i]=2; r[i+1]=2*s; fr.append(r)
terms=[(r,r) for r in fr]
# exactness: O[l,l'] = sum_k (l.u)(l'.w)/(u.w) ; need O = I on Q-cells
O=[[sum(F(int(P[a]@u)*int(P[b]@w),int(u@w)) for u,w in terms) for b in range(n)] for a in range(n)]
ok=all((O[a][b]==(P[a]@P[b])) for a in range(n) for b in range(n))  # O = Gram (scale 8)
ok2=all((O[a][b]==(8 if a==b else 0)) for a in range(n) for b in range(n) if Q[a,b])
lab=Labels(Q); cost=0; rs=[]
for u,w in terms:
    A=[i for i in range(n) if P[i]@u!=0]; B=[i for i in range(n) if P[i]@w!=0]
    r=rank2(Q[np.ix_(A,B)]); rs.append((len(A),len(B),r)); cost+=r
print('O == Gram:',ok,' N o O = 8 I on mask:',ok2)
print('terms (|A|,|B|,rho):',rs,' total cost',cost,' per port',F(cost,n))
# denominators of normalised decoder O/8 : entries (l.u)(l'.w)/(8 u.w)
dens=set()
for u,w in terms:
    for a in range(n):
        for b in range(n):
            x=F(int(P[a]@u)*int(P[b]@w),8*int(u@w))
            if x: dens.add(x.denominator)
print('per-term entry denominators of normalised rows:',sorted(dens))

# Danger probe: half-spin + D8 lines under the orthogonal-frame Gram design (u_k = w_k = r_k). Greedy add, exact F2 ranks.
import numpy as np
from fractions import Fraction as F
from ds_lib import *
L=e8_lines(); Qall=Qmat(L); n=120
hs=[i for i in range(n) if np.all(np.abs(L[i])==1)]; d8=[i for i in range(n) if i not in hs]
fr=[]
for i in range(0,8,2):
    for s in (1,-1):
        r=np.zeros(8,dtype=np.int64); r[i]=2; r[i+1]=2*s; fr.append(r)
supp=[set(np.nonzero(L@r)[0].tolist()) for r in fr]
def cost(P):
    return sum(rank2(Qall[np.ix_(sorted(S&P),sorted(S&P))]) if S&P else 0 for S in supp)
P=set(hs); c=cost(P); print('start halfspin v',len(P),'c',c,'h',hrank(L[sorted(P)]))
rest=list(d8)
while rest:
    best=None
    for l in rest:
        cc=cost(P|{l})
        if best is None or cc<best[0]: best=(cc,l)
    P.add(best[1]); rest.remove(best[1]); c=best[0]
    v=len(P); h=hrank(L[sorted(P)])
    flag=' <-- below 7/13' if F(c,v)<F(7,13) else ''
    print(f'v {v} c {c} h {h} ratio {c/v:.4f}{flag}')

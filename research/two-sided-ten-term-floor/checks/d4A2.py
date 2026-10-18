import sys, pickle, itertools, numpy as np
from lib import Bd, C, n
from collections import Counter
surv=pickle.load(open('d4A_surv.pkl','rb'))
print('(0,1,2,3) is a block:', any(set(np.nonzero(C[t])[0])=={0,1,2,3} for t in range(n)))
h=Counter()
for c,ws in surv:
    roots=[t for t in range(n) if all(sum(C[t][k]*C[w][k] for k in range(8))==0 for w in ws)]
    # max pairwise non-orthogonal (Bd=0) subset
    best=0
    for r in range(1,len(roots)+1):
        if any(all(Bd[a][b]==0 for a,b in itertools.combinations(S,2)) for S in itertools.combinations(roots,r)): best=r
        else: break
    h[(len(roots),best)]+=1
print('(#roots ⟂ all four c_w, max pairwise non-orth set):',sorted(h.items()))

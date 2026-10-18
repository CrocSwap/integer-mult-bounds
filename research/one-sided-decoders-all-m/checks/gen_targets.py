# targets h with |Off(h)| <= 73 in P112: f (8), roots (112), norm-4 (D7 type) with <=3 frame lines in h^perp. Writes targets.txt, labs.txt
import sys
from base import *
import numpy as np, itertools
R=np.array([list(r) for r in E8L],dtype=float)
P=np.array([list(r) for r in L],dtype=float); F=np.array([list(f) for f in F0],dtype=float)
def key(v):
    v=np.round(v*2).astype(int); 
    for x in v:
        if x!=0: return tuple(v if x>0 else -v)
cand={}
for v in list(R)+list(F): cand[key(v)]=v
G=R@R.T
for a in range(len(R)):
    for b in range(a+1,len(R)):
        if abs(G[a,b])<1e-9:
            for s in (1,-1): cand.setdefault(key(R[a]+s*R[b]),R[a]+s*R[b])
out=[]; from collections import Counter; C=Counter()
for k,h in cand.items():
    off=[t for t in range(112) if abs(P[t]@h)>1e-9]
    if len(off)<=73: out.append(off); C[(round(float(h@h)),len(off))]+=1
print(C)
open('targets.txt','w').write('\n'.join(' '.join(map(str,o)) for o in out)+'\n')
open('labs.txt','w').write(' '.join(map(str,LAB))+'\n')

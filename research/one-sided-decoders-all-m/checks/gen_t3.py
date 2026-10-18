# targets with |Off(h)| <= 75 in P112: adds E6+A1 hyperplanes (norm-6 normals) with no frame line inside. Writes targets75.txt
import sys
from base import *
import numpy as np
from collections import Counter
R=np.array([list(r) for r in E8L],dtype=float); P=np.array([list(r) for r in L],dtype=float); F=np.array([list(f) for f in F0],dtype=float)
def key(v):
    v=np.round(v*2).astype(int)
    for x in v:
        if x!=0: return tuple(v if x>0 else -v)
cand={}
G=R@R.T
for a in range(len(R)):
    cand.setdefault(key(R[a]),R[a])
    for b in range(len(R)):
        if a==b: continue
        for s in (1,-1):
            ip=s*G[a,b]
            if abs(ip)<1e-9 or abs(ip-1)<1e-9:
                v=R[a]+s*R[b]; cand.setdefault(key(v),v)
C=Counter(); out=[]
for k,h in cand.items():
    e8perp=int((np.abs(R@h)<1e-9).sum())
    off=[t for t in range(112) if abs(P[t]@h)>1e-9]
    C[(round(float(h@h)),e8perp,len(off))]+=1
    if len(off)<=int(sys.argv[1]) if len(sys.argv)>1 else len(off)<=75: out.append(off)
for k in sorted(C): print(k,C[k])
open('targets%s.txt'%(sys.argv[1] if len(sys.argv)>1 else '75'),'w').write('\n'.join(' '.join(map(str,o)) for o in out)+'\n'); print(len(out))

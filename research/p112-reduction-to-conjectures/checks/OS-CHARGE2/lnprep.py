# prep for independent Lemma N check: labels and all Off(h) sets with |Off|<=76 (P112)
import json, itertools, numpy as np
D=json.load(open('data.json')); L=np.array(D['L']); E8=np.array(D['E8']); v=len(L)
allr=list(E8)+[-r for r in E8]
offs={}
def off(h): return tuple(t for t in range(v) if abs(L[t]@h)>1e-9)
for r in E8: offs.setdefault(off(r),'r')
for a,b in itertools.combinations(range(len(allr)),2):
    s=allr[a]+allr[b]
    if round(s@s)==4: offs.setdefault(off(s),'n4')
sel=[o for o in offs if len(o)<=76]
from collections import Counter
print(len(sel),Counter((len(o),offs[o]) for o in sel))
with open('ln_in.txt','w') as f:
    print(*D['LAB'],file=f)
    print(len(sel),file=f)
    for o in sel: print(len(o),*o,file=f)

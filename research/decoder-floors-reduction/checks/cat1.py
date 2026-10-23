# WALL catalogue: for every label functional phi (511) and every direction h with |Off(h)|<=76 (complete list, OS-CHARGE2 lnprep),
# compute |O_phi ∩ Off(h)|, O_phi = {s : phi(u_s)=1}. Small values = outside-column corrections possible at small outside support.
import json, itertools, numpy as np
from collections import Counter, defaultdict
D=json.load(open('data.json')); L=np.array(D['L']); E8=np.array(D['E8']); LAB=D['LAB']; Z=D['Z']; v=len(L)
F0=np.array(D['F0'])
par=lambda x: bin(x).count('1')&1
O={phi: frozenset(s for s in range(v) if par(phi&LAB[s])) for phi in range(1,512)}
# identify phi of line type: phi_t(u_s)=Bd[t,s]
Bd=[[1 if (t==s or abs(L[t]@L[s])<1e-9) else 0 for s in range(v)] for t in range(v)]
linephi={}
for t in range(v):
    S=frozenset(s for s in range(v) if Bd[t][s])
    m=[p for p in O if O[p]==S]; assert len(m)==1; linephi[m[0]]=t
# frame phantoms: phi with O_phi = lines orthogonal to f_i
framephi={}
for i,f in enumerate(F0):
    S=frozenset(s for s in range(v) if abs(L[s]@f)<1e-9)
    m=[p for p in O if O[p]==S]; framephi[m[0] if m else None]=i
print('frame phi found:',[k for k in framephi])
allr=list(E8)+[-r for r in E8]
dirs={}
def off(h): return frozenset(t for t in range(v) if abs(L[t]@h)>1e-9)
for r in E8: dirs.setdefault(off(r),('r',tuple(r)))
for a,b in itertools.combinations(range(len(allr)),2):
    s=allr[a]+allr[b]
    if round(s@s)==4: dirs.setdefault(off(s),('n4',tuple(s)))
sel={o:dirs[o] for o in dirs if len(o)<=76}
print('directions',len(sel), Counter(len(o) for o in sel))
print('|O_phi| range',min(len(x) for x in O.values()),max(len(x) for x in O.values()))
res=[]
for o,(kind,h) in sel.items():
    for phi,S in O.items():
        n=len(S&o)
        if n<=12: res.append((n,kind,len(o),phi))
cnt=Counter((n,kind,lo, 'line' if phi in linephi else ('frame' if phi in framephi else 'other')) for n,kind,lo,phi in res)
for k in sorted(cnt): print(k,cnt[k])

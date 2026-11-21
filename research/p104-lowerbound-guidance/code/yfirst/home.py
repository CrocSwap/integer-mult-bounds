# token-home moments: helper h with row == {h:1} and no other register holding coefficient on h, at a MOVE of h
import sys; sys.path.insert(0,'../fewstops')
from load import *
from fractions import Fraction as Q
from collections import Counter, defaultdict
N=n+W['owned_fields']; rows=[{r:Q(1)} if r<n else {} for r in range(N)]
occ=defaultdict(set)  # token -> registers holding it
for r in range(n): occ[r].add(r)
def setrow(r,new):
    old=rows[r]
    for k in old:
        if k not in new: occ[k].discard(r)
    for k in new:
        if k not in old: occ[k].add(r)
    rows[r]=new
home=[]; movesH=0
ishelper=[r<n and kind(r)=='H' for r in range(N)]
nmoves=Counter(e[1] for e in P if e[0]=='MOVE' and e[1]<n)
seen=Counter()
for i,e in enumerate(P):
    op,r=e[0],e[1]
    if op=='MOVE':
        if r<n and ishelper[r]:
            seen[r]+=1
            if seen[r]>1:   # not the first move: there is a past with moves
                movesH+=1
                if rows[r]=={r:Q(1)} and occ[r]=={r}: home.append((i,r,seen[r]))
        continue
    if op=='INIT' or op=='CLEAR': setrow(r,{}); continue
    if op=='SCALE':
        q=Q(e[2]); setrow(r,{k:v*q for k,v in rows[r].items()}); continue
    s=e[2]; q=Q(e[3]); R=dict(rows[r])
    for k,v in rows[s].items():
        nv=R.get(k,0)+q*v
        if nv: R[k]=nv
        else: R.pop(k,None)
    setrow(r,R)
print('helper non-first moves',movesH,'token-home at move',len(home))
print(home[:20])
# also: clean (row==e_h) but residues elsewhere

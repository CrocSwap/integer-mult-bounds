import sys
from common import *
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2])
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
hf={int(k):span(f) for k,f in w['helper_final'].items()}
P,Pinv,comp=main_maps(w)
res=Counter();cands=[]
for h in range(2*v,n):
    if h in hf: continue
    supp={g for g,x in Pinv[h].items() if x}|{g for g in range(n) if P[g].get(h)}|{h}
    J=span([x for g in supp for x in endB[g]])
    kind='cold' if start[h]==() else 'E%d'%len(start[h])
    res[(kind,len(J))]+=1
    if len(J)<=8: cands.append((h,kind,len(J),endB[h],len(supp)))
print(sorted(res.items()))
for c in cands: print(c)

# level-2 targets: S = P112 \ (lines in an E6 = roots orthogonal to an A2), deduped, orbit reps under sym.py group
import numpy as np, json
from targ import L2, E8
from sym import G, idx
P=[tuple(r) for r in L2]
Ss=set()
for i in range(120):
    for j in range(i+1,120):
        if abs(E8[i]@E8[j])==4:
            Ss.add(frozenset(t for t in range(112) if L2[t]@E8[i]!=0 or L2[t]@E8[j]!=0))
Ss=list(Ss); print('E6 targets',len(Ss),'sizes',sorted(set(len(s) for s in Ss)))
PI=[[idx[tuple(M@r)] for r in L2] for M in G]
seen=set(); reps=[]
for s in Ss:
    if s in seen: continue
    reps.append(sorted(s)); st=[s]; seen.add(s)
    while st:
        x=st.pop()
        for pi in PI:
            y=frozenset(pi[t] for t in x)
            if y not in seen: seen.add(y); st.append(y)
print('orbits',len(reps),[len(r) for r in reps])
json.dump(reps,open('e6reps.json','w'))

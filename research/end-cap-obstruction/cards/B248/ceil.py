import climbs as C,step0 as S
from collections import Counter
w=C.load();log,start,end=C.climbs(w);v=112
S4=range(592,704)
pat=Counter();mass=0;prof=Counter()
for q in S4:
    pat[(len(start[q]),len(end[q]))]+=1
    for d,_ in log[q]:prof[d]+=1;mass+=d
print('S4 start/end dims',pat);print('S4 paid profile',dict(sorted(prof.items())),'mass',mass)
base={1:2412,2:418,3:432,4:142,5:82,8:8}
k0=S.kapG(S.kg(base,{}))
l=dict(base)
for r,n in prof.items():l[r]-=n
import math
for tag,ex in (('mass->H48',{48:mass*72/48}),('mass->H16',{16:mass*72/16})):
    ex={r:int(round(n)) for r,n in ex.items()}
    k=S.kapG(S.kg(l,ex));print(tag,ex,None if k is None else (k,100*(k-k0)/k0))

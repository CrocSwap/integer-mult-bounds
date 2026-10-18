import json,collections
import ev
from ev import *
T0=[list(e) for e in TAIL0]
tr=[];pp,_=prof.profile(w,tr)
by=collections.defaultdict(list)
for q,tag,a,b in tr:by[q].append((tag,a,b))
rows=[];cls=collections.Counter()
for k,e in enumerate(T0):
    rs=regs(e)
    for q in rs:
        L=by[q];idx=[j for j,(t,a,b) in enumerate(L) if t==('T',k)]
        if not idx or idx[0]+1>=len(L):continue
        j=idx[0];nxt=L[j+1];o=[x for x in rs if x!=q][0]
        d1=L[j][2]-L[j][1];d2=nxt[2]-nxt[1]
        # who forces the next climb: end cap of partner?
        capped=len(end[o])<nxt[2]
        kind='%s->%s'%(L[j][0][0],nxt[0][0])
        rows.append((k,q,o,d1,d2,nxt[0],len(end[q]),len(end[o]),capped))
        cls[(kind,'partner_end_cap' if capped else 'partner_uncapped',d1,d2)]+=1
for c,v_ in sorted(cls.items(),key=lambda x:-x[1]):print(v_,c)
print(len(rows))
json.dump(rows,open('splits.json','w'))

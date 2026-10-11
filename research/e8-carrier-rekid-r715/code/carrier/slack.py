# frame slack: how far can each rule's frame be raised (meet of its consumers' frames)?
import os,sys,json,ast
os.environ['E8COORD']='ham'
import e8lib as E, frames as Fm, ham2, compile2 as C2
from collections import Counter, defaultdict
V=E.V
Pd={ast.literal_eval(k):v for k,v in json.load(open('params-r740.json'))}
ham2.P.clear(); ham2.P.update(Pd)
h=ham2.build(0,True)
needed=C2.needed_symbols(h); ph=C2.phases(h,needed); low=C2.choose_low(h,needed,ph)
par=defaultdict(list); rd=defaultdict(list)
for w in needed:
    if w>=V:
        for c in h.kids[w]: par[c].append(w)
for t in range(V):
    for u in h.need[t]: rd[u].append((t,(t,u) in low))
def meet(a,b): return Fm.closure(a&b)[0]
st=Counter(); ex=[]
for w in sorted(needed):
    if w<V: continue
    up=Fm.FULL
    for p in par[w]: up=meet(up,h.frame[p])
    for t,lw in rd[w]:
        up=meet(up,h.frame[w] if lw else Fm.HYP[t])
    s=Fm.dim(up)-h.dim[w]
    st[(h.dim[w],bin(h.content[w]).count('1'),s)]+=1
for k in sorted(st): print('dim,n,slack',k,st[k])

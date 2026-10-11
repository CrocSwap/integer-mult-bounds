import os,sys,json,ast,time,pickle
os.environ['E8COORD']='ham'
import ham2, compile2 as C2, compile as C, frames as Fm, e8lib as E
from collections import Counter,defaultdict
Pd={ast.literal_eval(k):v for k,v in json.load(open('params-r865.json'))}
ham2.P.clear(); ham2.P.update(Pd)
h=ham2.build(0,True)
V=120
needed=C2.needed_symbols(h)
print('symbols total',len(h.content)-V,'needed',len(needed)-120)
# pool per target: existing symbols (composite, nonempty) with frame subset of HYP[t]
sizes=[]
for t in range(V):
    pool=[u for u in range(V,len(h.content)) if Fm.inside(h.frame[u],Fm.HYP[t])]
    sizes.append(len(pool))
print('pool size per target min/avg/max',min(sizes),sum(sizes)/V,max(sizes))
# sources in E7(t) also
# distribution of dim
c=Counter(h.dim[u] for u in range(V,len(h.content)))
print(c)
pickle.dump(h,open('h865.pkl','wb'))

import os,sys,json,ast,time
os.environ['E8COORD']='ham'
import ham2, compile2 as C2, compile as C, frames as Fm, e8lib as E
from collections import Counter,defaultdict
Pd={ast.literal_eval(k):v for k,v in json.load(open('params-r865.json'))}
ham2.P.clear(); ham2.P.update(Pd)
h=ham2.build(0,True)
V=120
needed=C2.needed_symbols(h); ph=C2.phases(h,needed)
lowset=C2.choose_low(h,needed,ph)
# replicate chain computation
from collections import defaultdict
uses=defaultdict(list)
for w in needed:
    if w<V: continue
    po=0 if ph[w]=='A' else 1
    for c in h.kids[w]: uses[c].append((po,h.dim[w],0,h.frame[w],w))
for t in range(V):
    for u in h.need[t]:
        if (t,u) in lowset: uses[u].append((1,h.dim[u],1,h.frame[u],t))
        else: uses[u].append((1,7,1,Fm.HYP[t],t))
nch={}
for u in needed:
    ev=sorted(uses[u],key=lambda e:(e[0],e[1],e[2],e[4]))
    cl=[]
    for e in ev:
        best=None
        for i,ch in enumerate(cl):
            last=ch[-1]
            if last[2]==1 and last[1]==7 and last[3]!=e[3]: continue
            if last[3]==e[3] or (last[1]<e[1] and Fm.inside(last[3],e[3])):
                if best is None or cl[best][-1][1]<last[1]: best=i
        if best is None: cl.append([e]); best=len(cl)-1
        else: cl[best].append(e)
    nch[u]=len(cl)
def size(u): return bin(h.content[u]).count('1')
tab=defaultdict(lambda:[0,0,0,0])
for u in needed:
    k=('src' if u<V else 'sz%d_d%d'%(size(u),h.dim[u]))
    nuse=len(uses[u])
    tab[k][0]+=1; tab[k][1]+=nch[u]; tab[k][2]+=nch[u]-1; tab[k][3]+=nuse
print('kind nsym chains excess uses')
for k,v in sorted(tab.items()): print(k,v)
print(sum(v[2] for v in tab.values()))
# how many readers per delivered symbol
dl=Counter()
for t in range(V):
    for u in h.need[t]: dl[u]+=1
print('delivered symbols by (size,dim,nusers):')
c=Counter((size(u),h.dim[u],n) for u,n in dl.items())
for k,v in sorted(c.items()): print(k,v)
print('reads/target', sum(len(h.need[t]) for t in range(V))/V, 'low',len(lowset))

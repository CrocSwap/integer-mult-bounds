# anatomy of the R863 producer word (params-r740): register causes
import os,sys,json,ast
os.environ['E8COORD']='ham'
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import e8lib as E, frames as Fm, ham2, compile2 as C2
from collections import Counter, defaultdict
V=E.V
Pd={ast.literal_eval(k):v for k,v in json.load(open(sys.argv[1] if len(sys.argv)>1 else 'params-r740.json'))}
ham2.P.clear(); ham2.P.update(Pd)
h=ham2.build(0,True)
W=C2.compile2(h)
print(W.stats)
needed=C2.needed_symbols(h); ph=C2.phases(h,needed)
low=C2.choose_low(h,needed,ph)
# uses per node
uses=defaultdict(list)
for w in needed:
    if w<V: continue
    for c in h.kids[w]: uses[c].append(('P',ph[w],h.dim[w],w))
for t in range(V):
    for u in h.need[t]:
        uses[u].append(('L' if (t,u) in low else 'H', 'B', h.dim[u] if (t,u) in low else 7, t))
# recompute chains like compile2
def nchains(u):
    ev=[]
    for k,phz,d,who in uses[u]:
        po=0 if phz=='A' else 1
        kind=0 if k=='P' else 1
        fr=h.frame[who] if k=='P' else (h.frame[u] if k=='L' else Fm.HYP[who])
        ev.append((po,d,kind,fr,who))
    ev.sort(key=lambda e:(e[0],e[1],e[2],e[4]))
    cl=[]
    for e in ev:
        best=None
        for i,ch in enumerate(cl):
            last=ch[-1]
            if last[2]==1 and last[1]==7 and last[3]!=e[3]: continue
            if last[3]==e[3] or (last[1]<e[1] and Fm.inside(last[3],e[3])):
                if best is None or cl[best][-1][1]<last[1]: best=i
        if best is None: cl.append([e])
        else: cl[best].append(e)
    return cl
def cat(u):
    if u<V: return 'src_frame' if sum(1 for a in E.LINES[u] if a)==1 else 'src_cw'
    d=h.dim[u]; n=bin(h.content[u]).count('1')
    return 'd%d_n%d'%(d,n)
agg=defaultdict(Counter)
for u in needed:
    cl=nchains(u)
    U=uses[u]; H=sum(1 for x in U if x[0]=='H'); L=sum(1 for x in U if x[0]=='L'); Pa=sum(1 for x in U if x[0]=='P')
    PA=sum(1 for x in U if x[0]=='P' and x[1]=='A'); PB=Pa-PA
    a=agg[cat(u)]
    a['n']+=1; a['chains']+=len(cl); a['H']+=H; a['L']+=L; a['PA']+=PA; a['PB']+=PB
    a['extra_over_H']+=len(cl)-max(H,1)
    # parent frame antichain lower bound (pairwise incomparable parents)
for k in sorted(agg): print(k,dict(agg[k]))
tot=Counter()
for k in agg:
    tot.update(agg[k])
print('TOTAL',dict(tot))

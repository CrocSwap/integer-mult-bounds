# exact identity R = X + Delta - S - 120 + F + 9 on the producer word, and path-end classes
import os,sys,json,ast
os.environ['E8COORD']='ham'
import e8lib as E, frames as Fm, ham2, compile2 as C2
from collections import Counter, defaultdict
V=E.V
Pd={ast.literal_eval(k):v for k,v in json.load(open(sys.argv[1]))}
ham2.P.clear(); ham2.P.update(Pd)
h=ham2.build(0,True)
needed=C2.needed_symbols(h); ph=C2.phases(h,needed); low=C2.choose_low(h,needed,ph)
uses=defaultdict(list)
for w in needed:
    if w<V: continue
    for c in h.kids[w]: uses[c].append((0,h.dim[w],0,h.frame[w],w))
for t in range(V):
    for u in h.need[t]:
        if (t,u) in low: uses[u].append((1,h.dim[u],1,h.frame[u],t))
        else: uses[u].append((1,7,1,Fm.HYP[t],t))
chains={};chain_of={}
for u in needed:
    ev=sorted(uses[u],key=lambda e:(e[0],e[1],e[2],e[4])); cl=[]
    for e in ev:
        best=None
        for i,ch in enumerate(cl):
            last=ch[-1]
            if last[2]==1 and last[1]==7 and last[3]!=e[3]: continue
            if last[3]==e[3] or (last[1]<e[1] and Fm.inside(last[3],e[3])):
                if best is None or cl[best][-1][1]<last[1]: best=i
        if best is None: cl.append([e]); best=len(cl)-1
        else: cl[best].append(e)
        chain_of[(u,e[2],e[4])]=best
    chains[u]=cl
# hosting as compile2: host = first kid whose chain ends at w and is a helper (or carrier); x registers can't host
rules=[w for w in needed if w>=V]
X=sum(len(h.kids[w])-1 for w in rules)
nrules=len(rules)
# simulate reg ownership: sources' x-chain choice
xchain={}
for s in range(V):
    if s not in needed: continue
    cl=chains[s]; cand=[i for i,ch in enumerate(cl) if all(e[0]==0 for e in ch)]
    xchain[s]=max(cand,key=lambda i:len(cl[i])) if cand else None
hosted=0; ends=Counter(); midnonhost=0
def ishelper(c,i): return not (c<V and xchain.get(c)==i)
for w in sorted(rules,key=lambda w:(h.dim[w],w)):
    info=[]
    for c in h.kids[w]:
        i=chain_of[(c,0,w)]; ch=chains[c][i]
        info.append((c,i,ch[-1][2]==0 and ch[-1][4]==w))
    host=None
    for c,i,end in info:
        if end and ishelper(c,i): host=(c,i); break
    if host: hosted+=1
    for c,i,end in info:
        if (c,i)==host: continue
        if end: ends['nonhost_death_'+('src' if c<V else 'd%d'%h.dim[c])]+=1
        else: midnonhost+=1
for u in needed:
    for ch in chains[u]:
        last=ch[-1]
        if last[2]==1: ends['deliv_high' if last[1]==7 else 'deliv_low_d%d'%h.dim[u]]+=1
nchains=sum(len(c) for c in chains.values())
print('rules',nrules,'binary XORs X',X,'chains',nchains,'hosted',hosted,'fresh',nrules-hosted,'mid-chain nonhost S',midnonhost)
print('path ends',dict(sorted(ends.items())),'total',sum(ends.values()))
Delta=sum(v for k,v in ends.items() if k.startswith('deliv'))
F=nrules-hosted
print('identity: X+Delta-S-120+F+9 =',X+Delta-midnonhost-120+F+9, '(Delta=%d)'%Delta)
# x registers end at totals (not counted as path ends here)

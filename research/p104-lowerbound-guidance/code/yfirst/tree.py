import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter, defaultdict
# union stays at dims 1..4 that share an op
cur=list(W['initial'])+[None]*W['owned_fields']
par={}
def fd(x):
    par.setdefault(x,x)
    while par[x]!=x: par[x]=par[par[x]]; x=par[x]
    return x
def un(a,b): par[fd(a)]=fd(b)
ver=defaultdict(int)  # stay version per reg
opsby=defaultdict(list)
for i,e in enumerate(P):
    op,r=e[0],e[1]
    if op=='MOVE': cur[r]=e[3]; ver[r]+=1; continue
    if op=='INIT': cur[r]=e[2]; ver[r]+=1; continue
    if op=='CLEAR': continue
    c=e[4] if op in('ADD','COPY') else e[3]
    if not (1<=dim[c]<=4): continue
    regs=[e[1],e[2]] if op in('ADD','COPY') else [e[1]]
    ks=[(x,ver[x]) for x in regs]
    for k in ks: fd(k)
    if len(ks)==2: un(ks[0],ks[1])
    opsby[fd(ks[0])].append(i)
comp=defaultdict(list)
for k in par: comp[fd(k)].append(k)
sizes=sorted(((len(v),c) for c,v in comp.items()),reverse=True)
print('components',len(comp),'top sizes',[s for s,_ in sizes[:20]])
print('reg-kind mix of top comps')
for s,c in sizes[:12]:
    print(s,Counter(kind(r) for r,_ in comp[c]))

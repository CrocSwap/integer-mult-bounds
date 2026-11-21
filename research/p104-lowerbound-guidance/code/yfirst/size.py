# YFIRST sizing: kappa if helper chart paths were compressed by a rule (optimistic histogram estimate, mains untouched)
import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter
paths={r:[dim[W['initial'][r]]] for r in range(n)}
for e in P:
    if e[0]=='MOVE' and e[1]<n: paths[e[1]].append(dim[e[3]])
nat=pk.native_from_word(W); ci=pk.caller_invoice(C)
def kap(rule):
    Pn=Counter(nat['P'])
    for r in range(n):
        if kind(r)!='H': continue
        p=paths[r]; q=rule(p)
        for a,b in zip(p,p[1:]): Pn[b-a]-=1
        for a,b in zip(q,q[1:]):
            if b>a: Pn[b-a]+=1
    inv=pk.invoice(ci,dict(nat,P=+Pn)); return str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:12]
rules={
 'none':lambda p:p,
 'single jump (helpers floor)':lambda p:[p[0],p[-1]],
 'keep first stop only':lambda p:[p[0],p[1],p[-1]] if len(p)>2 else p,
 'keep first+last-before-final':lambda p:[p[0],p[1],p[-2],p[-1]] if len(p)>3 else p,
 'keep last-before-final only':lambda p:[p[0],p[-2],p[-1]] if len(p)>2 else p,
 'drop dims 2,3 stops (tree flatten)':lambda p:[d for i,d in enumerate(p) if i in(0,len(p)-1) or d not in(2,3)],
 'drop dims 1,2,3 stops':lambda p:[d for i,d in enumerate(p) if i in(0,len(p)-1) or d not in(1,2,3)],
}
for k,f in rules.items(): print(f'{k:40s}',kap(f))
print('t7669 ref .0037214260438636')
print('--- drop intermediate stops at a dim set')
for S in [(1,),(2,),(3,),(4,),(5,),(6,),(7,),(8,),(6,7,8),(1,2,3),(5,6,7,8)]:
    print(S, kap(lambda p,S=S:[d for i,d in enumerate(p) if i in(0,len(p)-1) or d not in S]))

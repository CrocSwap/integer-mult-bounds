# Optimistic sizing of INTERLEAVE's swap-courier on t7669: helpers whose last stay before the final jump is a stop that
# deposits into a Y/Y2 main at that main's FINAL chart become swap-couriers ending there (no jump to 9, no cleanup).
import sys; sys.path.insert(0,'../fewstops')
from load import *
from collections import Counter
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
paths={r:[dim[W['initial'][r]]] for r in range(n)}
for e in P:
    if e[0]=='MOVE' and e[1]<n: paths[e[1]].append(dim[e[3]])
cand=set(); yfin={r:W['final'][r] for r in range(n) if kind(r) in('Y','Y2')}
for r in range(n):
    if kind(r)!='H': continue
    S=stays[r]
    if len(S)<3: continue
    s=S[-2]
    if any(kind(p) in('Y','Y2') and yfin[p]==s['f'] for _,p,_ in s['outs']+s['ins']): cand.add(r)
print('candidates',len(cand), Counter(tuple(paths[r][-2:]) for r in cand).most_common(5))
nat=pk.native_from_word(W); ci=pk.caller_invoice(C)
Pn=Counter(nat['P']); Tn=Counter(nat['T'])
for r in cand:
    p=paths[r]; Pn[p[-1]-p[-2]]-=1; Tn[p[-1]-p[0]]-=1; Tn[p[-2]-p[0]]+=1
inv=pk.invoice(ci,dict(nat,P=+Pn,T=+Tn)); print('optimistic swap-courier ending kappa',str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:12])
# how many candidates hold content that is cleaned at the final chart (gates at final stay)?
g=Counter()
for r in cand:
    s=stays[r][-1]; g[min(len(s['ins'])+len(s['outs']),50)//10*10]+=1
print('candidates: #gates at final (dim-9) stay, binned',sorted(g.items()))

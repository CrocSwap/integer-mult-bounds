import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter
print('n',n,'owned',W['owned_fields'],'kinds',Counter(kind(r) for r in range(n)))
print('ops',Counter(e[0] for e in P))
# Y registers: stays and partners
tot=Counter()
for r in range(n):
    k=kind(r)
    if k not in('Y','Y2'): continue
    for s in stays[r]:
        c=Counter(kind(p) for _,p,_ in s['ins']+s['outs'])
        tot[(k,dim[s['f']],tuple(sorted(c)))]+=1
for k,v in sorted(tot.items()): print(k,v)

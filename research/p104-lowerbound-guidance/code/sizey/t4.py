import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter
Yk=('Y','Y2'); pur=Counter()
for r in range(n):
    if kind(r)!='H': continue
    st=stays[r]
    for j,s in enumerate(st[1:-1],1):
        ks=set(kind(p) for _,p,_ in s['ins']+s['outs'])
        d=dim[s['f']]
        pur[(d, 'Y' if ks&set(Yk) else '-', ','.join(sorted(ks-set(Yk))) )]+=1
for k,v in sorted(pur.items()): print(k,v)

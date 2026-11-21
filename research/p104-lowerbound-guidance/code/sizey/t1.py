import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter
rows=[]
for r in range(n):
    k=kind(r)
    if k not in('Y','Y2'): continue
    chain=[dim[s['f']] for s in stays[r]]
    ds=[(dim[s['f']],s['f'],Counter(kind(p) for _,p,_ in s['ins']+s['outs'])) for s in stays[r] if s['f']!=stays[r][0]['f'] and (s['ins'] or s['outs'])]
    nonH=[d for d in ds]
    rows.append((r,k,chain,ds))
hist=Counter(); histH=Counter(); histdel=Counter()
for r,k,chain,ds in rows:
    hist[len(ds)]+=1
print('Y/Y2 count',len(rows))
print('#stays (dim>=1) with any meeting, per Y:',sorted(hist.items()))
# deliveries by partner kind classes
cls=Counter()
for r,k,chain,ds in rows:
    for d,f,c in ds:
        cls[(k,d,tuple(sorted(c)))]+=0
# ops count per Y by partner kind, per dim>=1
tot=Counter(); tot0=Counter()
for r,k,chain,ds in rows:
    for s in stays[r]:
        for _,p,_ in s['ins']+s['outs']:
            (tot0 if s['f']==stays[r][0]['f'] else tot)[(kind(p))]+=1
print('ops at dim>=1 stays by partner kind',dict(tot)); print('ops at initial stay',dict(tot0))
print('chain-length hist',sorted(Counter(len(c) for _,_,c,_ in rows).items()))
print('chains',Counter(tuple(c) for _,_,c,_ in rows).most_common(15))
# per Y: distinct meeting charts excluding final? 
fin=Counter(); 
for r,k,chain,ds in rows:
    fin[(len(ds), ds[-1][0] if ds else None)]+=1
print(sorted(fin.items()))

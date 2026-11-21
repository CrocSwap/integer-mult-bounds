import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter,defaultdict
Ys=[r for r in range(n) if kind(r) in('Y','Y2')]
per=defaultdict(dict)  # Y -> {stayidx:(dim,ops,helpers)}
for r in Ys:
    for j,s in enumerate(stays[r]):
        if j==0: continue
        hs=[p for _,p,_ in s['ins']+s['outs'] if kind(p)=='H']
        if hs: per[r][j]=(dim[s['f']],len(hs),len(set(hs)))
nch=Counter(len(per[r]) for r in Ys); print('Y by #distinct H-delivery charts (dim>=1):',sorted(nch.items()), ' Ys with none:',sum(1 for r in Ys if not per[r]))
bydim=Counter(); opsd=Counter(); helpd=Counter()
for r in Ys:
    for j,(d,o,h) in per[r].items(): bydim[d]+=1; opsd[d]+=o; helpd[d]+=h
print('delivery charts by dim:',dict(sorted(bydim.items())),'ops',dict(sorted(opsd.items())),'sum helpers',dict(sorted(helpd.items())))
sig=Counter(tuple(sorted((d,o) for d,o,h in per[r].values())) for r in Ys); 
print('top signatures (dim,ops) per Y:'); [print(' ',k,v) for k,v in sig.most_common(12)]
# helper ops/Y ops histogram
print('deliveries per chart hist:',sorted(Counter(o for r in Ys for d,o,h in per[r].values()).items()))
# also: per Y total H delivery ops (dim>=1)
print('H-ops per Y:',sorted(Counter(sum(o for d,o,h in per[r].values()) for r in Ys).items()))
# direction: ins (Y receives) vs outs
di=Counter()
for r in Ys:
    for j,s in enumerate(stays[r]):
        if j==0: continue
        for _,p,_ in s['ins']:
            if kind(p)=='H': di[('in',dim[s['f']])]+=1
        for _,p,_ in s['outs']:
            if kind(p)=='H': di[('out',dim[s['f']])]+=1
print('Y<-H (in) / Y->H (out) by dim',sorted(di.items()))
import pickle; pickle.dump(dict(per),open('per.pkl','wb'))

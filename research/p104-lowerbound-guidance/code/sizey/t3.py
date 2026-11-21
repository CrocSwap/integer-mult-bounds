import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter,defaultdict
Yk=('Y','Y2')
H=[r for r in range(n) if kind(r)=='H']
cl=Counter(); pathsig=Counter(); nY=Counter()
hy=[]  # helpers having Y-delivery stops
for r in H:
    st=stays[r]; sig=[]
    for j,s in enumerate(st):
        pk_=Counter(kind(p) for _,p,_ in s['ins']+s['outs'])
        isY=any(k in pk_ for k in Yk) and dim[s['f']]>=1  # meets Y at non-dim0 chart => (y chart stays)
        sig.append((dim[s['f']], 'Y' if isY else ('' ))
                   )
        cl[(dim[s['f']],tuple(sorted(pk_)))]+=0
    ny=sum(1 for _,t in sig if t=='Y')
    nY[ny]+=1
    if ny: hy.append(r)
print('helpers by #Y-delivery stops',sorted(nY.items()),'of',len(H))
# is the Y-meet at helper's stay really at Y's chart? helper stay chart == Y's stay chart necessarily (co-located).
# stops of Y-delivering helpers: path & which are Y stops
sig=Counter()
for r in hy:
    sg=tuple((dim[s['f']],'Y' if (dim[s['f']]>=1 and any(kind(p) in Yk for _,p,_ in s['ins']+s['outs'])) else '') for s in stays[r])
    sig[sg]+=1
for k,v in sig.most_common(25): print(v,' '.join(f'{d}{t}' for d,t in k))
# for Y-delivery helpers: total stops, Y stops, other
tot=Counter()
for r in hy:
    st=stays[r]; tot['stops']+=len(st)-2; tot['ystops']+=sum(1 for s in st if dim[s['f']]>=1 and any(kind(p) in Yk for _,p,_ in s['ins']+s['outs']))
print(dict(tot),'all-helper stops',sum(len(stays[r])-2 for r in H))

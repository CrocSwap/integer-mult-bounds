import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter
Yk={'Y','Y2'}; fin=W['final']
def info(s): return set(kind(p) for _,p,_ in s['ins']+s['outs'])
bl=Counter(); blk_first=Counter(); mult=Counter()
for r in range(n):
    if kind(r)!='H': continue
    st=stays[r]; p=[dim[s['f']] for s in st]
    yst=[j for j,s in enumerate(st[1:-1],1) if info(st[j])&Yk and p[j]<8]
    if not yst: continue
    Ys={y for s in st[1:-1] for _,y,_ in s['ins']+s['outs'] if kind(y) in Yk}
    Fs={fin[y] for y in Ys}
    if len(Fs)==1:
        F=next(iter(Fs))
        bad=[s for s in st[1:-1] if not SP[s['f']]<=SP[F]]
        if bad:
            ks=set().union(*[info(s) for s in bad]) 
            bl[(tuple(sorted('X' if k in('X','X2') else k for k in ks)), 'bad dims '+','.join(str(dim[s['f']]) for s in bad))]+=1
    else:
        # does the multi-F helper's Y stops sit at different dims? which dims of Y stops
        mult[tuple((dim[st[j]['f']]) for j in yst)]+=1
for k,v in sorted(bl.items(),key=lambda x:-x[1])[:15]: print(k,v)
print('multiF y-stop dims',mult.most_common(10))
# single-F-feasible A: how many of the stops they'd drop; also which Y stops dims

import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter
Yk={'Y','Y2'}
nat=pk.native_from_word(W); ci=pk.caller_invoice(C)
fin=W['final']
def info(s): return set(kind(p) for _,p,_ in s['ins']+s['outs'])
# Y finals
print('Y final dims',Counter(dim[fin[r]] for r in range(n) if kind(r) in Yk))
print('distinct Y final charts',len({fin[r] for r in range(n) if kind(r) in Yk}), 'Y/Y2 pairs sharing chart: ',Counter(Counter(fin[r] for r in range(n) if kind(r) in Yk).values()))
cat=Counter(); feas=[]; Pn=Counter(nat['P']); res=Counter()
for r in range(n):
    if kind(r)!='H': continue
    st=stays[r]
    ystops=[(j,s) for j,s in enumerate(st[1:-1],1) if info(s)&Yk and dim[s['f']]<8]
    if not ystops: continue
    # all Ys met at dim>=1 stays
    Ys={y for s in st[1:-1] for _,y,_ in s['ins']+s['outs'] if kind(y) in Yk}
    Fs={fin[y] for y in Ys}
    mid=[s['f'] for s in st[:-1]]  # all non-final stops incl first
    top=max((s['f'] for s in st[1:-1]), key=lambda f:dim[f], default=None)
    nonY=[s for s in st[1:-1] if not(info(s)&Yk)]
    # chart that must be inside F: all stops that are not the dim-9 end
    stops=[s['f'] for s in st[1:-1]]
    topf=max(stops,key=lambda f:dim[f])
    if len(Fs)==1:
        F=next(iter(Fs)); ok=SP[topf]<=SP[F]
        cat[('oneF', 'chart-feasible' if ok else 'top not in F')]+=1
        # also feasibility if only the Y stops (and earlier) need be inside F
        ys_top=max((s['f'] for _,s in ystops),key=lambda f:dim[f])
        cat[('oneF-Ytop⊆F',SP[ys_top]<=SP[F])]+=1
    else:
        cat[('multiF',len(Fs))]+=1
for k,v in sorted(cat.items(),key=str): print(k,v)

def kap(which, extra_cost=False):
    Pn=Counter(nat['P']); Tn=Counter(nat['T']); sel=Counter()
    for r in range(n):
        if kind(r)!='H': continue
        st=stays[r]; p=[dim[s['f']] for s in st]
        yst=[j for j,s in enumerate(st[1:-1],1) if info(st[j])&Yk and p[j]<8]
        if not yst: continue
        Ys={y for s in st[1:-1] for _,y,_ in s['ins']+s['outs'] if kind(y) in Yk}
        Fs={fin[y] for y in Ys}
        stops=[s['f'] for s in st[1:-1]]; topf=max(stops,key=lambda f:dim[f])
        if len(Fs)==1:
            F=next(iter(Fs)); cls='A' if SP[topf]<=SP[F] else 'B'
        else: cls='C'
        sel[cls]+=1
        if cls not in which: continue
        q=[p[0]]+[p[j] for j in range(1,len(st)-1) if j not in yst]+[p[-1]]
        if max(q[1:-1],default=0)<8 and p[-1]==9: q=q[:-1]+[8,9]
        for a,b in zip(p,p[1:]): Pn[b-a]-=1
        for a,b in zip(q,q[1:]):
            if b>a: Pn[b-a]+=1
        if extra_cost and cls=='C':
            for _ in range(len(Fs)-1): Pn[8]+=1; Pn[1]+=1; Tn[9]+=1   # extra courier helper 0->8->9
    inv=pk.invoice(ci,dict(nat,P=+Pn,T=+Tn)); return str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:12],dict(sel)
print('A chart-feasible only',kap('A'))
print('A+B (re-chart top)',kap('AB'))
print('A+B+C free',kap('ABC'))
print('A+B+C paid extra couriers',kap('ABC',True))

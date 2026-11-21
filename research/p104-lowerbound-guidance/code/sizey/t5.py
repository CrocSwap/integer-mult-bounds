import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter
Yk={'Y','Y2'}
nat=pk.native_from_word(W); ci=pk.caller_invoice(C)
def info(s):
    ks=set(kind(p) for _,p,_ in s['ins']+s['outs']); return ks
def kap(keep):
    Pn=Counter(nat['P']); removed=Counter()
    for r in range(n):
        if kind(r)!='H': continue
        st=stays[r]; p=[dim[s['f']] for s in st]
        q=[p[0]]
        for j in range(1,len(st)-1):
            if keep(st[j],r,j,st): q.append(p[j])
            else: removed[(p[j],)] +=1
        q.append(p[-1])
        for a,b in zip(p,p[1:]): Pn[b-a]-=1
        for a,b in zip(q,q[1:]):
            if b>a: Pn[b-a]+=1
    inv=pk.invoice(ci,dict(nat,P=+Pn)); return str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:12], sum(removed.values())
def isY(s): return bool(info(s)&Yk)
rules={
 'baseline':lambda s,*a:True,
 # consolidate Y deliveries to Y final chart (dim8), decoder unchanged: drop stops whose partners are Y-only, dim<8
 'V1 drop pure-Y stops dim1-7':lambda s,*a: not(info(s)<=Yk and info(s) and dim[s['f']]<8),
 'V1x drop pure-Y stops dim1-7 + pure-Y dim8 beyond first per helper':None,
 'V1y drop ALL Y-meeting stops dim<8 (even if other partners; optimistic)':lambda s,*a: not(isY(s) and dim[s['f']]<8),
 'V2 drop all Y stops dim 1-8 (couriers carry everything)':lambda s,*a: not(info(s)<=Yk and info(s)),
 'V3 V2 + drop owned-only/Y+O stops (decoder re-chosen)':lambda s,*a: not(info(s)<=Yk|{'O'} and info(s)),
 'V4 V3 + drop X-only(dim1 reads) too':lambda s,*a: not(info(s)<=Yk|{'O','X','X2'} and info(s)),
 'V5 drop every stop with no helper partner':lambda s,*a: 'H' in info(s),
}
for k,f in rules.items():
    if f is None: continue
    print(f'{k:70s}',*kap(f))
# V1x: keep only the first Y-final(dim8) stop pure-Y per helper
def kapx():
    Pn=Counter(nat['P']); rem=0
    for r in range(n):
        if kind(r)!='H': continue
        st=stays[r]; p=[dim[s['f']] for s in st]; q=[p[0]]; seen=False
        for j in range(1,len(st)-1):
            s=st[j]; ky=info(s)<=Yk and info(s)
            if ky and p[j]<8: rem+=1; continue
            if ky and p[j]==8:
                if seen: rem+=1; continue
                seen=True
            q.append(p[j])
        q.append(p[-1])
        for a,b in zip(p,p[1:]): Pn[b-a]-=1
        for a,b in zip(q,q[1:]):
            if b>a: Pn[b-a]+=1
    inv=pk.invoice(ci,dict(nat,Pn=0,P=+Pn)); return str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:12],rem
print('V1x',kapx())

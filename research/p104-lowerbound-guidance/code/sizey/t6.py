import sys; sys.path.insert(0,'../fewstops')
from load import *
exec(open('../fewstops/stays.py').read().split('from load import *')[1])
from collections import Counter
Yk={'Y','Y2'}
nat=pk.native_from_word(W); ci=pk.caller_invoice(C)
def info(s): return set(kind(p) for _,p,_ in s['ins']+s['outs'])
def run(drop, courier):
    Pn=Counter(nat['P']); Tn=Counter(nat['T']); ycharts=set()
    for r in range(n):
        if kind(r)!='H': continue
        st=stays[r]; p=[dim[s['f']] for s in st]; q=[p[0]]
        for j in range(1,len(st)-1):
            if drop(st[j]):
                ys=[x for _,x,_ in st[j]['ins']+st[j]['outs'] if kind(x) in Yk]
                for y in set(ys): ycharts.add((y,st[j]['f'],p[j]))
            else: q.append(p[j])
        q.append(p[-1])
        for a,b in zip(p,p[1:]): Pn[b-a]-=1
        for a,b in zip(q,q[1:]):
            if b>a: Pn[b-a]+=1
    if courier:
        for y,f,d in ycharts: Pn[d]+=1; Pn[8-d]+=1; Tn[8]+=1   # courier 0->d->8 (T adds one register's total climb 8)
    inv=pk.invoice(ci,dict(nat,P=+Pn,T=+Tn)); return str(pk.kappa(inv['T'],inv['P'],20)['lo'])[:12],len(ycharts)
for name,d in [('V1y drop Y-meeting stops <8',lambda s: bool(info(s)&Yk) and dim[s['f']]<8),
               ('V2 drop pure-Y stops all dims',lambda s: bool(info(s)) and info(s)<=Yk)]:
    print(name,'free couriers',run(d,False),' one courier [0,d,8] per (Y,chart) paid',run(d,True))

import sys, pickle, math; sys.path.insert(0,'../../PRICEKIT'); import pricekit as pk
from collections import Counter
W=pk.load('../../ATTACK/STACK7616/best7616.json.gz'); C=pk.load('../../MONOCALLER/7113_CALLER.json')
nat=pk.native_from_word(W); ci=pk.caller_invoice(C)
base=pk.price(pk.invoice(ci,nat),30); k0=base['kappa']['lo']; print(pk.cite('#7617',base))
dim=pickle.load(open('data.pkl','rb'))['dim']
def hops(ch): return Counter(dim[b]-dim[a] for a,b in zip(ch,ch[1:]))
def run(label,res,sel=lambda m,r:True):
    dP=Counter()
    for m,r in res.items():
        if not sel(m,r): continue
        dP.subtract(hops(r['path'])); dP.update(hops(r['chain']))
    n2=pk.native_param(nat,96,8,dP=dict(dP)); pr=pk.price(pk.invoice(ci,n2),30)
    print('%-40s S %d kappa %s x%.5f D0 %.2f'%(label,pr['S'],pk.kstr(pr['kappa'],14),float(pr['kappa']['lo']/k0),float(pr['D0'])))
b2=pickle.load(open('b2.pkl','rb'))
run('B2 all mains (co-location only)',b2)
for c in ('X','Y','X2','Y2'): run('B2 class '+c,b2,lambda m,r,c=c:r['cls']==c)
vw=pickle.load(open('var_w.pkl','rb')); res={m:dict(path=v[3],chain=v[2]) for m,v in vw.items()}; run('B3w windows-only',res)
vo=pickle.load(open('var_o.pkl','rb')); res={m:dict(path=v[3],chain=v[2]) for m,v in vo.items()}; run('B3o order-only',res)
ideal={m:dict(path=r['path'],chain=[r['path'][0],r['path'][-1]]) for m,r in b2.items()}; run('ideal one 8-hop',ideal)
# concentration of B2 gain
g=lambda r: r*math.log(r) if r>1 else 0
gains=sorted(((r['bound']-r['actual'],m,r['cls']) for m,r in b2.items()),reverse=True)
tot=sum(x[0] for x in gains); print('B2 gain/call %.1f'%tot)
for k in (10,25,50,100,200): print(' top',k,'%.1f'%sum(x[0] for x in gains[:k]))
print(gains[:8])

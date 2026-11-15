import sys,json,collections
sys.path.insert(0,'.'); sys.path.insert(0,'inputs/PRICEKIT')
from tails import *
import pricekit as pk
fin=W['final']
C='inputs/MONOCALLER/7113_CALLER.json'
nat=pk.native_from_word(W)
def kap(P):
    n2=dict(nat); n2['P']=+P; return pk.run(C,n2,digits=20)['price']['kappa']['lo']
K0=kap(collections.Counter(nat['P'])); print('base kappa',K0)
cj=json.load(open('inputs/ATTACK/PAIR/code/cands.json'))
byst={}
for cl in cj:
    for x in cj[cl]: byst[tuple(x['st'])]=x
byrc=collections.defaultdict(list)
for k in byst: byrc[(k[0],k[1])].append(k)
recs=[]
for fn in sys.argv[1:]:
    for l in open(fn):
        o=json.loads(l)
        if 'dirty' not in o: continue
        st=tuple(o['st'])
        if st not in byst:
            c=byrc.get((st[0],st[1]))
            if not c: continue
            st=c[0]
        if any(tuple(r['st'])==st for r in recs): continue
        o['key']=st; recs.append(o)
print('stays with census',len(recs))
def need(o):
    req=[]; bad=[]
    for d in o['dirty']:
        if d['kind']!='pub': bad.append('owned'); continue
        G=d['G']
        if G==127: continue
        Tm=arrive(d['r'],G)
        if d['ncols']>len(d['cols']): bad.append('trunc')
        for c in d['cols']:
            if fin[c]!=127:
                if fin[c]==G or ssub(G,fin[c]): req.append((c,G,'main-ok',0.0))
                else: bad.append('main-col')
            else:
                s,dc=opt(c,G,Tm); req.append((c,G,s,dc))
    return req,bad
cls=collections.Counter(); rows=[]
for o in recs:
    req,bad=need(o); o['req']=req; o['bad']=bad
    nm=sum(1 for d in o['dirty'] if d['kind']=='pub' and d['G']!=127)
    st=collections.Counter(s for _,_,s,_ in req)
    legal=all(s in('ok','ok-atG','main-ok') for _,_,s,_ in req)
    # chain consistency per helper (model A): required G set of each helper must be a chain
    gs=collections.defaultdict(set)
    for c,G,s,_ in req: gs[c].add(G)
    chain=all(all(sub(a,b) or sub(b,a) for a in v for b in v) for v in gs.values())
    o['legal']=legal and not bad and nm>0; o['chainA']=chain and not bad and nm>0
    cls[('nomain' if nm==0 else 'main', 'bad' if bad else '', 'B-legal' if o['legal'] else ('A-chain' if o['chainA'] else 'A-conflict'))]+=1
    rows.append((o['key'],round(byst[o['key']]['m'],2),nm,len(req),dict(st),bad[:2],o['legal'],o['chainA']))
for k,v in sorted(cls.items(),key=str): print(v,k)
json.dump([dict(key=o['key'],m=byst[o['key']]['m'],req=o['req'],bad=o['bad'],legal=o['legal'],chainA=o['chainA']) for o in recs],open('../need.json','w'))
# helper -> stays needing it, distribution
hn=collections.Counter(); hg=collections.defaultdict(set)
for o in recs:
    for c,G,s,_ in o['req']: hg[c].add(G)
print('distinct (helper) required',len(hg),'helpers needed at >=2 incomparable G:',sum(1 for v in hg.values() if not all(sub(a,b) or sub(b,a) for a in v for b in v)))
print('status totals',collections.Counter(s for o in recs for _,_,s,_ in o['req']))
print('per-stay #required pairs: quantiles',sorted(len(o['req']) for o in recs)[::max(1,len(recs)//10)])

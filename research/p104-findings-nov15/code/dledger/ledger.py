import sys, math, json
sys.path.insert(0,'inputs/PRICEKIT')
import pricekit as pk
from collections import Counter, defaultdict
f=lambda r: r*math.log(r)
CALLER='inputs/MONOCALLER/7113_CALLER.json'
WORDS={'7615':'inputs/ATTACK/COURIER226/hit_c226_1.json.gz',
       '7616':'inputs/ATTACK/WATCH/work/pr7616_word.json.gz'}
C=pk.load(CALLER); ports=pk.caller_ports(C); NST=C['stages']
def ledger(wpath):
    W=pk.load(wpath); nat=pk.native_from_word(W); ci=pk.caller_invoice(C)
    L=ci['nJ']; inv=pk.invoice(ci,nat); pr=pk.price(inv,30)
    B=defaultdict(lambda:[Counter(),Counter()])   # bucket -> [T,P] histograms (totals over all calls/ports)
    # caller T: fields
    for ty,t in C['types'].items():
        for dg in t['diagonal']:
            bits=dg[2:]; d=sum(bits); r=int(dg[0])%2+8*d
            idx=[k+1 for k,b in enumerate(bits) if b]
            if d==NST: name='C.T hub (deg17)'
            elif d==1: name='C.T single (deg1)'
            elif idx[0]==1 and d==8 or idx[-1]==NST and d==9 and idx[0]==9 or (idx[0]==1 and d==8): name='C.T arm top'
            elif idx[-1]==NST and idx[0]==9 and d==9: name='C.T arm top'
            else: name='C.T arm interior (deg2..7/8)'
            B[name+' %s'%ty][0][r]+=ports[ty]
    # caller P
    for e in C['events']:
        if e[0]=='J': continue
        ty,op=e[0],e[1]; k=ports[ty]
        if op=='QUERY': B['C.P thin QUERY '+ty][1][1]+=k
        elif op=='IDLE_ONE': B['C.P idle line '+ty][1][8*len(e[3])]+=k
        elif op=='IDLE_ODD': B['C.P idle line (ODD) '+ty][1][8*len(e[3])+1]+=k
    # J/host ops: ADD/SWAP/SCALE/HOST/LAMBDA unpriced
    n=len(W['initial']); live=set(W['live']); H=W.get('hosted') or {}
    X2,Y2=set(H.get('X2',[])),set(H.get('Y2',[]))
    cls={}
    for r in live: cls[r]='X'; cls[r+112]='Y'
    for r in X2: cls[r]='X2'
    for r in Y2: cls[r]='Y2'
    dim=[len(b) for b in W['frames']]
    for e in W['program']:
        if e[0]=='MOVE':
            rk=abs(dim[e[3]]-dim[e[2]]); r=e[1]
            if r in cls: nm='N.P main '+cls[r]
            elif r>=n: nm='N.P owned reg'
            else: nm='N.P helper MOVE'
            B[nm][1][rk]+=L
    main=live|{r+112 for r in live}|X2|Y2
    for r in range(n):
        if r in main: continue
        d0,d1=dim[W['initial'][r]],dim[W['final'][r]]
        B['N.T helper birth-dim %d'%d0][0][d1-d0]+=L
    return pr,B,L,inv
def Dof(T,P): return sum(v*f(r) for r,v in T.items())-sum(v*f(r) for r,v in P.items())
def Sof(T,P): return sum(r*v for r,v in T.items())-sum(r*v for r,v in P.items())
out={}
for lab,wp in WORDS.items():
    pr,B,L,inv=ledger(wp)
    Tt=Counter(); Pt=Counter()
    for T,P in B.values(): Tt.update(T); Pt.update(P)
    exact = (+Tt==+inv['T']) and (+Pt==+inv['P'])
    rows=sorted(((Dof(T,P),Sof(T,P),b,sum(T.values()),sum(P.values())) for b,(T,P) in B.items()),reverse=True)
    out[lab]=dict(kappa=pk.kstr(pr['kappa'],14),S=int(pr['S']),D0=float(pr['D0']),exact_hist=exact,sumD=sum(r[0] for r in rows),L=L,
        rows=[dict(D=r[0],S=r[1],b=r[2],nT=r[3],nP=r[4]) for r in rows],
        detail={b:dict(T=dict(sorted(T.items())),P=dict(sorted(P.items()))) for b,(T,P) in B.items()})
    print(lab,out[lab]['kappa'],out[lab]['S'],out[lab]['D0'],'hist-exact',exact,'sumD',out[lab]['sumD'],'L',L)
json.dump(out,open('ledger.json','w'),default=str)
a,b=out['7615'],out['7616']; bb={r['b']:r['D'] for r in b['rows']}
print('%-40s %12s %12s %10s'%('bucket','D0/call 7615','D0 7616','delta'))
for r in a['rows']:
    print('%-40s %12.2f %12.2f %10.2f'%(r['b'],r['D']/17,bb.get(r['b'],0)/17,(bb.get(r['b'],0)-r['D'])/17))

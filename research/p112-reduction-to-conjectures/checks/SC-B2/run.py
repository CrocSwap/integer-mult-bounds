import csv,ast,sys,time,itertools,json
from cov3 import *
rs=list(csv.DictReader(open('residue.csv')))
def _sl(r):
    ws=sorted(ast.literal_eval(r['weights']),reverse=True);d=int(r['d']);return sum(g[w] for w in ws[d-2:])
rs.sort(key=_sl)
rs=rs[0::2]
JS=[int(x) for x in sys.argv[1].split(',')]
par_cache={}
memo={}
def parab(I):
    if I not in par_cache: par_cache[I]=frozenset(parabolic(I))
    return par_cache[I]
out=open(sys.argv[2],'a')
for r in rs:
    ws=sorted(ast.literal_eval(r['weights']),reverse=True); d=int(r['d']); s=int(r['s'])
    for j in JS:
        comp=ws[d-j:]; cap=sum(g[w] for w in comp); rank=8-j
        t0=time.time(); alive=[]; 
        for I in itertools.combinations(range(8),rank):
            P_=parab(I); T=[t for t in range(n) if t not in P_]
            if len(T)>cap: continue
            key=(len(P_),tuple(comp))
            if key not in memo: memo[key]=cover_set3(T,comp)
            if memo[key] is not False: alive.append((I,memo[key]))
        res=dict(d=d,s=s,ws=ws,j=j,cap=cap,alive=len(alive),timeouts=sum(1 for a in alive if a[1] is None),t=round(time.time()-t0,1))
        print(json.dumps(res),flush=True); out.write(json.dumps(res)+"\n"); out.flush()
        if not alive: break

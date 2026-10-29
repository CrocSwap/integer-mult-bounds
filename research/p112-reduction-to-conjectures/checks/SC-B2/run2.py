import csv,ast,sys,time,itertools,json
from cov4 import *
gens=load_gens('grp.out')
E6=(0,1,2,3,4,5)
done={}
for f in ('fwd.jsonl','rev.jsonl'):
    for l in open(f):
        r=json.loads(l); done[(r['d'],tuple(r['ws']))]=r
rs=list(csv.DictReader(open('residue.csv')))
memo={}
out=open('hard.jsonl','a')
for r in rs:
    ws=sorted(ast.literal_eval(r['weights']),reverse=True); d=int(r['d']); s=int(r['s'])
    if (d,tuple(ws)) in done: continue
    j=2; comp=ws[d-j:]; cap=sum(g[w] for w in comp)
    t0=time.time(); alive=[]
    for I in itertools.combinations(range(8),8-j):
        P_=parabolic(I); T=[t for t in range(n) if t not in set(P_)]
        if len(T)>cap: continue
        key=(I if I==E6 else len(P_),tuple(comp))
        if key not in memo:
            memo[key]=cover_set4(T,comp,gens,verbose=True) if I==E6 else cover_set3(T,comp)
        if memo[key] is not False: alive.append((I,memo[key]))
    res=dict(d=d,s=s,ws=ws,j=j,cap=cap,alive=len(alive),timeouts=sum(1 for a in alive if a[1] is None),t=round(time.time()-t0,1))
    print(json.dumps(res),flush=True); out.write(json.dumps(res)+"\n"); out.flush()

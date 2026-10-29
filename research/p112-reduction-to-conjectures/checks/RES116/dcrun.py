# unique-comp Dim-Cover runner. usage: dcrun.py out.jsonl comp1 comp2 ...   (comp like 6,6,5,5,5,4)
import sys,os,json,time,itertools
sys.path.insert(0,'../SC-B2'); os.chdir('../SC-B2')
from cov4 import *
gens=load_gens('grp.out')
PAR={}
def parab(I):
    if I not in PAR: PAR[I]=frozenset(parabolic(I))
    return PAR[I]
E6=(0,1,2,3,4,5)
out=open(sys.argv[1],'a')
for a in sys.argv[2:]:
    comp=sorted(map(int,a.split(',')),reverse=True); cap=sum(g[w] for w in comp)
    res=[]
    for I in itertools.combinations(range(8),6):
        P_=parab(I); T=[t for t in range(n) if t not in P_]
        if len(T)>cap: continue
        t0=time.time()
        if not any(w>=5 for w in comp): r='nobig'
        elif I==E6: r=cover_set4(T,comp,gens,tmo=1100)
        else: r=cover_set3(T,comp)
        res.append((list(I),len(T),r,round(time.time()-t0,1)))
        if r is not False: break   # alive/unknown -> not killed
    killed=all(x[2] is False for x in res)
    out.write(json.dumps(dict(comp=comp,cap=cap,res=res,killed=killed))+"\n"); out.flush()

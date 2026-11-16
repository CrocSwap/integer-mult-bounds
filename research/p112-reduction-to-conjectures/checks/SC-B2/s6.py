import csv,ast,sys,time,itertools,json
from cov4 import *
gens=load_gens('grp.out'); E6=(0,1,2,3,4,5)
rs=[r for r in csv.DictReader(open('residue.csv')) if r['s']=='6']
memo={}
def dead(comp,tag=''):
    comp=tuple(sorted(comp,reverse=True)); cap=sum(g[w] for w in comp)
    alive=[]
    for I in itertools.combinations(range(8),6):
        P_=parabolic(I); T=[t for t in range(n) if t not in set(P_)]
        if len(T)>cap: continue
        key=(I if I==E6 else len(P_),comp)
        if key not in memo:
            memo[key]=cover_set4(T,comp,gens) if I==E6 else cover_set3(T,comp)
        if memo[key] is not False: alive.append(I)
    plane=False
    if alive==[E6]:
        capc=sum(g[w] for w in comp)
        M=[w for w in comp if capc-g[w]<=82]
        pairs_ok=all(capc-g[a]-g[b]<57 for a,b in itertools.combinations(M,2)) if len(M)>=4 else False
        plane = len(M)>=4 and pairs_ok
    res=(not alive) or plane
    print(tag,comp,'dead(cover)' if not alive else ('dead(plane)' if plane else 'ALIVE/unknown %s'%alive),flush=True)
    return res
for r in rs:
    ws=sorted(ast.literal_eval(r['weights']),reverse=True); d=int(r['d'])
    comp=ws[d-2:]; kmin=ws[d-3]
    print('ROW',ws,flush=True)
    out={}
    out['V1(+line)']=dead(comp+[1],'V1')
    for x in sorted(set(comp)):
        up=list(comp); up.remove(x); up.append(x+1)
        sw=list(comp); sw.remove(x); sw.append(kmin)
        if x==kmin:
            out['x%d'%x]=dead(comp,'base(x=kmin)')
        else:
            out['x%d'%x]=dead(up,'A%d'%x) or dead(sw,'B%d'%x)
    print(json.dumps(out),flush=True)

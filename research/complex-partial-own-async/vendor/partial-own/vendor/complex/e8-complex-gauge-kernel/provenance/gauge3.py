"""per-target nested + per-centre chain gauge assignment (greedy / SA-lite)"""
from gauge import *
import random,pickle
def setup_g(w):
    col,first,cap,cands,P=prep(w);R=len(col)
    served={}
    for i,r in enumerate(w['centers']):
        served[i]=sorted({e[1]-v for e in w['cut'] if e[2]==r})
    cf=[span(f) for f in w['center_frames']]
    tcent=defaultdict(list)
    for i,ts in served.items():
        for t in ts:tcent[t].append(i)
    return col,first,cap,cands,P,served,cf,tcent
def greedy_g(col,cands,served,cf,tcent,order,minrank=1):
    R=len(col)
    L={t:frozenset({0}) for t in range(v)}   # span sets of current level
    Lall={t:[] for t in range(v)}
    Lb={t:() for t in range(v)}
    E_of={};eps=0
    for h in order:
        for E in cands[h]:
            sE=span(E)
            ok=True;newL={}
            for t in col[h]:
                cur=L[t]
                if not all(sE<=c or c<=sE for c in Lall[t]):ok=False;break
                newL[t]=sE if len(sE)>len(cur) else cur
            if not ok:continue
            # centre chains + containment in cf
            cs={i for t in newL for i in tcent[t]}
            for i in cs:
                levels=[newL.get(u,L[u]) for u in served[i]]
                top=max(levels,key=len)
                if not all(a<=b or b<=a for a in set(levels) for b in set(levels)):ok=False;break
                if not top<=cf[i]:ok=False;break
            if not ok:continue
            E_of[h]=E;eps+=len(E)
            for t,s in newL.items():
                L[t]=s;Lb[t]=E if len(s)>len(span(Lb[t])) else Lb[t]
            for t in col[h]:Lall[t].append(sE)
            break
    return E_of,eps
if __name__=='__main__':
    w=load();w['R']=w['report']['R']
    col,first,cap,cands,P,served,cf,tcent=setup_g(w);R=len(col)
    print('centres served sizes',[len(served[i]) for i in served])
    best=(0,None)
    for seed in range(300):
        rnd=random.Random(seed);order=list(range(R));rnd.shuffle(order)
        if seed%3==0:order.sort(key=lambda h:len(col[h]))
        E_of,eps=greedy_g(col,cands,served,cf,tcent,order)
        if eps>best[0]:best=(eps,E_of);print(seed,eps,len(E_of),Counter(len(E) for E in E_of.values()),flush=True)
    pickle.dump(best,open('gauge3_best.pkl','wb'))

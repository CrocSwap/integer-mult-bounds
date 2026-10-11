from gauge3 import *
import time
def state_from(E_of,col,tcent,served,cf):
    pass
def refill(col,cands,served,cf,tcent,E_of,drop,rnd):
    keep={h:E for h,E in E_of.items() if h not in drop}
    R=len(col)
    # rebuild L from keep
    L={t:frozenset({0}) for t in range(v)}
    Lall={t:[] for t in range(v)}
    for h,E in keep.items():
        sE=span(E)
        for t in col[h]:
            Lall[t].append(sE)
            if len(sE)>len(L[t]):L[t]=sE
    cur=dict(keep);eps=sum(len(E) for E in keep.values())
    order=[h for h in range(R) if h not in keep];rnd.shuffle(order)
    for h in order:
        for E in cands[h]:
            sE=span(E);ok=True;newL={}
            for t in col[h]:
                c=L[t]
                if not all(sE<=x or x<=sE for x in Lall[t]):ok=False;break
                newL[t]=sE if len(sE)>len(c) else c
            if not ok:continue
            cs={i for t in newL for i in tcent[t]}
            for i in cs:
                levels=[newL.get(u,L[u]) for u in served[i]]
                top=max(levels,key=len)
                if not all(a<=b or b<=a for a in set(levels) for b in set(levels)) or not top<=cf[i]:ok=False;break
            if not ok:continue
            cur[h]=E;eps+=len(E)
            for t,s in newL.items():L[t]=s
            for t in col[h]:Lall[t].append(sE)
            break
    return cur,eps
if __name__=='__main__':
    import sys
    seed=int(sys.argv[1]);iters=int(sys.argv[2])
    w=load();w['R']=w['report']['R']
    col,first,cap,cands,P,served,cf,tcent=setup_g(w);R=len(col)
    eps0,E_of=pickle.load(open('gauge3_best.pkl','rb'))
    rnd=random.Random(seed);best=(eps0,E_of);t0=time.time()
    cands_h=[h for h in range(R) if cands[h]]
    for it in range(iters):
        cur=best[1]
        drop=set(rnd.sample(list(cur),max(1,int(len(cur)*rnd.choice([0.05,0.1,0.2,0.4])))))
        n,e=refill(col,cands,served,cf,tcent,cur,drop,rnd)
        if e>=best[0]:
            if e>best[0]:print(it,e,len(n),Counter(len(E) for E in n.values()),round(time.time()-t0),flush=True)
            best=(e,n)
    pickle.dump(best,open('gauge4_best_%d.pkl'%seed,'wb'))
    print('final',best[0])

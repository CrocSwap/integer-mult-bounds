from e8net import *
import random,sys,pickle
def rand_sub_with(v,d,rng):
    c=[v]
    while len(span(c))<d: c=span(c+[rng.randrange(1,512)])
    return span(c)
def inA(A,t): return inspan(A,L[t])
def build(n,mode,dims,seed,delta_rows=0,hubs_contain_v=True):
    W,U,vs=WU(n); N=Net(n); rng=random.Random(seed)
    As=[]
    for h in range(8):
        v=vs[h]; d=dims[h]
        A=rand_sub_with(v,d,rng) if hubs_contain_v else span([rng.randrange(1,512) for _ in range(d)]) 
        As.append(A)
    gat={}
    pending=[]
    for h in range(8):
        A=As[h]; v=vs[h]
        sup=[t for t in range(n) if U[t,h]%P]
        inn=[t for t in sup if inA(A,t)]; out=[t for t in sup if not inA(A,t)]
        rel={}
        if mode=='B':                      # single-port shared gatherers
            for t in out:
                if t not in gat: gat[t]=N.add([L[t]],[],{t:1},{})
                rel[gat[t]]=int(U[t,h])
        elif mode=='C':                    # coset groups of A in F2^9
            groups={}
            for t in out:
                key=min(L[t]^a for a in [0]+[x for x in itertools.chain.from_iterable([[]])]) 
                # canonical coset rep: reduce L[t] by basis of A
                x=L[t]
                for b in A: x=min(x,x^b)
                groups.setdefault(x,[]).append(t)
            for x,ts in groups.items():
                aB=labspan(ts); bB=[y for y in span(aB) if inspan(A,y)]
                bB=span([y for y in span([*aB]) if inspan(A,y)] + [])  # may be partial basis; recompute properly below
                # proper intersection: vectors of span(aB) lying in A
                allv=[0]
                for b in aB: allv+= [w^b for w in allv]
                inter=span([w for w in allv if w and inspan(A,w)])
                g=N.add(aB,inter,{t:int(U[t,h]) for t in ts},{})
                rel[g]=1
        pending.append((h,A,inn,rel))
    for h,A,inn,rel in pending:
        v=vs[h]; Fh={t:int(U[t,h]) for t in inn}
        Gh={s:int(W[s,h])%P for s in range(n) if W[s,h]}
        bB=[v] if inspan(A,v) else []
        # hub chart must contain relays' b
        aB=list(A)
        N.add(aB,bB,Fh,Gh,rel)
    return N
if __name__=='__main__':
    n=int(sys.argv[1]); mode=sys.argv[2]; trials=int(sys.argv[3])
    rng=random.Random(7); res=[]
    for it in range(trials):
        dims=[rng.choice([2,3,4,5,6,7,8,8,8]) for _ in range(8)]
        N=build(n,mode,dims,it)
        bad=N.legal()
        if bad: print('ILLEGAL',dims,bad[:2]); continue
        ok,Mm=N.check()
        if not ok: print('NOT DECODER',dims); continue
        r=N.report('%s%s'%(mode,dims)); res.append(r)
        print(mode,dims,{k:r[k] for k in('D','YC','DX','loss','junk','viol')},flush=True)
    print('SUMMARY n',n,mode,'trials',len(res),'min D',min(r['D'] for r in res),'violations',sum(r['viol'] for r in res),'min DX',min(r['DX'] for r in res),'min YC',min(r['YC'] for r in res))

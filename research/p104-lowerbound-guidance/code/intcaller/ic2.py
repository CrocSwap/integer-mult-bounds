"""INTCALLER ic2: exact soundness of every ic1 row (incl. TURAN) on built frames C1, c33 (pieces known; unlisted singletons = mains,
listed singletons = idle) and c12, c22 (json; degree-1 pads dropped; main/idle split unknown -> exists-check over all main counts)."""
import sys,io,contextlib,itertools
sys.path.insert(0,'code/callercut')
with contextlib.redirect_stdout(io.StringIO()):import cc0
import ic1
def frame_types(R):
    out=[]
    for M,P in R:
        listed=set().union(*P) if P else set()
        mains=len(M-listed);pieces=tuple(sorted([len(p) for p in P]+[1]*mains,reverse=True))
        out.append((len(M),pieces,mains))
    return out
def check(name,k,tl,fixed=True):
    T=sorted(set((D,P) for D,P,m in tl));idx={t:i for i,t in enumerate(T)}
    xs={};
    for D,P,m in tl:xs[idx[(D,P)]]=xs.get(idx[(D,P)],0)+1
    if fixed:
        ys={}
        for D,P,m in tl:
            i=idx[(D,P)]
            if any(L==1 for L in P):ys[i]=ys.get(i,0)+m
        cands=[ys]
    else:
        rng=[range(0,xs[i]*sum(1 for L in T[i][1] if L==1)+1) if any(L==1 for L in T[i][1]) else [None] for i in range(len(T))]
        cands=[{i:v for i,v in enumerate(c) if v is not None} for c in itertools.product(*rng)]
    best=None
    for ys in cands:
        bad,ms=ic1.verify(k,T,xs,ys,True)
        if best is None or len(bad)<len(best[0]):best=(bad,ms,ys)
    bad,ms,ys=best
    print('%-6s k=%d n=%d (2k-2=%d) types %s mains %s  -> %s  minslack %s'%(name,k,len(tl),2*k-2,[(D,P) for D,P,m in tl],sum(ys.values()),
          'ALL ROWS OK' if not bad else bad, min((v,n) for n,v in ms.items() if n not in('n','MAINS'))))
check('C1',3,frame_types(cc0.C1));check('c33',6,frame_types(cc0.C33))
for nm in ['c12_tm1o2','c22_tm1o2']:
    k,R=cc0.fromjson(cc0.BASE+'UNIMODEL/arm1/caller_%s.json'%nm)
    check(nm,k,[(len(M),tuple([1]*len(M)),0) for M,P in R],fixed=False)

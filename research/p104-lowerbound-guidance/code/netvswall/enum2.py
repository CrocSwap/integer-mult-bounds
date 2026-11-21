# faster exhaustive: all P subsets (odd labels) at h, m nodes, D<=n-1 (or Dmax), all legal-edge DAG orders, Singular GB.
import itertools, sys, time
from netcheck import *
h=int(sys.argv[1]); m=int(sys.argv[2]); nmin=int(sys.argv[3]); nmax=int(sys.argv[4]); part=int(sys.argv[5]); nparts=int(sys.argv[6])
odd=[x for x in range(1,1<<h) if bin(x).count('1')&1]
subs=subspaces(h)
NODES=[(a,b) for a in subs for b in subs if b<=a]
dd=[dimof(a)-dimof(b) for a,b in NODES]
def canon_sets():
    # P up to coordinate permutation
    seen=set(); out=[]
    for r in range(nmin,nmax+1):
        for P in itertools.combinations(odd,r):
            best=min(tuple(sorted(sum(((x>>i)&1)<<pi[i] for i in range(h)) for x in P)) for pi in itertools.permutations(range(h)))
            if best not in seen: seen.add(best); out.append(P)
    return out
Ps=canon_sets()
print('P sets',len(Ps),flush=True)
for pi_,P in enumerate(Ps):
    if pi_%nparts!=part: continue
    labs=list(P); n=len(labs); Dmax=n-1
    Q=[[dot(s,t) for t in labs] for s in labs]
    # precompute node masks
    idxs=[i for i in range(len(NODES)) if dd[i]<=Dmax]
    Am={i:sum(1<<j for j,q in enumerate(labs) if q in NODES[i][0]) for i in idxs}
    Bm={i:sum(1<<j for j,q in enumerate(labs) if all(dot(q,y)==0 for y in NODES[i][1])) for i in idxs}
    # drop nodes with no gather and no deposit AND d>=1? keep all (pure relays)
    cnt={}; t0=time.time(); ncalls=0
    for ids in itertools.combinations_with_replacement(idxs,m):
        D=sum(dd[i] for i in ids)
        if D>Dmax: continue
        # quick: union of A masks must include all; union of B
        if (Am[ids[0]]|(Am[ids[-1]] if m>1 else 0))==0 and m==1: continue
        ua=0;ub=0
        for i in ids: ua|=Am[i]; ub|=Bm[i]
        full=(1<<n)-1
        if ua!=full or ub!=full: cnt['cover']=cnt.get('cover',0)+1; continue
        seen=set()
        for order in itertools.permutations(range(m)):
            nodes=[NODES[ids[o]] for o in order]
            edges=tuple((j,k) for j in range(m) for k in range(j+1,m) if nodes[j][1]<=nodes[k][0])
            if not edges: continue
            key=(tuple(nodes),edges)
            if key in seen: continue
            seen.add(key)
            r=net_eqs(labs,nodes,list(range(m)),list(edges),Q)
            if r is None: cnt['nodiag']=cnt.get('nodiag',0)+1; continue
            ncalls+=1; res=run_sing(*r,timeout=120)
            cnt[res]=cnt.get(res,0)+1
            if res!='INFEASIBLE':
                print('HIT',res,'h',h,'P',labs,'D',D,[(sorted(a),sorted(b)) for a,b in nodes],edges,flush=True)
    print('DONE h',h,'P',labs,'m',m,'Dmax',Dmax,cnt,'calls',ncalls,'t',round(time.time()-t0,1),flush=True)

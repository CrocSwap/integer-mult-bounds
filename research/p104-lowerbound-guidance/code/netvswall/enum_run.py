import itertools, sys, time
from netcheck import *
h=int(sys.argv[1]); labs=[int(x) for x in sys.argv[2].split(',')]; m=int(sys.argv[3]); Dmax=int(sys.argv[4])
part=int(sys.argv[5]); nparts=int(sys.argv[6])
n=len(labs); Q=[[dot(s,t) for t in labs] for s in labs]
subs=subspaces(h)
N=[(a,b) for a in subs for b in subs if b<=a and dimof(a)-dimof(b)<=Dmax]
dd=[dimof(a)-dimof(b) for a,b in N]
cnt={}; t0=time.time(); idx=0; ncalls=0
for ids in itertools.combinations_with_replacement(range(len(N)),m):
    D=sum(dd[i] for i in ids)
    if D>Dmax: continue
    idx+=1
    if idx%nparts!=part: continue
    seen=set()
    for order in itertools.permutations(range(m)):
        nodes=[N[ids[o]] for o in order]
        edges=tuple((j,k) for j in range(m) for k in range(j+1,m) if nodes[j][1]<=nodes[k][0])
        if not edges: continue
        key=(tuple(nodes),edges)
        if key in seen: continue
        seen.add(key)
        r=net_eqs(labs,nodes,list(range(m)),list(edges),Q)
        if r is None: cnt['nodiag']=cnt.get('nodiag',0)+1; continue
        ncalls+=1
        res=run_sing(*r)
        cnt[res]=cnt.get(res,0)+1
        if res!='INFEASIBLE':
            print('HIT',res,'D',D,[(sorted(a),sorted(b)) for a,b in nodes],edges,flush=True)
print('DONE h',h,labs,'m',m,'Dmax',Dmax,'counts',cnt,'calls',ncalls,'time',time.time()-t0,flush=True)

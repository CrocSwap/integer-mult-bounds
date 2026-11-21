import itertools, sys, time
from nv import *
h=int(sys.argv[1]); nmin=int(sys.argv[2]); nmax=int(sys.argv[3])
odd=[x for x in range(1,1<<h) if bin(x).count('1')&1]
seen=set()
for r in range(nmin,nmax+1):
    for P in itertools.combinations(odd,r):
        best=min(tuple(sorted(sum(((x>>i)&1)<<pi[i] for i in range(h)) for x in P)) for pi in itertools.permutations(range(h)))
        if best in seen: continue
        seen.add(best); t=time.time()
        res=min_mass(h,list(P),timeout=60)
        print('h',h,'P',P,'n',r,'m<n search:',res,'t',round(time.time()-t,1),flush=True)

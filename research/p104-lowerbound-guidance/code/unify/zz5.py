# UNIFY: targeted ZIGZAG instances in the first uncovered regime (h=5, dim B=2, e=1, xf=xb=2, D=4, budget D+e=5).
import sys, random, time
sys.path.insert(0,'../netattr')
from common import *
from netgen import rand_net, net_M
from exact import min_mass
seed=int(sys.argv[1]); TR=int(sys.argv[2]); dens=float(sys.argv[3]); random.seed(seed)
h=5; labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
Qm=[[dot(s,t) for t in labs] for s in labs]
done=0
while done<TR:
    v=[random.randrange(1,32) for _ in range(6)]
    B=span(v[:2]); A=span(v[:4]); A2=span(v[:2]+[v[4]]); B2=span([v[5]])
    if dimof(B)!=2 or dimof(A)!=4 or dimof(A2)!=3 or dimof(B2)!=1 or not B2<=A2 or (B&B2)!=frozenset({0}): continue
    xf=dimof(A)-dimof(A&A2); xb=dimof(span(list(B)+list(B2)))-dimof(B2)
    if xf<2 or xb<2: continue
    F,G,H=rand_net(h,labs,[(A,B),(A2,B2)],[(0,1)],dens=dens,vals=(1,))
    M,_=net_M(G,H,F); T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    if sum(1 for t in range(n) for p in range(n) if t!=p and T[t][p])<4: continue
    t0=time.time(); st,c,R,res=min_mass(h,labs,T,Qm,5,timeout=120,diagfree=True)
    done+=1
    print(done,'D=4 e=1 xf',xf,'xb',xb,'status@budget5',st,'covers tried',len(res),'%.0fs'%(time.time()-t0),
          '' if st=='FEASIBLE' else 'INSTANCE '+str(dict(A=sorted(A),B=sorted(B),A2=sorted(A2),B2=sorted(B2),F=F,G=G)),flush=True)

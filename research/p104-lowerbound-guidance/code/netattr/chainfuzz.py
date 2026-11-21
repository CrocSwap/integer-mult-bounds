# 2-node chains j->k (both gather, both deposit) with relay ascent e = dim a_k - dim b_j; exact min mass vs D.
import sys, random, time
from common import *
from netgen import *
from exact import min_mass
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3])
random.seed(seed)
labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
Qm=[[dot(s,t) for t in labs] for s in labs]
stats={'feas':0,'none':0,'und':0,'skip':0}
for tr in range(TR):
    daj=random.randint(2,h); aj=rand_sub(h,daj)
    dbj=random.randint(0,daj-1); bj=rand_sub(h,dbj,aj)
    # a_k contains b_j, with ascent e>=0
    e=random.randint(0,min(2,h-dbj)); ak=span(list(bj)+[random.randrange(1<<h) for _ in range(e)])
    dak=dimof(ak); dbk=random.randint(0,dak-1); bk=rand_sub(h,dbk,ak)
    nodes=[(aj,bj),(ak,bk)]; D=(daj-dbj)+(dak-dbk)
    F,G,H=rand_net(h,labs,nodes,[(0,1)])
    M,_=net_M(G,H,F)
    T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    if all(x==0 for r in T for x in r): stats['skip']+=1; continue
    t0=time.time()
    st,c,R,res=min_mass(h,labs,T,Qm,D,timeout=60)
    key={'FEASIBLE':'feas','NONE':'none','UNDECIDED':'und'}[st]; stats[key]+=1
    print(tr,'d',(daj-dbj,dak-dbk),'e',dimof(ak)-dbj,'D',D,st,[R[i][2] for i in c] if c else '', 'covers tried',len(res),'%.1fs'%(time.time()-t0),flush=True)
    if st!='FEASIBLE':
        print('  INSTANCE',dict(aj=sorted(aj),bj=sorted(bj),ak=sorted(ak),bk=sorted(bk),F=F,G=G,H=H),flush=True)
print('STATS',stats)

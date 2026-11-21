# structured chains j->k with forward excess xf=dim A - dim(A^A')>0, backward excess xb=dim(B+B')-dim B'>0; exact min mass
import sys, random, time
from common import *
from netgen import *
from exact import min_mass
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3])
random.seed(seed)
labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
Qm=[[dot(s,t) for t in labs] for s in labs]
def desc(S): return 'dim%d'%dimof(S)
done=0
while done<TR:
    A=rand_sub(h,random.randint(2,h)); B=rand_sub(h,random.randint(0,dimof(A)-1),A)
    A2=span(list(B)+[random.randrange(1<<h) for _ in range(random.randint(1,3))]); 
    if dimof(A2)==0: continue
    B2=rand_sub(h,random.randint(0,dimof(A2)-1),A2)
    AA=A&A2; BB=span(list(B)+list(B2)) 
    xf=dimof(A)-dimof(AA); xb=dimof(BB)-dimof(B2); e=dimof(A2)-dimof(B)
    if xf==0 or xb==0: continue
    nodes=[(A,B),(A2,B2)]; D=dimof(A)-dimof(B)+dimof(A2)-dimof(B2)
    if D>6: continue
    F,G,H=rand_net(h,labs,nodes,[(0,1)],dens=.85)
    M,_=net_M(G,H,F)
    T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    t0=time.time(); st,c,R,res=min_mass(h,labs,T,Qm,D,timeout=30)
    done+=1
    rows=[]
    if c:
        for i in c:
            Dl,Sl,pr=R[i]; U=span([labs[t] for t in Dl]); V=span([labs[p] for p in Sl])
            rows.append('pr%d U%d V%d [U<=Bp^:%d U<=B2p^:%d V<=A:%d V<=A2:%d]'%(pr,dimof(U),dimof(V),
               int(all(dot(u,b)==0 for u in U for b in B)),int(all(dot(u,b)==0 for u in U for b in B2)),int(V<=A),int(V<=A2)))
    print('dims A,B,A2,B2',dimof(A),dimof(B),dimof(A2),dimof(B2),'d',(dimof(A)-dimof(B),dimof(A2)-dimof(B2)),'xf',xf,'xb',xb,'e',e,'D',D,st,rows,'covers',len(res),'%.1fs'%(time.time()-t0),flush=True)
    if st!="FEASIBLE": print("  INSTANCE",dict(A=sorted(A),B=sorted(B),A2=sorted(A2),B2=sorted(B2),F=F,G=G,H=H),flush=True)

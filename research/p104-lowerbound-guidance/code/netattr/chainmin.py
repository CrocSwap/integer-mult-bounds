# search chains with xf,xb,e>=1 and D<=Dmax for counterexamples (min mass > D); own code
import sys, random, time
from common import *
from netgen import *
from exact import min_mass
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3]); Dmax=int(sys.argv[4]); dens=float(sys.argv[5]); DF=len(sys.argv)>6 and sys.argv[6]=='diagfree'
random.seed(seed)
labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
Qm=[[dot(s,t) for t in labs] for s in labs]
cnt={}
done=0; tries=0
while done<TR and tries<10**6:
    tries+=1
    A=rand_sub(h,random.randint(1,h)); B=rand_sub(h,random.randint(0,dimof(A)-1),A)
    A2=span(list(B)+[random.randrange(1<<h) for _ in range(random.randint(1,3))])
    if dimof(A2)==dimof(B): continue
    B2=rand_sub(h,random.randint(0,dimof(A2)-1),A2)
    xf=dimof(A)-dimof(A&A2); xb=dimof(span(list(B)+list(B2)))-dimof(B2)
    D=dimof(A)-dimof(B)+dimof(A2)-dimof(B2)
    if xf==0 or xb==0 or D>Dmax: continue
    F,G,H=rand_net(h,labs,[(A,B),(A2,B2)],[(0,1)],dens=dens)
    M,_=net_M(G,H,F)
    T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    if all(T[t][p]==0 for t in range(n) for p in range(n) if not (DF and t==p)): continue
    st,c,R,res=min_mass(h,labs,T,Qm,D,timeout=30,diagfree=DF)
    done+=1; key=(D,st); cnt[key]=cnt.get(key,0)+1
    if st!='FEASIBLE':
        print('D',D,st,'dims',dimof(A),dimof(B),dimof(A2),dimof(B2),'e',dimof(A2)-dimof(B),'INSTANCE',dict(A=sorted(A),B=sorted(B),A2=sorted(A2),B2=sorted(B2),F=F,G=G,H=H),flush=True)
print('h',h,'counts',cnt)

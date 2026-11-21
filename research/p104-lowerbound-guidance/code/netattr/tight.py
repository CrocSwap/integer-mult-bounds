# [C] tight-relay networks (every relay j->k has a_k = b_j); all nodes may gather and deposit (non-bowtie). exact min mass vs D.
import sys, random, time
from common import *
from netgen import *
from exact import min_mass
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3]); DF=len(sys.argv)>4
random.seed(seed)
labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
Qm=[[dot(s,t) for t in labs] for s in labs]; cnt={}
done=0
while done<TR:
    m=random.randint(2,3); a0=rand_sub(h,random.randint(2,h)); nodes=[(a0,rand_sub(h,random.randint(0,dimof(a0)-1),a0))]; edges=[]
    for k in range(1,m):
        j=random.randrange(k); a=nodes[j][1]
        if dimof(a)==0: break
        nodes.append((a,rand_sub(h,random.randint(0,dimof(a)-1),a))); edges.append((j,k))
    if len(nodes)<2: continue
    D=sum(dimof(a)-dimof(b) for a,b in nodes)
    if D>5: continue
    F,G,H=rand_net(h,labs,nodes,edges,dens=.8)
    M,_=net_M(G,H,F); T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    if all(T[t][p]==0 for t in range(n) for p in range(n) if not(DF and t==p)): continue
    st,c,R,res=min_mass(h,labs,T,Qm,D,timeout=30,diagfree=DF); done+=1
    cnt[st]=cnt.get(st,0)+1
    if st!='FEASIBLE': print(st,'D',D,dict(nodes=[(sorted(a),sorted(b)) for a,b in nodes],edges=edges,F=F,G=G,H=H),flush=True)
print('tight h',h,cnt)

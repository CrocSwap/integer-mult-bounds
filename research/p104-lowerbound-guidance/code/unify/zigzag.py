# UNIFY: exact test of ZIGZAG  m(pattern) <= D + sum_relays e  (NA C3(a)) on random legal NetW chains/DAGs.
# Refutation is rigorous (exact.py: NONE = no F2 cover within budget is feasible even over Qbar).
# Also records the relay-blind level sum L = sum_l rank_Q M_l (YC law L <= D). Own code; imports NETATTR helpers read-only.
import sys, random
sys.path.insert(0,'../netattr')
from fractions import Fraction as Fr
from common import *
from netgen import rand_sub, rand_net, net_M
from exact import min_mass
def rankQ(M):
    M=[[Fr(x) for x in r] for r in M]; r=0
    for c in range(len(M[0]) if M else 0):
        p=next((i for i in range(r,len(M)) if M[i][c]!=0),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        for i in range(len(M)):
            if i!=r and M[i][c]!=0:
                f=M[i][c]/M[r][c]; M[i]=[x-f*y for x,y in zip(M[i],M[r])]
        r+=1
    return r
def levelsum(h,nodes,F,G,N):
    n=len(G); tot=0
    for l in range(1,h+1):
        Ml=[[0]*n for _ in range(n)]
        for g,(a,_) in enumerate(nodes):
            if dimof(a)<l: continue
            for d,(_,b) in enumerate(nodes):
                if dimof(b)>=l or N[d][g]==0: continue
                for t in range(n):
                    if G[t][d]:
                        for p in range(n): Ml[t][p]+=G[t][d]*N[d][g]*F[g][p]
        tot+=rankQ(Ml)
    return tot
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3]); Dmax=int(sys.argv[4]); mode=sys.argv[5]  # mode chain|dag
DF=len(sys.argv)>6 and sys.argv[6]=='diagfree'
random.seed(seed)
labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
Qm=[[dot(s,t) for t in labs] for s in labs]
stats={}; done=0; tries=0
while done<TR and tries<10**6:
    tries+=1
    if mode=='chain':
        A=rand_sub(h,random.randint(2,h)); B=rand_sub(h,random.randint(1,dimof(A)-1),A)
        A2=span(list(B)+[random.randrange(1<<h) for _ in range(random.randint(1,2))])
        if dimof(A2)==dimof(B): continue
        B2=rand_sub(h,random.randint(0,dimof(A2)-1),A2)
        nodes=[(A,B),(A2,B2)]; edges=[(0,1)]
    else:
        m=3; nodes=[]
        for k in range(m):
            a=rand_sub(h,random.randint(1,h)); b=rand_sub(h,random.randint(0,dimof(a)-1),a); nodes.append((a,b))
        edges=[(j,k) for k in range(m) for j in range(k) if nodes[j][1]<=nodes[k][0] and random.random()<.7]
        if not edges: continue
    E=sum(dimof(nodes[k][0])-dimof(nodes[j][1]) for j,k in edges)
    D=sum(dimof(a)-dimof(b) for a,b in nodes)
    if E==0 or D>Dmax: continue
    if mode=='chain':
        xf=dimof(A)-dimof(A&A2); xb=dimof(span(list(B)+list(B2)))-dimof(B2)
        if min(xf,xb)<=E: continue   # only the regime the simple row maps do NOT cover
    F,G,H=rand_net(h,labs,nodes,edges,dens=.6)
    M,N=net_M(G,H,F)
    T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    if all(T[t][p]==0 for t in range(n) for p in range(n) if not (DF and t==p)): continue
    L=levelsum(h,nodes,F,G,N)
    st,c,R,res=min_mass(h,labs,T,Qm,D+E,timeout=60,diagfree=DF)
    done+=1; key=(D,E,st); stats[key]=stats.get(key,0)+1
    if st!='FEASIBLE':
        print('VIOL?' if st=='NONE' else 'UND', 'D',D,'E',E,'L',L,st,'nodes',[(sorted(a),sorted(b)) for a,b in nodes],'edges',edges,'F',F,'G',G,'H',H,flush=True)
    if done%1==0: print('progress',done,stats,flush=True)
print('h',h,mode,'DF' if DF else 'exact','stats (D,E,status):count',stats,flush=True)

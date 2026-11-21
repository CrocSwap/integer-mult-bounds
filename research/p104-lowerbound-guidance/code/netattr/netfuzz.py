# random legal DAG networks (2-4 nodes, relays where legal); exact min decoder mass vs D. own code.
import sys, random, time
from common import *
from netgen import *
from exact import min_mass
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3]); mmax=int(sys.argv[4]); Dmax=int(sys.argv[5])
ctrl=len(sys.argv)>6 and sys.argv[6]=='ctrl'   # control: ignore relay rule
random.seed(seed)
labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
Qm=[[dot(s,t) for t in labs] for s in labs]
stats={'feas':0,'none':0,'und':0,'skip':0}
for tr in range(TR):
    m=random.randint(2,mmax); nodes=[]
    for k in range(m):
        # bias: later nodes contain some earlier b to allow relays
        if k>0 and random.random()<.7:
            j=random.randrange(k); bj=nodes[j][1]
            a=span(list(bj)+[random.randrange(1<<h) for _ in range(random.randint(0,2))])
        else: a=rand_sub(h,random.randint(1,h))
        if dimof(a)==0: a=rand_sub(h,1)
        b=rand_sub(h,random.randint(0,dimof(a)-1),a)
        nodes.append((a,b))
    D=sum(dimof(a)-dimof(b) for a,b in nodes)
    if D>Dmax: stats['skip']+=1; continue
    edges=[(j,k) for k in range(m) for j in range(k) if (ctrl or nodes[j][1]<=nodes[k][0]) and random.random()<.8]
    if not edges: stats['skip']+=1; continue
    if ctrl:
        F,G,H=rand_net(h,labs,nodes,[]); 
        for (j,k) in edges: H[k][j]=random.choice((1,2,3,-1))
    else: F,G,H=rand_net(h,labs,nodes,edges)
    M,_=net_M(G,H,F)
    T=[[M[t][p]*Qm[t][p] for p in range(n)] for t in range(n)]
    if all(x==0 for r in T for x in r): stats['skip']+=1; continue
    t0=time.time()
    st,c,R,res=min_mass(h,labs,T,Qm,D,timeout=60)
    key={'FEASIBLE':'feas','NONE':'none','UNDECIDED':'und'}[st]; stats[key]+=1
    print(tr,'m',m,'d',[dimof(a)-dimof(b) for a,b in nodes],'edges',edges,'D',D,st,[R[i][2] for i in c] if c else '','covers',len(res),'%.1fs'%(time.time()-t0),flush=True)
    if st!='FEASIBLE':
        print('  INSTANCE',dict(nodes=[(sorted(a),sorted(b)) for a,b in nodes],edges=edges,F=F,G=G,H=H),flush=True)
print('STATS',stats)

# [C] check of the BOWTIE theorem: in-arborescence -> hub -> out-arborescence; gathers only in in-part(+hub), deposits only in out-part(+hub).
# claim: M = w v^T exactly (w = (G N)[:,hub] restricted to out-part, v = content of hub) and price(w,v) <= total drop.
# control: allow a deposit at an in-part node / gather at an out-part node -> rank/price claims should fail.
import sys, random
from common import *
from netgen import rand_sub, net_M
seed=int(sys.argv[1]); h=int(sys.argv[2]); TR=int(sys.argv[3]); ctrl=False; rule=len(sys.argv)>4
random.seed(seed)
labs=[x for x in range(1,1<<h) if bin(x).count('1')&1]; n=len(labs)
viol_rank=viol_price=tight=0
for tr in range(TR):
    # build hub first, then in-tree (children of nodes, b_child <= a_parent), out-tree (a_child >= b_parent)
    ah=rand_sub(h,random.randint(1,h)); bh=rand_sub(h,random.randint(0,dimof(ah)-1),ah)
    nodes=[(ah,bh)]; parent={0:None}; side={0:'hub'}
    for _ in range(random.randint(1,4)):   # in-part: node c feeds an existing in/hub node p: b_c <= a_p
        p=random.choice([k for k in side if side[k] in ('hub','in')]); ap=nodes[p][0]
        b=rand_sub(h,random.randint(0,dimof(ap)),None if rule else ap); a=span(list(b)+[random.randrange(1<<h) for _ in range(random.randint(1,3))])
        if dimof(a)==dimof(b): continue
        nodes.append((a,b)); k=len(nodes)-1; parent[k]=p; side[k]='in'
    for _ in range(random.randint(1,4)):   # out-part: p feeds new node c: b_p <= a_c
        p=random.choice([k for k in side if side[k] in ('hub','out')]); bp=nodes[p][1]
        a=span(list(bp)+[random.randrange(1<<h) for _ in range(random.randint(0,3))])
        if dimof(a)==0: continue
        b=rand_sub(h,random.randint(0,dimof(a)-1),a)
        nodes.append((a,b)); k=len(nodes)-1; parent[k]=p; side[k]='out'
    m=len(nodes); H=[[0]*m for _ in range(m)]
    for k in range(1,m):
        p=parent[k]
        if side[k]=='in': H[p][k]=random.choice((1,2,3,-1,-2))   # k -> p
        else: H[k][p]=random.choice((1,2,3,-1,-2))               # p -> k
    F=[[0]*n for _ in range(m)]; G=[[0]*m for _ in range(n)]
    for k,(a,b) in enumerate(nodes):
        cang = side[k] in ('in','hub') or ctrl; cand = side[k] in ('out','hub') or ctrl
        for p,q in enumerate(labs):
            if cang and q in a and random.random()<.6: F[k][p]=random.choice((1,2,3,-1))
            if cand and all(dot(q,y)==0 for y in b) and random.random()<.6: G[p][k]=random.choice((1,2,3,-1))
    # H indexes: H[target][source]; need DAG order for N=sum H^i (nilpotent since tree)
    M,N=net_M(G,H,F)
    v=[sum(N[0][k]*F[k][p] for k in range(m)) for p in range(n)]      # hub content
    w=[sum(G[t][k]*N[k][0] for k in range(m)) for t in range(n)]      # hub's downstream deposit vector
    Qm=[[dot(s,t) for t in labs] for s in labs]
    exact=all(M[t][p]*Qm[t][p]==w[t]*v[p]*Qm[t][p] for t in range(n) for p in range(n))
    D=sum(dimof(a)-dimof(b) for a,b in nodes)
    pr=price([labs[t] for t in range(n) if w[t]],[labs[p] for p in range(n) if v[p]])
    viol_rank+= (not exact); viol_price+= (pr>D); tight+=(pr==D)
print('h',h,'RULE-DROPPED ctrl' if rule else 'legal','trials',TR,'odd-cell mismatch',viol_rank,'price>drop',viol_price,'tight',tight)

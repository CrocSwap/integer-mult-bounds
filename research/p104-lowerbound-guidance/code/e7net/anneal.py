# SA over chart structures (a_k,b_k), total drop <= Dmax, objective = LM residual (feasibility proxy). Control: Dmax=49 must reach ~0.
from lm7 import *
import math, sys, json, random, time
kind=sys.argv[1]; Dmax=int(sys.argv[2]); seed=int(sys.argv[3]); minutes=float(sys.argv[4]); start=sys.argv[5] if len(sys.argv)>5 else 'dec'
rng=random.Random(seed)
ports=shard(kind); N0=dec_net(ports); setlabels(ports)
V=span([NL.L[i] for i in range(len(ports))]); dV=len(V)
def rsub(d,within):
    # random subspace of dim d inside span `within`
    for _ in range(100):
        vs=[]; 
        while len(span(vs))<d:
            x=0
            for b in within:
                if rng.random()<.5: x^=b
            vs.append(x)
        s=span(vs)
        if len(s)==d: return s
def rsub_containing(d,base,within):
    s=span(base)
    while len(s)<d:
        x=0
        for b in within:
            if rng.random()<.5: x^=b
        s2=span(s+[x])
        if len(s2)>len(s): s=s2
    return s
def drop(nodes): return sum(len(a)-len(b) for a,b in nodes)
def ok(nodes): return all(all(inspan(a,x) for x in b) and len(a)>len(b) for a,b in nodes) and drop(nodes)<=Dmax
def mutate(nodes):
    nodes=[(list(a),list(b)) for a,b in nodes]; mv=rng.random(); i=rng.randrange(len(nodes)); a,b=nodes[i]
    if mv<.2:   # new b of same dim inside a
        nb=rsub(len(b),a) if len(b)>0 else []; nodes[i]=(a,nb)
    elif mv<.4: # new a same dim containing b
        na=rsub_containing(len(a),b,V); nodes[i]=(na,b)
    elif mv<.55: # shrink a to hyperplane containing b
        if len(a)-1>len(b):
            na=rsub_containing(len(a)-1,b,a); nodes[i]=(na,b)
    elif mv<.7: # grow b
        if len(b)+1<len(a): nb=rsub_containing(len(b)+1,b,a); nodes[i]=(a,nb)
    elif mv<.8: # grow a
        if len(a)<dV: na=rsub_containing(len(a)+1,a,V); nodes[i]=(na,b)
    elif mv<.9: # shrink b
        if len(b)>0: nb=rsub(len(b)-1,b) if len(b)>1 else []; nodes[i]=(a,nb)
    else:       # split node via middle chart c
        if len(a)-len(b)>=2 and len(nodes)<MMAX:
            d=rng.randint(len(b)+1,len(a)-1); c=rsub_containing(d,b,a); nodes[i]=(a,c); nodes.append((c,b))
    return [(span(a),span(b)) for a,b in nodes]
MMAX=14
nodes=[(nd['aB'],nd['bB']) for nd in N0.nodes]
if start=='random':
    nodes=[]
    while drop(nodes)<Dmax-3 and len(nodes)<MMAX:
        d=rng.randint(2,dV); a=rsub(d,V); b=rsub(rng.randint(0,d-1),a); nodes.append((a,b))
        if drop(nodes)>Dmax: nodes.pop()
while not ok(nodes):
    nodes=mutate(nodes) if drop(nodes)<=Dmax else mutate(nodes)
def evalc(nodes,reps=2):
    S=Struct(ports,nodes); best=1e9
    for r in range(reps):
        c,x=S.solve(rng.randrange(10**6),iters=100,tol=1e-9)
        best=min(best,c)
        if c<1e-7: break
    return best
cur=evalc(nodes); best=cur; t0=time.time(); it=0; T=0.5; hist=[]
print('start D',drop(nodes),'m',len(nodes),'cost',cur,flush=True)
while time.time()-t0<minutes*60:
    it+=1
    new=mutate(nodes)
    if not ok(new): continue
    c=evalc(new)
    if c<1e-6:
        print('FEASIBLE D=%d m=%d it=%d'%(drop(new),len(new),it),[ (len(a),len(b)) for a,b in new],flush=True)
        json.dump(dict(kind=kind,D=drop(new),nodes=[(a,b) for a,b in new]),open('feas_%s_%d_%d.json'%(kind,Dmax,seed),'w')); break
    dl=math.log(c+1e-12)-math.log(cur+1e-12)
    if dl<0 or rng.random()<math.exp(-dl/T): nodes=new; cur=c
    best=min(best,c)
    if it%20==0: print(it,'D',drop(nodes),'m',len(nodes),'cur %.3g best %.3g'%(cur,best),'%.0fs'%(time.time()-t0),flush=True)
print('end',it,'best',best)

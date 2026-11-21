# one-unit shrink neighbourhood of the decoder (D-1), LM with border detection (cost vs |x| power law).
from lm7 import *
import random, sys, pickle
kind=sys.argv[1]; per=int(sys.argv[2]); rng=random.Random(11)
ports=shard(kind); N0=dec_net(ports); setlabels(ports)
nodes0=[(nd['aB'],nd['bB']) for nd in N0.nodes]; D0=sum(len(a)-len(b) for a,b in nodes0)
V=span(NL.L); labset=set(NL.L)
def rnd_in(sp,k):
    while True:
        x=0
        for y in sp:
            if rng.random()<.5: x^=y
        if x: return x
def run(nodes,tag):
    S=Struct(ports,nodes); best=1e9; bx=None
    for r in range(4):
        c,x=S.solve(rng.randrange(10**6),iters=400,tol=1e-12)
        if c<best: best,bx=c,x
    line='%s D %d min resid %.3e'%(tag,S.D,best)
    if 1e-12<best<0.05:
        # continue best run: crude border test via second run with more iters, report |x|
        c2,x2=S.solve(rng.randrange(10**6),iters=1500,tol=1e-12)
        line+=' | long %.2e |x| %.0f'%(c2,np.linalg.norm(x2))
    if best<1e-9: line+=' EXACT-FEASIBLE?'
    print(line,flush=True); return best
for i in range(len(nodes0)):
    a,b=nodes0[i]
    for p in range(per):
        # b grows by x (x in a, not in b): record whether x is a port label
        while True:
            x=rnd_in(a,1)
            nb=span(b+[x])
            if len(nb)==len(b)+1 and (p%2==0)==(x in labset): break
        run(nodes0[:i]+[(a,nb)]+nodes0[i+1:],'row %d b+x(label=%s)'%(i,x in labset))
    for p in range(per):
        # a shrinks to hyperplane containing b
        while True:
            f=rnd_in(a,1)     # hyperplane = {y in a: dot(y,w)=0} choose w random in F2^9
            w=rng.randrange(1,512); na=span([y for y in _ for _ in []]) if False else None
            els=[0]
            for y in a: els+=[e^y for e in els]
            h=[e for e in els if dot(e,w)==0]
            na=span(h)
            if len(na)==len(a)-1 and all(inspan(na,y) for y in b): break
        run(nodes0[:i]+[(na,b)]+nodes0[i+1:],'row %d a->hyperplane'%i)

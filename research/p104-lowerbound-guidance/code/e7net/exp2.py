from lm7 import *
import random, sys
kind=sys.argv[1]; rng=random.Random(3)
ports=shard(kind); N0=dec_net(ports); setlabels(ports)
nodes0=[(nd['aB'],nd['bB']) for nd in N0.nodes]; D0=sum(len(a)-len(b) for a,b in nodes0)
V=span(NL.L)
def lm(nodes,reps=4):
    S=Struct(ports,nodes); return min(S.solve(rng.randrange(10**6),iters=150)[0] for _ in range(reps)),S.D
print(kind,'decoder D',D0,'control',lm(nodes0,2))
# (a) delete each row (rank floor)
for i in range(len(nodes0)):
    print('drop row',i,'D',D0-(len(nodes0[i][0])-len(nodes0[i][1])),'resid %.3f'%lm(nodes0[:i]+nodes0[i+1:])[0],flush=True)
# (b) shrink: grow b by 1 or shrink a by 1, random choices
res=[]
for t in range(24):
    i=rng.randrange(len(nodes0)); a,b=nodes0[i]
    if rng.random()<.5:
        while True:
            x=0
            for y in a:
                if rng.random()<.5: x^=y
            nb=span(b+[x])
            if len(nb)==len(b)+1: break
        nn=(a,nb)
    else:
        while True:
            x=0
            for y in a:
                if rng.random()<.5: x^=y
            na=span(b+[x]+[z for z in a if rng.random()<.5][:len(a)-2-len(b)]) 
            if len(b)<len(na)<len(a) and all(inspan(a,z) for z in na): break
        nn=(na,b)
    nodes=nodes0[:i]+[nn]+nodes0[i+1:]
    c,D=lm(nodes,3); res.append(c)
    if c<0.1:
        S=Struct(ports,nodes); best=None
        for sd in range(6):
            c2,x=S.solve(100+sd,iters=1500,tol=1e-14)
            print('   long run',sd,'resid %.3e'%c2,'|x| %.1f'%np.linalg.norm(x),'max|x| %.1f'%abs(x).max(),flush=True)
        import pickle; pickle.dump(nodes,open('cand_%s_%d.pkl'%(kind,t),'wb'))
    print('shrink',i,(len(nn[0]),len(nn[1])),'D',D,'resid %.3f'%c,flush=True)
print('min shrink resid',min(res))

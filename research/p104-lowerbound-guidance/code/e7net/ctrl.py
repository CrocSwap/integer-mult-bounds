from lm7 import *
ports=shard('e7'); N=dec_net(ports)
S=Struct(ports,[(nd['aB'],nd['bB']) for nd in N.nodes])
print('m',S.m,'D',S.D,'nv',S.nv,'odd',len(S.odd),'edges',len(S.edges))
for seed in range(3):
    t=time.time(); c,x=S.solve(seed,iters=300,verbose=False); print(seed,'cost',c,'time',time.time()-t,flush=True)

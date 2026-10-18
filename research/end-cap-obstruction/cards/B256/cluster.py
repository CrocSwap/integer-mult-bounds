from plan import *
import random
w=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz');M=Model(w);P=M.P;NA=len(w['A'])
g0=NA+239
regs=(124,125,148,149,231,283,281,299,297,591)
cur0={r:M.frame_at(r,g0) for r in regs}
print({r:len(f) for r,f in cur0.items()})
ops={'r1':(125,231),'r2':(124,231),'r3':(124,283),'r4':(125,281),'a3':(591,283),'a1':(591,281),
     's1':(149,231),'s2':(148,231),'s3':(148,299),'s4':(149,297),'b9':(591,299),'b7':(591,297)}
def run(perm,extra=None):
    cur=dict(cur0)
    for n in perm:
        t,s=ops[n];F=G.basis(list(cur[t])+list(cur[s]));cur[t]=cur[s]=F
    return cur
def score(cur):
    c=[inperp(cur[124],12,P),inperp(cur[125],13,P),inperp(cur[148],36,P),inperp(cur[149],37,P),inperp(cur[591],58,P)]
    return sum(c),c
names=list(ops);random.seed(1);best=0;sols=[]
for it in range(20000):
    perm=names[:];random.shuffle(perm)
    s,c=score(run(perm))
    if s==5: sols.append(perm)
print(len(sols)); print(sols[:3])
# identify extra constraint: 591 also in perp(63)
ok63=[p for p in sols if inperp(run(p)[591],63,P)]
print('also perp63',len(ok63))
import json;json.dump(sols[:200],open('cluster_sols.json','w'))

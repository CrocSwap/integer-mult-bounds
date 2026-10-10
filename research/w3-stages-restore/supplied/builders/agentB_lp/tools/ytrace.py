import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
t=int(sys.argv[2])
F,Lp,K=target_parts(t)
atoms=[('F%d'%p,m) for p,m in F.items()]+[('L%d%d'%ab,x[2]) for ab,x in Lp.items()]+[('K%d'%k,1<<k) for k in K]
def desc(m):
    out=[]; rest=m
    for name,am in atoms:
        if am&m==am: out.append(name); rest&=~am
        elif am&m: out.append('%s~%d/%d'%(name,popc(am&m),popc(am)))
    ext=popc(rest & ~mask(range(v)) ) 
    nn=N_of(t)
    outside=popc(m&~nn)
    s=' '.join(out)
    if outside: s+=' +OUT%d'%outside
    return s
y=v+t
print('target',t,lab[t],'chain',[(c[0],c[2]) for c in chain[y]])
for e in ev:
    if e[1]==y:
        print('k=%d @d%d frame %d  += H%d : %s   -> %s'%(e[0],e[4],e[3],e[2],desc(e[6]),desc(e[7])))

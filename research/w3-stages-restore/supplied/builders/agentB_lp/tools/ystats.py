import sys, pickle, collections
sys.path.insert(0,'/home/claude/work/agentB/tools')
from base import *
L=pickle.load(open(sys.argv[1],'rb'))
ev=L['ev']; n=L['n']; dim=L['dim']; init=L['init']; chain=L['chain']
byy=collections.defaultdict(list)
for e in ev:
    if v<=e[1]<2*v: byy[e[1]-v].append(e)
pat=collections.Counter(); chains=collections.Counter()
for t in range(v):
    F,Lp,K=target_parts(t)
    c,d,e_=lab[t]
    nameF={c:'Fc',d:'Fd',e_:'Fe'}
    atoms=[(nameF[p],m) for p,m in F.items()]+[({(c,d):'Lcd',(c,e_):'Lce',(d,e_):'Lde'}[ab],x[2]) for ab,x in Lp.items()]+[('K',1<<k) for k in K]
    def desc(m):
        out=[]; rest=m
        for name,am in atoms:
            if am&m==am: out.append(name); rest&=~am
            elif am&m: out.append('%s~'%(name))
        nn=N_of(t)
        if m&~nn: out.append('OUT')
        return '+'.join(out) if out else '0'
    seq=tuple('d%d:%s'%(e[4],desc(e[6])) for e in byy[t])
    pat[seq]+=1
    chains[tuple(c_[2] for c_ in chain[v+t])]+=1
for s,c in pat.most_common(40): print(c,' | '.join(s))
print(len(pat))
for s,c in chains.most_common(20): print(c,s)

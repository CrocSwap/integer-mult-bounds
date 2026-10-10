# Independent replay of an abstract design JSON (meet3 format).
import json, sys
D=json.load(open(sys.argv[1])); n=10
N=len(D); T=max(h[0] for h in D[0]['hist'])
K={d['r']:(set([d['r']]) if d['R'] else set()) for d in D}
C={d['r']:(set([d['r']]) if d['R'] else set()) for d in D}
role={d['r']:d['role'] for d in D}; tgt={d['r']:d['tgt'] for d in D}
ok=True
for t in range(1,T+1):
    groups={}
    met={d['r']:set(d['hist'][t][3]) for d in D}
    recv={d['r']:d['hist'][t][4] for d in D}
    # check symmetric meets and transitivity -> groups
    for r in met:
        for s in met[r]:
            if r not in met[s]: print('asym meet',t,r,s); ok=False
    seen=set(); grps=[]
    for r in met:
        if r in seen: continue
        g={r}|met[r]
        for s in g:
            if met[s]|{s}!=g: print('nontransitive',t,r,s); ok=False
        seen|=g; grps.append(g)
    newK={}
    for g in grps:
        U=set().union(*[K[r] for r in g])
        for r in g: newK[r]=set(U) if len(g)>1 else set(K[r])
    newC={}
    for r in C:
        c=set(C[r])
        for s in recv[r]:
            if s not in met[r]: print('give without meet',t,r,s); ok=False
            if recv[s]: print('giver also receives',t,s); ok=False
            c^=C[s]
        newC[r]=c
    K,C=newK,newC
    for r in K:
        if role[r] in 'OM' and tgt[r] in K[r]: print('target contaminated',t,r); ok=False
        if not C[r]<=K[r]: print('content outside K',t,r); ok=False
        hK=''.join('%d'%x for x in sorted(K[r])); hC=''.join('%d'%x for x in sorted(C[r]))
        dK=D[[d['r'] for d in D].index(r)]['hist'][t]
        if dK[1]!=hK or dK[2]!=hC: print('mismatch with recorded',t,r,dK[1],hK,dK[2],hC); ok=False
for z in range(n):
    Os=[r for r in K if role[r]=='O' and tgt[r]==z]; Ms=[r for r in K if role[r]=='M' and tgt[r]==z]
    if len(Os)!=1 or len(Ms)!=1: print('bad roles',z); ok=False; continue
    if C[Os[0]]^C[Ms[0]]!=set(range(n))-{z}: print('bad final',z); ok=False
print('CHECK','OK' if ok else 'FAIL')

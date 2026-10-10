# Independent replay of a meet4 design JSON (with sigma>0 fresh registers and dirt symbols).
import json, sys
D=json.load(open(sys.argv[1])); n=10
T=max(h[0] for h in D[0]['hist'])
regs=[d['r'] for d in D]; byr={d['r']:d for d in D}
K={}; C={}
for d in D:
    r=d['r']
    if d['R']: K[r]={r}; C[r]={r}
    elif d.get('sig'): K[r]=set(int(c) for c in d['hist'][0][1]); C[r]={'d%d'%r}
    else: K[r]=set(); C[r]=set()
ok=True
for r in regs:
    if byr[r]['tgt'] in K[r]: print('target in K0',r); ok=False
for t in range(1,T+1):
    met={r:set(byr[r]['hist'][t][3]) for r in regs}
    recv={r:byr[r]['hist'][t][4] for r in regs}
    seen=set(); grps=[]
    for r in regs:
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
    for r in regs:
        c=set(C[r])
        for s in recv[r]:
            if s not in met[r]: print('give w/o meet',t,r,s); ok=False
            if recv[s]: print('giver receives',t,s); ok=False
            c^=C[s]
        newC[r]=c
    K,C=newK,newC
    for r in regs:
        if byr[r]['tgt'] in K[r]: print('target contaminated',t,r); ok=False
        if not set(x for x in C[r] if isinstance(x,int))<=K[r]: print('content outside K',t,r); ok=False
for z in range(n):
    O=[r for r in regs if byr[r]['role']=='O' and byr[r]['tgt']==z]; M=[r for r in regs if byr[r]['role']=='M' and byr[r]['tgt']==z]
    if len(O)!=1 or len(M)!=1: print('roles',z); ok=False; continue
    if C[O[0]]^C[M[0]]!=set(range(n))-{z}: print('bad final',z,C[O[0]]^C[M[0]]); ok=False
print('CHECK','OK' if ok else 'FAIL')

# THINQ tq7: soundness of the thin-branch rows on #7113 type A (data: MONOCALLER/7113_CALLER.json; pieces = paid IDLE sets + leftover singletons)
import json
from collections import defaultdict
C=json.load(open('cards/WILD/MONOCALLER/7113_CALLER.json')); k=C['stages']
for tn in ('A','B'):
    v=C['types'][tn]; off=v['offset']; pcs=defaultdict(list)
    for e in C['events']:
        if e[0]==tn and e[1] in ('IDLE_ONE','IDLE_ODD'): pcs[e[2]-off].append(frozenset(x-1 for x in e[3]))
    T=sum(1 for e in C['events'] if e[0]==tn and e[1]=='QUERY')
    roles=[]; ok=True
    for i,d in enumerate(v['diagonal']):
        m=frozenset(j for j,b in enumerate(d[2:]) if b); u=set()
        for q in pcs.get(i,[]):
            if q&u or not q<=m: ok=False
            u|=q
        roles.append((m,list(pcs.get(i,[]))+[frozenset([x]) for x in m-u]))
    n=len(roles); Q=n-2*k+2; d1=sum(1 for m,_ in roles if len(m)==1); d0=sum(1 for m,_ in roles if len(m)==0)
    deep=[sum(1 for m,ps in roles if len(m)>=2 and s in m for q in ps if q=={s}) for s in range(k)]
    allsg=[sum(1 for m,ps in roles if s in m for q in ps if q=={s}) for s in range(k)]
    leaves_by_stage=defaultdict(int)
    for m,_ in roles:
        if len(m)==1: leaves_by_stage[min(m)]+=1
    print(tn,'partition',ok,'n',n,'k',k,'Q=n-2k+2',Q,'T(QUERY)',T,'e=T-Q',T-Q,'leaves',d1,'empty-mask',d0,'leaves/stage',dict(leaves_by_stage))
    print('  singletons on DEGREE>=2 roles per stage (RC2_2 needs >=2):',deep,'min',min(deep))
    print('  all singletons per stage:',allsg)
    print('  per-stage leaf law |F_s|<=T:',all(c<=T for c in leaves_by_stage.values()),' global d1<=T [CONJ]:',d1<=T)

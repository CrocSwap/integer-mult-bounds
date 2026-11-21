# QBRANCH qb3: RC2 pair form + MAINS count on the #7113 type-A role frame (36 roles/port, k=17), pieces = paid IDLE sets (ids are 1-based stages) + leftover singleton mains
import json,itertools
from collections import defaultdict
C=json.load(open('cards/WILD/MONOCALLER/7113_CALLER.json'))
k=17
def frame(tname):
    v=C['types'][tname]; off=v['offset']; roles=[]
    pcs=defaultdict(list)
    for e in C['events']:
        if e[0]==tname and e[1] in('IDLE_ONE','IDLE_ODD'): pcs[e[2]-off].append(frozenset(x-1 for x in e[3]))
    for i,d in enumerate(v['diagonal']):
        m=frozenset(j for j,b in enumerate(d[2:]) if b); ps=pcs.get(i,[])
        u=set();ok=True
        for q in ps:
            if q&u or not q<=m: ok=False
            u|=q
        left=m-u
        parts=list(ps)+[frozenset([x]) for x in left]
        roles.append((m,parts,ok))
    return roles
for tn in ('A','B'):
    R=frame(tn); print(tn,'roles',len(R),'partition-ok',all(r[2] for r in R))
    if not all(r[2] for r in R): 
        print(' (pieces overlap / not within mask -> type B uses repeated idle sets: not a partition model)'); continue
    mains=[sum(1 for m,ps,_ in R for q in ps if len(q)==1 and s in q) for s in range(k)]
    print(' singleton pieces per stage',mains)
    bad=0;minv=99
    for s in range(k):
        for t in range(k):
            if s==t: continue
            for l in range(2,k+2):
                lhs=0
                for m,ps,_ in R:
                    if s not in m: continue
                    P=[q for q in ps if s in q][0]; D=len(m)
                    if D>=l and len(P)<l and t not in P: lhs+=1
                    elif D<l and t in m and t not in P: lhs+=1
                minv=min(minv,lhs)
                if lhs<2: bad+=1; 
                if lhs<2 and bad<6: print('  VIOL s,t,l',s,t,l,lhs)
    print(' RC2 pair-form violations',bad,'min lhs',minv)

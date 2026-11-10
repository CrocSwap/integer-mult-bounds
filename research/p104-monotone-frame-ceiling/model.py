"""Build exact local constraints for the frame tariff.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from itertools import combinations

from frames import bounds, dimension


def model(w,g,k):
    lo,hi=bounds(w,g);n=len(lo)
    labels=[list(range(dimension(a),dimension(b)+1)) for a,b in zip(lo,hi)]
    variables=[];cost=[];nodes=[];eq=[];ub=[];tariffs=[]
    for i,values in enumerate(labels):
        table={}
        for d in values:
            table[d]=len(cost);variables.append(('node',i,d));cost.append(0.)
        nodes.append(table);eq.append((dict.fromkeys(table.values(),1),1))
    weights=Counter();successors=[set() for _ in range(n)]
    for a,b,p,_ in g['moves']:
        if p:
            a,b=b,a
        weights[a,b]+=1
        if a!=b:
            successors[a].add(b)
    main=set(w['live'])|{r+112 for r in w['live']}
    for r in range(w['public']):
        if r not in main:
            weights[g['starts'][r],g['ends'][r]]-=1
    for (a,b),weight in sorted(weights.items()):
        if a==b:
            continue
        floor=dimension(lo[b])-dimension(lo[b]&hi[a])
        table={}
        for x in labels[a]:
            for y in labels[b]:
                if y-x>=floor:
                    rank=y-x;index=len(cost);table[x,y]=index
                    variables.append(('edge',a,b,x,y))
                    cost.append(0 if k is None else weight*rank**(1-k))
                    tariffs.append((index,weight,rank))
        for x in labels[a]:
            row={i:1 for (xx,y),i in table.items() if xx==x}
            row[nodes[a][x]]=-1;eq.append((row,0))
        for y in labels[b]:
            row={i:1 for (x,yy),i in table.items() if yy==y}
            row[nodes[b][y]]=-1;eq.append((row,0))

    def dimensions(coeff,rhs):
        row=Counter()
        for a,c in coeff.items():
            for d,i in nodes[a].items():
                row[i]+=c*d
        ub.append(({i:x for i,x in row.items() if x},rhs))

    reachable=[set() for _ in range(n)];predecessors=[set() for _ in range(n)]
    for a in sorted(range(n),key=lambda i:-len(w['frames'][g['old'][i]])):
        for b in successors[a]:
            reachable[a].add(b);reachable[a].update(reachable[b]);predecessors[b].add(a)
    for a,targets in enumerate(reachable):
        for b in sorted(targets):
            floor=dimension(lo[b])-dimension(lo[b]&hi[a])
            if floor>0 and (a,b) not in weights:
                dimensions({a:1,b:-1},-floor)
    for c in range(n):
        for a,b in combinations(sorted(predecessors[c]),2):
            dimensions({a:1,b:1,c:-1},dimension(hi[a]&hi[b]))
        for a,b in combinations(sorted(successors[c]),2):
            floor=dimension(lo[a])+dimension(lo[b])-dimension(lo[a]&lo[b])
            dimensions({a:-1,b:-1,c:1},-floor)
    return variables,cost,eq,ub,tariffs

"""Independent E8 line model and bounded first-boundary discovery.

PR717/DreamingOfClouds and PR968/themilkman216 supply the mathematical model;
this implementation is prepared for @woklerx with substantial OpenAI Codex
assistance, Apache-2.0. Only the exact odd-root-pair class is explored.
"""
from itertools import combinations, product
from collections import Counter


def lines():
    roots = set()
    for i,j in combinations(range(8),2):
        for signs in product((-2,2),repeat=2):
            v=[0]*8
            v[i],v[j]=signs
            t=tuple(v)
            roots.add(max(t,tuple(-x for x in t)))
    for v in product((-1,1),repeat=8):
        if sum(x<0 for x in v)%2==0:
            roots.add(max(v,tuple(-x for x in v)))
    return sorted(roots)


def rank(rows):
    pivots={}
    for row in rows:
        while row:
            p=row.bit_length()-1
            if p not in pivots:
                pivots[p]=row
                break
            row^=pivots[p]
    return len(pivots)


def setup():
    roots=lines()
    dot=lambda a,b:sum(x*y for x,y in zip(a,b))
    pairing=[sum((((dot(a,b)//4)+1)&1)<<j for j,b in enumerate(roots)) for a in roots]
    basis=[]
    for i in range(120):
        if rank([pairing[x] for x in basis+[i]])>len(basis):basis.append(i)
        if len(basis)==9:break
    labels=[sum(((row>>b)&1)<<j for j,b in enumerate(basis)) for row in pairing]
    viol=[sum(((lam&label).bit_count()%2)<<i for i,label in enumerate(labels)) for lam in range(1,512)]
    supports=[sum((dot(a,b)!=0)<<j for j,b in enumerate(roots)) for a in roots]
    return roots,pairing,labels,viol,supports


def candidates(viol,support,limit):
    restricted=[x&support for x in viol]
    return {x|y for i,x in enumerate(restricted) for y in restricted[i+1:] if (x|y).bit_count()<=limit}


def cost(pairing,supports,a,b,p):
    return rank([row&(supports[b]&~p) for i,row in enumerate(pairing) if (supports[a]&~p)>>i&1])


def main():
    roots,pairing,labels,viol,supports=setup()
    a=48
    b=next(i for i in range(120) if abs(sum(x*y for x,y in zip(roots[a],roots[i])))==4)
    masks=candidates(viol,supports[a],25)|candidates(viol,supports[b],25)
    dist=Counter(cost(pairing,supports,a,b,p) for p in masks)
    print('pair',a,b,'masks25',len(masks),'ranks',dict(dist),flush=True)
    hits=[p for p in masks if cost(pairing,supports,a,b,p)<=6]
    if not hits:
        for p in sorted(masks):
            for i in range(120):
                if p>>i&1:continue
                q=p|(1<<i)
                if cost(pairing,supports,a,b,q)<=6:
                    print('FIRST26',q,'cost',cost(pairing,supports,a,b,q),'indices',[i for i in range(120) if q>>i&1],flush=True)
                    return
    print('HITS25',hits[:3],flush=True)


if __name__=='__main__':main()

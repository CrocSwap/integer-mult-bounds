#!/usr/bin/env python3
"""Explicit disjointness rectangle partitions and exact membership counts.

The dynamic program optimizes only the listed recursive/row/column strategies.
It is not a global lower bound on rectangle representations or finite networks.
"""
from dataclasses import dataclass
from functools import cache
from itertools import combinations, product
from math import comb


@dataclass(frozen=True)
class Plan:
    n: int
    a: int
    b: int
    count: int
    left: int
    right: int
    kind: str
    split: int = 0
    terms: tuple = ()

    def score(self, alpha=1, beta=1):
        return alpha*self.left+beta*self.right-self.count


def stars(n, a, b, kind):
    if a+b>n:
        return Plan(n,a,b,0,0,0,'empty')
    if kind=='rows':
        c=comb(n,a)
        return Plan(n,a,b,c,c,c*comb(n-a,b),kind)
    c=comb(n,b)
    return Plan(n,a,b,c,c*comb(n-b,a),c,kind)


@cache
def best(n, a, b, alpha=1, beta=1):
    assert 0<=a<=2 and 0<=b<=2 and n>=0 and alpha>0 and beta>0
    if a+b>n:
        return Plan(n,a,b,0,0,0,'empty')
    if not a or not b:
        return Plan(n,a,b,1,comb(n,a),comb(n,b),'base')
    score=lambda p:p.score(alpha,beta)
    winner=min((stars(n,a,b,'rows'),stars(n,a,b,'cols')),key=score)
    for l in range(1,n):
        r=n-l
        terms=[]
        for x in range(a+1):
            for y in range(b+1):
                aa,bb=a-x,b-y
                if x+y>l or aa+bb>r:
                    continue
                if x==y==aa==bb==1:
                    # Restricted product search; no global optimality claim.
                    left=(best(l,1,1),stars(l,1,1,'rows'),stars(l,1,1,'cols'))
                    right=(best(r,1,1),stars(r,1,1,'rows'),stars(r,1,1,'cols'))
                    A,B=min(product(left,right),key=lambda pair:
                        alpha*pair[0].left*pair[1].left+
                        beta*pair[0].right*pair[1].right-
                        pair[0].count*pair[1].count)
                elif not x or not y:
                    A=best(l,x,y)
                    B=best(r,aa,bb,alpha*A.left,beta*A.right)
                else:
                    B=best(r,aa,bb)
                    A=best(l,x,y,alpha*B.left,beta*B.right)
                terms.append((A,B))
        candidate=Plan(n,a,b,sum(A.count*B.count for A,B in terms),
                       sum(A.left*B.left for A,B in terms),
                       sum(A.right*B.right for A,B in terms),'split',l,tuple(terms))
        if score(candidate)<score(winner):
            winner=candidate
    return winner


def rectangles(plan, points=None):
    """Yield (source-family,target-family), each a tuple of subsets."""
    if points is None:
        points=tuple(range(plan.n))
    assert len(points)==plan.n
    if plan.kind=='empty':
        return
    if plan.kind=='base':
        yield tuple(combinations(points,plan.a)),tuple(combinations(points,plan.b))
    elif plan.kind=='rows':
        for s in combinations(points,plan.a):
            yield (s,),tuple(combinations(tuple(i for i in points if i not in s),plan.b))
    elif plan.kind=='cols':
        for t in combinations(points,plan.b):
            yield tuple(combinations(tuple(i for i in points if i not in t),plan.a)),(t,)
    else:
        assert plan.kind=='split'
        left,right=points[:plan.split],points[plan.split:]
        for A,B in plan.terms:
            for s1,t1 in rectangles(A,left):
                for s2,t2 in rectangles(B,right):
                    yield (tuple(x+y for x in s1 for y in s2),
                           tuple(x+y for x in t1 for y in t2))


def verify_partition(n, a=2, b=2):
    """Exhaustively check each ordered disjoint pair occurs exactly once."""
    p=best(n,a,b)
    sources=list(combinations(range(n),a));targets=list(combinations(range(n),b))
    si={s:i for i,s in enumerate(sources)};ti={t:i for i,t in enumerate(targets)}
    width=len(targets);seen=bytearray(len(sources)*width)
    counts=[0,0,0];edges=0
    for S,T in rectangles(p):
        assert S and T
        counts[0]+=1;counts[1]+=len(S);counts[2]+=len(T)
        for s in S:
            for t in T:
                assert not set(s)&set(t)
                index=si[s]*width+ti[t]
                assert not seen[index], 'Overlapping partition rectangles'
                seen[index]=1;edges+=1
    assert counts==[p.count,p.left,p.right]
    assert edges==comb(n,a)*comb(n-a,b)
    return dict(n=n,a=a,b=b,rectangles=p.count,left_memberships=p.left,
                right_memberships=p.right,scratch_roles=p.score(),edges=edges,
                all_ordered_disjoint_pairs_exactly_once=True)


if __name__=='__main__':
    print(verify_partition(45))

"""Explicit intersection-two permutations in every even dimension h >= 8.

Extends PR #7's matching by replacing its Euler tour with a Hamilton cycle
in the line graph of a complete graph. No new scalar-circuit claim.
"""
from itertools import combinations
from math import comb
import argparse
import json


def edge_cycle(vertices):
    assert len(vertices) >= 3 and len(set(vertices)) == len(vertices)
    a, b, c = vertices[:3]
    cycle = [tuple(sorted(e)) for e in ((a,b), (b,c), (c,a))]
    for new in vertices[3:]:
        shared, = set(cycle[0]) & set(cycle[1])
        last, = set(cycle[1]) - {shared}
        old = sorted({x for edge in cycle for x in edge})
        order = [shared] + [x for x in old if x not in (shared,last)] + [last]
        cycle[1:1] = [tuple(sorted((x,new))) for x in order]
    assert set(cycle) == set(combinations(sorted(vertices),2))
    assert len(cycle) == comb(len(vertices),2)
    successor = {edge:cycle[(i+1)%len(cycle)] for i,edge in enumerate(cycle)}
    assert len(set(successor.values())) == len(cycle)
    assert all(len(set(a)&set(b)) == 1 for a,b in successor.items())
    return successor


def matching(h):
    assert h >= 8 and h % 2 == 0
    q = h//2
    cycles = {i:edge_cycle([j for j in range(q) if j!=i]) for i in range(q)}
    images = set()
    for S in combinations(range(h),5):
        members = set(S)
        full = {x//2 for x in S if x^1 in members}
        singles = [x for x in S if x^1 not in members]
        if not full:
            keep = set(sorted(singles,key=lambda x:x//2)[:2])
            T = tuple(sorted(x if x in keep else x^1 for x in S))
        elif len(full)==1:
            T = tuple(sorted([x for x in S if x//2 in full]+[x^1 for x in singles]))
        else:
            u, = singles
            new = cycles[u//2][tuple(sorted(full))]
            T = tuple(sorted([2*j+b for j in new for b in (0,1)]+[u^1]))
        assert len(T)==len(set(T))==5 and all(0<=x<h for x in T)
        assert len(members&set(T))==2
        assert T not in images
        images.add(T)
    assert len(images)==comb(h,5)
    return dict(h=h, five_sets=comb(h,5), distinct_images=len(images),
                every_intersection_two=True)


def small_hall_control(h,r,t):
    """Independent full bipartite matching control, including odd h."""
    masks=[sum(1<<x for x in S) for S in combinations(range(h),r)]
    neighbors=[[j for j,b in enumerate(masks) if (a&b).bit_count()==t]
               for a in masks]
    degree=comb(r,t)*comb(h-r,r-t)
    assert degree>0 and all(len(row)==degree for row in neighbors)
    owner={}
    def augment(i,seen):
        for j in neighbors[i]:
            if j in seen:continue
            seen.add(j)
            if j not in owner or augment(owner[j],seen):
                owner[j]=i
                return True
        return False
    for i in range(len(masks)):assert augment(i,set())
    assert len(owner)==len(set(owner.values()))==len(masks)
    assert all((masks[i]&masks[j]).bit_count()==t for j,i in owner.items())
    return dict(h=h,r=r,t=t,vertices=len(masks),degree=degree,
                perfect_matching_verified=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('dimensions',nargs='+',type=int)
    print(json.dumps([matching(h) for h in parser.parse_args().dimensions],indent=2))

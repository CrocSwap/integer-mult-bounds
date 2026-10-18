#!/usr/bin/env python3
"""Optional deterministic witness discovery; no optimality claim is needed."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import authenticated_model


def load():
    labels, pairs, mask = authenticated_model()
    adjacency = [sum(1 << j for j in range(56) if i != j and mask[i][j]) for i in range(56)]
    return pairs, labels, adjacency


def maximum_clique(adjacency):
    best = []
    nodes = 0
    def coloring(candidates):
        order, bounds = [], []
        unused, color = candidates, 0
        while unused:
            color += 1
            available = unused
            while available:
                bit = available & -available
                v = bit.bit_length()-1
                order.append(v); bounds.append(color)
                unused ^= bit
                available &= ~bit & ~adjacency[v]
        return order,bounds
    def expand(chosen,candidates):
        nonlocal best,nodes
        nodes += 1
        order,bounds=coloring(candidates)
        for i in range(len(order)-1,-1,-1):
            if len(chosen)+bounds[i] <= len(best):
                return
            v=order[i]
            child=candidates & adjacency[v]
            if child:
                expand(chosen+[v],child)
            elif len(chosen)+1>len(best):
                best=chosen+[v]
            candidates &= ~(1<<v)
    expand([], (1<<len(adjacency))-1)
    return sorted(best),nodes


def color_with_clique(adjacency, clique, colors):
    classes = [1<<v for v in clique] + [0]*(colors-len(clique))
    remaining = ((1<<len(adjacency))-1) ^ sum(1<<v for v in clique)
    nodes=0
    def visit(left):
        nonlocal nodes
        nodes+=1
        if not left:
            return classes[:]
        choices=[]
        scan=left
        while scan:
            bit=scan&-scan;v=bit.bit_length()-1;scan^=bit
            allowed=[i for i,c in enumerate(classes) if not adjacency[v]&c]
            if not allowed:
                return None
            choices.append((len(allowed),-(adjacency[v]&left).bit_count(),v,allowed))
        _,_,v,allowed=min(choices)
        empty_used=False
        for i in allowed:
            if not classes[i]:
                if empty_used:
                    continue
                empty_used=True
            classes[i]|=1<<v
            result=visit(left&~(1<<v))
            if result:
                return result
            classes[i]^=1<<v
        return None
    result=visit(remaining)
    return (None if result is None else [[v for v in range(len(adjacency)) if c>>v&1] for c in result]),nodes


if __name__=='__main__':
    pairs,labels,adj=load()
    clique,nodes=maximum_clique(adj)
    classes,color_nodes=color_with_clique(adj,clique,25)
    print(json.dumps({'schema_version':1,'plane_clique':clique,'port_clique':sorted(i for v in clique for i in pairs[v]),'orthogonal_classes':classes},indent=2))

"""Small DAG path enumeration for a prescribed subset of terminal pairs.

This is a diagnostic for clean coding seeds, not the full all-role contract.
Budget exhaustion raises instead of being reported as nonroutability.
"""
from collections import defaultdict
from hashlib import sha256
import json

from certify import require


def partial_routing(edges,pairs,max_paths=10000,max_branches=100000):
    vertices = {x for e in edges for x in e}; adjacency = defaultdict(list)
    indegree = {v:0 for v in vertices}
    for index,(u,v) in enumerate(edges):
        adjacency[u].append((index,v)); indegree[v] += 1
    ready = [v for v in vertices if indegree[v] == 0]; count = 0
    while ready:
        u = ready.pop(); count += 1
        for _,v in adjacency[u]:
            indegree[v] -= 1
            if indegree[v] == 0: ready.append(v)
    require(count == len(vertices),'Path enumeration requires a DAG')
    require(len({s for s,t in pairs}) == len({t for s,t in pairs}) == len(pairs),
            'Terminal pairs must have distinct sources and sinks')
    options = []
    for source,target in pairs:
        cache = {}
        def paths(u):
            if u == target: return [()]
            if u not in cache:
                result = []
                for index,v in adjacency[u]:
                    for suffix in paths(v):
                        result.append((index,)+suffix)
                        require(len(result) <= max_paths,'Path enumeration budget exceeded')
                cache[u] = result
            return cache[u]
        options.append(paths(source))
    masks = [[sum(1 << edge for edge in path) for path in group] for group in options]
    order = sorted(range(len(pairs)),key=lambda i:len(options[i]))
    selected = [None]*len(pairs); branches = 0
    def choose(depth,used):
        nonlocal branches
        if depth == len(order): return True
        i = order[depth]
        for j,mask in enumerate(masks[i]):
            branches += 1
            require(branches <= max_branches,'Path-combination budget exceeded')
            if mask & used: continue
            selected[i] = j
            if choose(depth+1,used|mask): return True
        return False
    found = choose(0,0)
    return dict(routable=found,exhaustive=not found,
                path_counts=[len(group) for group in options],combination_branches=branches,
                paths=[list(options[i][j]) for i,j in enumerate(selected)] if found else None,
                all_paths_sha256=sha256(json.dumps(options,separators=(',',':')).encode()).hexdigest())

"""Bounded forward refactoring after exposing earlier sums.

Unlike adjoint factoring, this expands low-fanout nodes in the forward DAG.
Every expression remains cancellation-free. Greedy pair sharing is a search
heuristic, not an optimal rectangle-cover algorithm.
"""
from collections import Counter, defaultdict
import heapq
from itertools import combinations

from experiments.mixed_point_circuit import Circuit


def refactor(t, depth=2, max_fanout=2):
    if depth < 1 or max_fanout < 1:
        raise ValueError('Positive expansion limits required')
    uses = Counter(t.outputs)
    for node in t.active:
        if t.args[node]:
            uses.update(t.args[node])

    def expand(node, remaining):
        if remaining and t.args[node] and uses[node] <= max_fanout:
            a,b = t.args[node]
            return expand(a,remaining-1) + expand(b,remaining-1)
        return [node]

    # Only expressions reachable after expansion participate in factoring.
    expressions = {}
    pending = list(t.outputs)
    seen = set()
    while pending:
        node = pending.pop()
        if node in seen:
            continue
        seen.add(node)
        if not t.args[node]:
            continue
        terms = [x for child in t.args[node] for x in expand(child,depth-1)]
        assert len(set(terms)) == len(terms)
        expressions[node] = set(terms)
        pending.extend(terms)
    exposed_terms = sum(map(len,expressions.values()))
    occurrence = defaultdict(set)
    for node,terms in expressions.items():
        for pair in combinations(sorted(terms),2):
            occurrence[pair].add(node)
    heap = [(-len(nodes),pair) for pair,nodes in occurrence.items() if len(nodes)>1]
    heapq.heapify(heap)
    helpers = {}
    next_tag = len(t.args)
    while heap:
        negative,pair = heapq.heappop(heap)
        nodes = occurrence.get(pair,set())
        if len(nodes)<2:
            continue
        if len(nodes) != -negative:
            heapq.heappush(heap,(-len(nodes),pair))
            continue
        a,b = pair
        tag = next_tag
        next_tag += 1
        helpers[tag] = pair
        touched = set()
        for node in sorted(nodes):
            terms = expressions[node]
            others = terms-{a,b}
            for x in others:
                for v in (a,b):
                    old = tuple(sorted((x,v)))
                    occurrence[old].remove(node)
                    if not occurrence[old]:
                        del occurrence[old]
                new = tuple(sorted((x,tag)))
                occurrence[new].add(node)
                touched.add(new)
            terms.difference_update((a,b))
            terms.add(tag)
        del occurrence[pair]
        for pair in sorted(touched):
            if len(occurrence[pair])>1:
                heapq.heappush(heap,(-len(occurrence[pair]),pair))

    c = Circuit(t.n,t.k,t.l,t.r)
    image = {i:i for i in range(1,len(t.inputs)+1)}
    for output in t.outputs:
        stack = [(output,False)]
        while stack:
            node,ready = stack.pop()
            if node in image:
                continue
            terms = helpers[node] if node in helpers else sorted(expressions[node])
            if ready:
                image[node] = c.total([image[x] for x in terms])
            else:
                stack.append((node,True))
                stack.extend((x,False) for x in terms if x not in image)
    c.finish([image[x] for x in t.outputs])
    return c,dict(depth=depth,max_fanout=max_fanout,
                  exposed_expressions=len(expressions),exposed_terms=exposed_terms,
                  factored_pairs=len(helpers))

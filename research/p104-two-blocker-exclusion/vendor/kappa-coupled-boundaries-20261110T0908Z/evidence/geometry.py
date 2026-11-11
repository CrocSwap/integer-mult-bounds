"""Chart intervals and independent invoice components, derived from the 0853 screen."""

from functools import lru_cache
from math import prod

from screen import basis, boundaries


@lru_cache(None)
def subspace_count(dimension, rank):
    if rank == 0 or rank == dimension:
        return 1
    return subspace_count(dimension - 1, rank) + (2**(dimension-rank)
        * subspace_count(dimension - 1, rank - 1))


def geometry(word, graph):
    groups, frames, _, moves, _ = graph.graph(word)
    frozen, helpers = boundaries(word, groups)
    space = [graph.span(word['frames'][f]) if f is not None else None for f in frames]
    dims = [len(s).bit_length() - 1 if s is not None else -1 for s in space]
    order = sorted(range(len(groups)), key=dims.__getitem__)
    parents = [set() for _ in groups]
    children = [set() for _ in groups]
    for _, a, b in moves:
        assert space[a] < space[b]
        parents[b].add(a)
        children[a].add(b)

    @lru_cache(None)
    def join(a, b):
        if a <= b:
            return b
        if b <= a:
            return a
        result = set(a)
        for v in basis(b):
            if v not in result:
                result |= {v ^ x for x in result}
        return frozenset(result)

    low = [frozenset((0,)) for _ in groups]
    high = [frozenset(range(512)) for _ in groups]
    for i in order:
        if i in frozen and space[i] is not None:
            low[i] = space[i]
        for a in parents[i]:
            low[i] = join(low[i], low[a])
    for i in reversed(order):
        if i in frozen and space[i] is not None:
            high[i] = space[i]
        for b in children[i]:
            high[i] = high[i] & high[b]
    assert all(low[i] <= s <= high[i] for i, s in enumerate(space) if s is not None)
    variable = {i for i, s in enumerate(space) if s is not None and low[i] != high[i]}
    neighbor = [a | b for a, b in zip(parents, children)]
    for _, a, b in helpers:
        assert space[a] < space[b]
        neighbor[a].add(b)
        neighbor[b].add(a)
    islands = []
    while variable:
        pivot = min(variable)
        variable.remove(pivot)
        pending, block = [pivot], []
        while pending:
            i = pending.pop()
            block.append(i)
            for j in sorted(neighbor[i] & variable):
                variable.remove(j)
                pending.append(j)
        quotients = tuple(sorted(len(high[i]).bit_length()-len(low[i]).bit_length() for i in block))
        choices = prod(sum(subspace_count(q, r) for r in range(q+1)) for q in quotients)
        islands.append((choices, block))
    return space, low, high, moves, helpers, islands

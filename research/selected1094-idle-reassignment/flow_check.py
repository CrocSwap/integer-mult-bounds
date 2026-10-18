"""Separate exhaustive rank-vector checker using integral max-flow/min-cut.

No imports from the component reduction or majorization/attainment code.
Gareth Davidson with substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import deque
from itertools import combinations


def compositions(total, k):
    if k == 1:
        yield (total,)
    else:
        for first in range(total+1):
            for rest in compositions(total-first, k-1):
                yield (first,)+rest


def solve(k, fixed, sizes, ranks):
    """A row node for every clique, capacity one to each child node."""
    demands = [r-fixed for r in ranks]
    if min(demands) < 0 or sum(demands) != sum(sizes):
        return False, 0
    n = 2+len(sizes)+k
    source, sink = n-2, n-1
    capacity = [[0]*n for _ in range(n)]
    for row, size in enumerate(sizes):
        capacity[source][row] = size
        for j in range(k):
            capacity[row][len(sizes)+j] = 1
    for j, d in enumerate(demands):
        capacity[len(sizes)+j][sink] = d
    residual = [row[:] for row in capacity]
    value = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v, c in enumerate(residual[u]):
                if c and v not in parent:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            # Verify a cut certificate as well as the integer flow.
            cut = sum(capacity[u][v] for u in parent for v in range(n) if v not in parent)
            if cut != value:
                raise ValueError('max-flow/min-cut mismatch')
            break
        v = sink
        amount = sum(sizes)+1
        while parent[v] is not None:
            u = parent[v]
            amount = min(amount, residual[u][v])
            v = u
        v = sink
        while parent[v] is not None:
            u = parent[v]
            residual[u][v] -= amount
            residual[v][u] += amount
            v = u
        value += amount
    for u in range(n):
        if u not in (source, sink):
            net = sum(capacity[u][v]-residual[u][v] for v in range(n))
            if net != 0:
                raise ValueError('flow conservation')
    return value == sum(sizes), value


def census(table):
    records = []
    for row in table:
        k, f = row['k'], row['fixed']
        sizes = [int(q) for q, count in row['cliques'].items() for _ in range(count)]
        tested, accepted = 0, 0
        signatures = []
        for deficits in compositions(3*k, k):
            ranks = tuple(51-d for d in deficits)
            # k<=4 implies every tuple here has positive ranks.
            feasible, value = solve(k, f, sizes, ranks)
            tested += 1
            sorted_ranks = sorted(ranks, reverse=True)
            inequalities = all(sum(sorted_ranks[:s]) <= row['prefix_bounds'][s-1] for s in range(1, k+1))
            if feasible != inequalities:
                raise ValueError('prefix criterion disagrees with independent flow')
            if feasible:
                accepted += 1
                if any(sum(sorted_ranks[:s]) > sum(row['ranks'][:s]) for s in range(1, k+1)):
                    raise ValueError('witness fails to majorize a feasible vector')
            signatures.append([list(ranks), feasible, value])
        records.append(dict(k=k, fixed=f, tested=tested, accepted=accepted, verdicts=signatures))
    return records

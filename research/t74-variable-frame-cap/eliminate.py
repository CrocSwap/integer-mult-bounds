"""Exact int64 min-sum elimination; saturated infinity prevents overflow."""

import math
import numpy as np

INF = 1 << 60


def solve(dom, factors):
    for scope, table in factors:
        if scope != sorted(set(scope)) or any(i not in dom for i in scope):
            raise ValueError("factor scope must contain sorted distinct domain keys")
        if table.dtype != np.int64 or table.shape != tuple(len(dom[i]) for i in scope):
            raise ValueError("factor shape or exact integer dtype")
        if np.any(table < 0) or np.any(table > INF):
            raise ValueError("factor outside bounded nonnegative integer range")
    adj = {i: set() for i in dom}
    for scope, a in factors:
        for i in scope:
            adj[i].update(set(scope) - {i})
    steps = []
    maxstates = 0
    while adj:
        i = min(
            adj,
            key=lambda i: (
                math.prod(len(dom[j]) for j in adj[i] | {i}),
                len(adj[i]),
                i,
            ),
        )
        nb = sorted(adj.pop(i))
        scope = sorted(nb + [i])
        shape = [len(dom[j]) for j in scope]
        maxstates = max(maxstates, math.prod(shape))
        need = math.prod(shape)
        if need > 10000000:
            raise ValueError(("table exceeds registered budget", need))
        total = np.zeros(shape, dtype=np.int64)
        used = []
        for k, (ss, a) in enumerate(factors):
            if i not in ss:
                continue
            used.append(k)
            view = [len(dom[j]) if j in ss else 1 for j in scope]
            total = np.minimum(INF, total + a.reshape(view))
        used = set(used)
        factors = [f for k, f in enumerate(factors) if k not in used]
        axis = scope.index(i)
        arg = np.argmin(total, axis=axis).astype(np.int32)
        best = total.min(axis=axis)
        steps.append((i, nb, arg))
        factors.append((nb, best))
        for j in nb:
            adj[j].remove(i)
            adj[j].update(set(nb) - {j})
    score = sum(int(a) for ss, a in factors)
    chosen = {}
    for i, nb, arg in reversed(steps):
        chosen[i] = int(arg[tuple(chosen[j] for j in nb)])
    return score, chosen, maxstates

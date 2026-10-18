"""Complete interval-subspace domains and transported bounds."""

import collections
from functools import lru_cache
import frame_model as F


def linear(G, x):
    y = 0
    for i, g in enumerate(G):
        if x >> i & 1:
            y ^= g
    return y


@lru_cache(None)
def image(m, G):
    return F.mask(tuple(linear(G, x) for x in F.basis(m)))


@lru_cache(None)
def inverse(G):
    back = {linear(G, x): x for x in range(512)}
    F.need(len(G) == 9 and len(back) == 512, "singular transport")
    return tuple(back[1 << i] for i in range(9))


def bounds(fs, loc, pr, nx, transports):
    F.need(
        all(a < z for z, aa in pr.items() for a in aa),
        "edges must follow chronological order",
    )
    F.need(
        all(a < z for a, z in transports), "transports must follow chronological order"
    )
    before = {b: (a, G) for (a, b), G in transports.items()}
    after = {a: (b, inverse(G)) for (a, b), G in transports.items()}
    low = list(fs)
    high = list(fs)
    for i in range(len(fs)):
        if loc[i] is not None:
            low[i] = 1
            for j in pr[i]:
                low[i] = F.join(low[i], low[j])
            if i in before:
                j, G = before[i]
                low[i] = image(low[j], G)
    for i in reversed(range(len(fs))):
        if loc[i] is not None:
            high[i] = F.FULL
            for j in nx[i]:
                high[i] &= high[j]
            if i in after:
                j, G = after[i]
                high[i] = image(high[j], G)
    F.need(all(a & b == a for a, b in zip(low, high)), "inconsistent frame bounds")
    return low, high


def components(low, high, pr, nx, transports):
    adj = collections.defaultdict(list)
    for a, b in transports:
        adj[a].append(b)
        adj[b].append(a)
    todo = {i for i, (a, b) in enumerate(zip(low, high)) if a != b}
    result = []
    while todo:
        i = min(todo)
        todo.remove(i)
        todo2 = [i]
        component = []
        while todo2:
            i = todo2.pop()
            component.append(i)
            for j in pr[i] + nx[i] + adj[i]:
                if j in todo:
                    todo.remove(j)
                    todo2.append(j)
        result.append(sorted(component))
    return sorted(result, key=lambda x: (len(x), x))


_DOM = {}


def domain(L, U):
    key = (L, U)
    if key not in _DOM:
        extra = []
        s = L
        for x in F.basis(U):
            if not ((s >> x) & 1):
                extra.append(x)
                s = F.join(s, F.mask((x,)))
        states = {L}
        front = [L]
        vectors = []
        for mask in range(1, 1 << len(extra)):
            v = 0
            for i, x in enumerate(extra):
                if mask >> i & 1:
                    v ^= x
            vectors.append(v)
        while front:
            cur = front.pop()
            for x in vectors:
                nxt = F.join(cur, F.mask((x,)))
                if nxt not in states:
                    states.add(nxt)
                    front.append(nxt)
        _DOM[key] = sorted(states, key=lambda m: (F.rank(m), m))
    return _DOM[key]

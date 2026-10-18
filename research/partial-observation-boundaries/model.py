"""Exact six-generator boundary model; standard library only, Apache-2.0.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Rows are two-bit coefficient vectors on the incoming workspace. No predecessor
implementation is imported. Fixed children are never split by adapters.
"""
from collections import deque
from functools import lru_cache
from heapq import heapify, heappop, heappush
from itertools import product

INF = 10**6
FRAMES = tuple((a, b) for a in range(1, 4) for b in range(1, 4) if a != b)
STATES = tuple((a, b, c, d) for a, b in FRAMES for c, d in product(range(4), repeat=2))
INDEX = {s: i for i, s in enumerate(STATES)}
START = INDEX[(1, 2, 0, 0)]
GATES = ("w0^=w1", "w1^=w0", "d0^=w0", "d0^=w1", "d1^=w0", "d1^=w1")
CHILDREN = tuple(product(range(2), repeat=3))  # output, reader, shear destination


def gate(state, op):
    rows = list(state)
    if op < 2:
        rows[op] ^= rows[1 - op]
    else:
        dest, source = divmod(op - 2, 2)
        rows[2 + dest] ^= rows[source]
    return tuple(rows)


EDGES = tuple(tuple(INDEX[gate(s, g)] for g in range(6)) for s in STATES)


def child(state, spec):
    dest, source, shear = spec
    return gate(gate(state, 2 + 2 * dest + source), shear)


def reference_increment(q, spec):
    rows = list(q)
    rows[spec[0]] ^= 1 << spec[1]
    return tuple(rows)


def observed(state, q, mask):
    return all(not (mask & (1 << j)) or state[2 + j] == q[j] for j in range(2))


def closure(initial):
    """Multi-source Dijkstra; adapters have unit cost, initial labels may differ."""
    costs = list(initial)
    origins = list(range(96))
    heap = [(value, i) for i, value in enumerate(costs) if value < INF]
    heapify(heap)
    while heap:
        value, s = heappop(heap)
        if value != costs[s]:
            continue
        for t in EDGES[s]:
            if value + 1 < costs[t]:
                costs[t] = value + 1
                origins[t] = origins[s]
                heappush(heap, (value + 1, t))
    return tuple(costs), tuple(origins)


@lru_cache(maxsize=None)
def shortest_word(source, target, workspace_only=False):
    queue = deque([source])
    previous = {source: None}
    while queue:
        s = queue.popleft()
        if s == target:
            result = []
            while previous[s] is not None:
                s, op = previous[s]
                result.append(op)
            return tuple(reversed(result))
        for op, t in enumerate(EDGES[s][:2] if workspace_only else EDGES[s]):
            if t not in previous:
                previous[t] = (s, op)
                queue.append(t)
    raise ValueError("unreachable boundary")


def validate_instance(calls, masks):
    if not calls or len(calls) != len(masks) or masks[-1] != 3:
        raise ValueError("nonempty calls with matching masks and full final observation required")
    if any(tuple(c) not in CHILDREN for c in calls) or any(type(m) is not int or m not in (1, 2, 3) for m in masks):
        raise ValueError("outside the declared child/observation alphabet")


def solve(calls, masks, witness=False, canonical=False):
    """All boundary words, including entry preparation and final restoration."""
    validate_instance(calls, masks)
    initial = [INF] * 96
    initial[START] = 0
    costs, _ = closure(initial)
    history = []
    q = (0, 0)
    for spec, mask in zip(calls, masks):
        permutation = tuple(INDEX[child(s, spec)] for s in STATES)
        inverse = {t: s for s, t in enumerate(permutation)}
        raw = [INF] * 96
        for s, t in enumerate(permutation):
            raw[t] = costs[s]
        costs, origins = closure(raw)
        q = reference_increment(q, spec)
        costs = tuple(v if observed(s, q, mask) and (not canonical or s[:2] == (1, 2)) else INF
                      for s, v in zip(STATES, costs))
        if witness:
            history.append((origins, inverse))
    target = INDEX[(1, 2, *q)]
    value = costs[target]
    if value >= INF:
        raise ValueError("unreachable requested endpoint")
    if not witness:
        return value
    words = []
    for origins, inverse in reversed(history):
        source = origins[target]
        words.append(shortest_word(source, target))
        target = inverse[source]
    words.append(shortest_word(START, target))
    return value, tuple(reversed(words))


def restored_partition(calls, masks):
    """No entry adapters or output repair; only full workspace returns at cuts.

    Every chosen cut must have canonical data too. Observations inside an
    interval are checked even when that boundary is not a chosen cut.
    """
    validate_instance(calls, masks)
    best = None
    n = len(calls)
    for bits in range(1 << (n - 1)):
        cuts = tuple(i for i in range(n) if i == n - 1 or bits & (1 << i))
        state, q, price, valid = STATES[START], (0, 0), 0, True
        for i, (spec, mask) in enumerate(zip(calls, masks)):
            state = child(state, spec)
            q = reference_increment(q, spec)
            if i in cuts:
                if state[2:] != q:
                    valid = False
                    break
                target = (1, 2, *q)
                price += len(shortest_word(INDEX[state], INDEX[target], True))
                state = target
            if not observed(state, q, mask):
                valid = False
                break
        if valid:
            record = (price, tuple(i + 1 for i in cuts))
            if best is None or record < best:
                best = record
    if best is None:
        raise RuntimeError("the eager partition must be feasible")
    return best


def instances():
    for n in range(1, 4):
        for calls in product(CHILDREN, repeat=n):
            for prefix in product((1, 2, 3), repeat=n - 1):
                yield calls, prefix + (3,)

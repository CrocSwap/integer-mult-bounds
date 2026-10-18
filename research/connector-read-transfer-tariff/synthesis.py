"""Exact componentwise call-count frontier; fixed source order and colors.

The availability-state method is credited to PR2538. This implementation
keeps two transfer-price coordinates and does not fix minimum read counts.
"""
from collections import deque
from heapq import heappop, heappush

WORD = (0, 0, 1, 1, 2, 2)
COLORS = (1, 1, 2)
IDENTITY = (1, 2)


def need(ok, why):
    if not ok: raise ValueError(why)


def leq(a, b):
    return all(x <= y for x, y in zip(a, b))


def geometry():
    row = [0, 0]; cuts = [tuple(row)]
    for j in WORD:
        for k in range(2):
            if COLORS[j] >> k & 1: row[k] ^= 1 << j
        cuts.append(tuple(row))
    queries = [[(direction << 3) | (a if direction == 1 else b if direction == 2 else a ^ b)
                for direction in (1, 2, 3)] for a, b in cuts]
    vectors = sorted({v for qs in queries for v in qs})
    bits = [[1 << vectors.index(v) for v in qs] for qs in queries]
    return cuts, queries, vectors, bits


def reads(vectors):
    previous = {0: None}; queue = deque([0])
    while queue:
        x = queue.popleft()
        for v in vectors:
            y = x ^ v
            if y not in previous: previous[y] = x, v; queue.append(y)
    result = {}
    for target in range(1, 8):
        if target not in previous: continue
        value, path = target, []
        while value:
            value, v = previous[value]; path.append(v)
        result[target] = path
    return result


def synthesize(state_cap=20000):
    cuts, queries, vectors, bits = geometry()
    initial = (0, IDENTITY, bits[0][0])
    labels = {initial: {(0, 0)}}
    queue = [(0, 0, 0, initial)]
    parents = {}
    while queue:
        _, u, v, state = heappop(queue)
        if (u, v) not in labels[state]: continue
        cut, frame, available = state
        edges = []
        if cut < len(WORD):
            color = COLORS[WORD[cut]]
            if (frame[0]&color).bit_count() % 2 == 1 and (frame[1]&color).bit_count() % 2 == 0:
                edges.append((u, v, (cut+1, frame, available | bits[cut+1][frame[0]-1]), ['B', WORD[cut]]))
        for p in (0, 1):
            following = list(frame); following[p] ^= following[1-p]; following = tuple(following)
            edges.append((u+(p == 0), v+(p == 1), (cut, following, available | bits[cut][following[0]-1]), ['C', p]))
        for a, b, following, operation in edges:
            old = labels.get(following, set())
            if any(x <= a and y <= b for x, y in old): continue
            need(following in labels or len(labels) < state_cap, 'exact state cap exceeded')
            labels[following] = {(x, y) for x, y in old if not (a <= x and b <= y)} | {(a, b)}
            parents[(following, a, b)] = (state, u, v), operation
            heappush(queue, (a+b, a, b, following))
    terminals = {}
    for state, prices in labels.items():
        cut, frame, available = state
        if cut != len(WORD) or frame != IDENTITY: continue
        paths = reads([x for i, x in enumerate(vectors) if available >> i & 1])
        if len(paths) != 7: continue
        for u, v in sorted(prices):
            invoice = (u, v, *(len(paths[m]) for m in range(1, 8)))
            terminals.setdefault(invoice, (state, u, v, paths))
    frontier = sorted(x for x in terminals if not any(y != x and leq(y, x) for y in terminals))
    witnesses = []
    for invoice in frontier:
        state, u, v, paths = terminals[invoice]
        key = (state, u, v); skeleton = []
        while key != (initial, 0, 0):
            key, operation = parents[key]; skeleton.append(operation)
        skeleton.reverse()
        wanted = {}
        for m, path in paths.items():
            for vector in path: wanted.setdefault(vector, []).append(m)
        cut, frame, program = 0, IDENTITY, []
        for operation in skeleton + [None]:
            vector = queries[cut][frame[0]-1]
            for m in wanted.pop(vector, []): program.append(['A', m])
            if operation is None: break
            program.append(operation)
            if operation[0] == 'B': cut += 1
            else:
                frame = list(frame); frame[operation[1]] ^= frame[1-operation[1]]; frame = tuple(frame)
        need(not wanted, 'every read is placed')
        witnesses.append({'invoice': list(invoice), 'program': program})
    # Canonical physical-row image permits a code-separated frontier check.
    records = []
    for (cut, frame, available), prices in labels.items():
        for u, v in prices:
            records.append([cut, queries[cut][frame[0]-1], queries[cut][frame[1]-1],
                            sorted(x for i, x in enumerate(vectors) if available >> i & 1), u, v])
    return witnesses, sorted(records), len(labels)

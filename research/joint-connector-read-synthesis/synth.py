"""Joint minimum-read / minimum-transfer synthesis; Apache-2.0.

Prepared for ywz65 with substantial OpenAI Codex assistance.
No predecessor implementation is imported.
"""
from collections import deque
from heapq import heappop, heappush
from hashlib import sha256
import json

IDENTITY = (1, 2)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def instance(source, colors, targets):
    n = len(colors)
    need(1 <= n <= 6 and all(type(c) is int and c in (1, 2, 3) for c in colors),
         "one to six sources with nonzero binary colors required")
    need(len(source) == 2*n and all(type(j) is int and 0 <= j < n for j in source)
         and all(source.count(j) == 2 for j in range(n)), "each source occurs twice")
    need(bool(targets) and len(set(targets)) == len(targets)
         and all(type(t) is int and 0 < t < 1 << n for t in targets), "invalid targets")
    rows = [0, 0]
    cuts = [tuple(rows)]
    for j in source:
        for p in range(2):
            if colors[j] >> p & 1:
                rows[p] ^= 1 << j
        cuts.append(tuple(rows))
    queries = [[(d << n) | (a if d == 1 else b if d == 2 else a ^ b)
                for d in (1, 2, 3)] for a, b in cuts]
    vectors = sorted({v for row in queries for v in row})
    bits = [[1 << vectors.index(v) for v in row] for row in queries]
    return n, queries, vectors, bits


def read_paths(vectors, n):
    previous = {0: None}
    queue = deque([0])
    while queue:
        v = queue.popleft()
        for q in vectors:
            w = v ^ q
            if w not in previous:
                previous[w] = (v, q)
                queue.append(w)
    paths = {}
    for t in range(1 << n):
        if t not in previous:
            continue
        v, path = t, []
        while v:
            v, q = previous[v]
            path.append(q)
        paths[t] = path
    return paths


def synthesize(source, colors, targets, state_cap=250000):
    """Exact lexicographic optimum, or explicit resource rejection.

    State: source cut, physical frame rows, ever available read-vector set.
    Reads are chosen AFTER path optimization, from all visited vectors.
    """
    n, queries, vectors, bits = instance(source, colors, targets)
    optimum_reads = {t: len(p) for t, p in read_paths(vectors, n).items() if t in targets}
    need(len(optimum_reads) == len(targets), "unreachable target")
    initial = (0, IDENTITY, bits[0][0])
    best = {initial: 0}
    parent = {}
    queue = [(0, initial)]
    settled = []
    path_cache = {}
    while queue:
        bill, state = heappop(queue)
        if best[state] != bill:
            continue
        cut, frame, available = state
        if cut == len(source) and frame == IDENTITY:
            if available not in path_cache:
                path_cache[available] = read_paths(
                    [v for i, v in enumerate(vectors) if available >> i & 1], n)
            paths = path_cache[available]
            if all(t in paths and len(paths[t]) == optimum_reads[t] for t in targets):
                terminal = state
                break
        settled.append((bill, cut, *frame, available))
        edges = []
        if cut < len(source):
            color = colors[source[cut]]
            if (frame[0] & color).bit_count() % 2 == 1 and (frame[1] & color).bit_count() % 2 == 0:
                edges.append((0, (cut+1, frame, available | bits[cut+1][frame[0]-1]),
                              ["B", source[cut], 0]))
        for p in (0, 1):
            after = list(frame)
            after[p] ^= after[1-p]
            after = tuple(after)
            edges.append((1, (cut, after, available | bits[cut][after[0]-1]), ["C", p]))
        for price, following, op in edges:
            if bill + price < best.get(following, 10**9):
                need(following in best or len(best) < state_cap, "exact graph state cap exceeded")
                best[following] = bill + price
                parent[following] = state, op
                heappush(queue, (bill+price, following))
    else:
        raise ValueError("no restoring complete program")
    skeleton = []
    state = terminal
    while state != initial:
        state, op = parent[state]
        skeleton.append(op)
    skeleton.reverse()
    wanted = {}
    for t in targets:
        for vector in paths[t]:
            wanted.setdefault(vector, []).append(t)
    program = []
    cut, frame = 0, IDENTITY
    for op in skeleton + [None]:
        vector = queries[cut][frame[0]-1]
        for t in wanted.pop(vector, []):
            program.append(["A", t, 0])
        if op is not None:
            program.append(op)
            if op[0] == "B":
                cut += 1
            else:
                frame = list(frame)
                frame[op[1]] ^= frame[1-op[1]]
                frame = tuple(frame)
    need(not wanted, "unemitted read")
    lower = sorted(row for row in settled if row[0] < bill)
    layer_counts = [sum(row[0] == k for row in lower) for k in range(bill)]
    return {"source": source, "colors": colors, "targets": targets,
            "minimum_reads": {str(t): optimum_reads[t] for t in targets},
            "transfers": bill, "program": program,
            "lower_frontier_counts": layer_counts,
            "lower_frontier_sha256": sha256(json.dumps(lower, separators=(",", ":")).encode()).hexdigest(),
            "discovered_states": len(best)}

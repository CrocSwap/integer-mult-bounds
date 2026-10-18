"""Complete last-ADD graph and shortest reverse-envelope census.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
The row-subtraction recurrence follows the credited PR925/1002/281 lineage.
This implementation and the envelope census are new.
"""
from collections import Counter, defaultdict
from functools import cache
import hashlib
import json

N = 6
IDENTITY = tuple(int(i == j) for i in range(N) for j in range(N))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def positive_map(gates):
    rows = [list(IDENTITY[N*i:N*(i+1)]) for i in range(N)]
    for dst, src in gates:
        if type(dst) is not int or type(src) is not int or not (
                0 <= dst < N and 0 <= src < N and dst != src):
            raise ValueError("invalid ADD")
        rows[dst] = [a+b for a, b in zip(rows[dst], rows[src])]
    return tuple(v for row in rows for v in row)


def graph(target, limit=100_000):
    """Exhaust all last-gate removals, including dead ends.

    Each edge lowers the entry sum. There is no depth cutoff. Resource
    exhaustion raises an error and never supplies an exclusion or minimum.
    """
    if len(target) != N*N or any(type(v) is not int or v < IDENTITY[i]
                               for i, v in enumerate(target)):
        raise ValueError("expected an integral matrix >= identity")
    if type(limit) is not int or limit < 1:
        raise ValueError("invalid state limit")
    edges, choices, counts = {}, {}, {}
    unreachable = sum(target)+1

    @cache
    def distance(current):
        if distance.cache_info().misses > limit:
            raise ValueError("incomplete search: state cap")
        if current == IDENTITY:
            edges[current], choices[current], counts[current] = [], [], 1
            return 0
        outgoing = []
        for dst in range(N):
            d = N*dst
            for src in range(N):
                if dst == src:
                    continue
                s = N*src
                row = tuple(current[d+j]-current[s+j] for j in range(N))
                if any(v < int(j == dst) for j, v in enumerate(row)):
                    continue
                previous = current[:d]+row+current[d+N:]
                outgoing.append((dst, src, previous))
        edges[current] = outgoing
        best = min((1+distance(p) for _, _, p in outgoing), default=unreachable)
        best = min(best, unreachable)
        choices[current] = [(d, s, p) for d, s, p in outgoing
                            if best < unreachable and distance(p)+1 == best]
        counts[current] = sum(counts[p] for _, _, p in choices[current])
        return best

    minimum = distance(target)
    if minimum == unreachable:
        raise ValueError("no positive factorization")
    rows = [[list(s), distance(s), counts[s]] for s in sorted(edges)]
    result = {
        "minimum": minimum, "states": len(edges),
        "edges": sum(map(len, edges.values())),
        "dead_ends": sum(distance(s) == unreachable for s in edges),
        "distance_histogram": dict(sorted(Counter(str(distance(s)) for s in edges).items())),
        "shortest_programs": counts[target], "state_cap": limit, "exhausted": True,
        "graph_sha256": hashlib.sha256(canonical(rows)).hexdigest(),
    }
    # Peeled last gates are the literal cleanup in execution order. Keep its
    # positive matrix as a second state. Finish a complete distance layer
    # before propagating multiplicities through merged states.
    layer = {(target, IDENTITY): 1}
    layer_sizes, paired_edges = [1], 0
    for _ in range(minimum):
        following = defaultdict(int)
        for (state, bound), ways in layer.items():
            for dst, src, previous in choices[state]:
                d, s = N*dst, N*src
                row = tuple(bound[d+j]+bound[s+j] for j in range(N))
                following[previous, bound[:d]+row+bound[d+N:]] += ways
                paired_edges += 1
        layer = dict(following)
        layer_sizes.append(len(layer))
        if sum(layer_sizes) > limit:
            raise ValueError("incomplete reverse census: state cap")
    if any(s != IDENTITY for s, _ in layer):
        raise ValueError("shortest census has nonidentity endpoint")
    endpoints = [{"matrix": list(b), "programs": ways}
                 for (_, b), ways in sorted(layer.items())]
    if sum(e["programs"] for e in endpoints) != counts[target]:
        raise ValueError("path multiplicities disagree")
    minima = [e["matrix"] for e in endpoints if not any(
        f["matrix"] != e["matrix"] and all(a <= b for a, b in zip(f["matrix"], e["matrix"]))
        for f in endpoints)]
    result["reverse_census"] = {
        "paired_states": sum(layer_sizes), "paired_edges": paired_edges,
        "layer_sizes": layer_sizes, "distinct_endpoints": len(endpoints),
        "endpoints": endpoints, "pareto_minima": minima,
    }
    return result

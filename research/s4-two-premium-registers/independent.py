#!/usr/bin/env python3
"""Separate packed-integer, right-multiplication weighted census. Apache-2.0.

Imports no producer or predecessor implementation. Full formal coefficients,
not a nonfaithful permutation representation, decide every state equality.
"""
import hashlib
import heapq
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MASK = (1 << 24) - 1
CAPACITY = 2_000_000


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def setup():
    permutations = list(itertools.permutations(range(4)))
    numbering = {p: i for i, p in enumerate(permutations)}
    product = [[numbering[tuple(p[q[i]] for i in range(4))]
                for q in permutations] for p in permutations]
    labels = []
    for i in range(3):
        p = list(range(4))
        p[i], p[i + 1] = p[i + 1], p[i]
        labels.append(numbering[tuple(p)])
    tables = []
    for g in range(24):
        chunks = []
        for chunk in range(3):
            entries = []
            for mask in range(256):
                entries.append(sum(1 << product[chunk * 8 + bit][g]
                                   for bit in range(8) if mask >> bit & 1))
            chunks.append(entries)
        tables.append(chunks)
    calls = [(g, u, v, cost) for g, cost in zip(labels, (2, 1, 2))
             for u in range(1, 4) for v in range(1, 4)
             if (u & v).bit_count() % 2]
    require(len(calls) == 18, "independent paid alphabet")
    return permutations, product, labels, tables, calls


def shift(x, table):
    return table[0][x & 255] ^ table[1][(x >> 8) & 255] ^ table[2][x >> 16]


def right_call(state, call, tables):
    g, u, v, _ = call
    a, b = state & MASK, (state >> 24) & MASK
    c, d = (state >> 48) & MASK, state >> 72
    top = (a if u & 1 else 0) ^ (b if u & 2 else 0)
    bottom = (c if u & 1 else 0) ^ (d if u & 2 else 0)
    top ^= shift(top, tables[g])
    bottom ^= shift(bottom, tables[g])
    delta = top | (bottom << 48)
    return state ^ ((delta if v & 1 else 0) ^ (delta << 24 if v & 2 else 0))


def weighted_ball(calls, tables, radius):
    require(type(radius) is int and 0 <= radius <= 9, "bounded independent radius")
    identity = 1 | (1 << 72)
    distances = {identity: 0}
    layers = [[identity]] + [[] for _ in range(radius)]
    for cost in range(1, radius + 1):
        for call in calls:
            weight = call[3]
            if weight > cost:
                continue
            for state in layers[cost - weight]:
                candidate = right_call(state, call, tables)
                if candidate not in distances:
                    require(len(distances) < CAPACITY, "independent state capacity")
                    distances[candidate] = cost
                    layers[cost].append(candidate)
    return distances, layers


def direct_distances(product, labels):
    distances, queue = {0: 0}, [(0, 0)]
    # Each vertex is finalized once, so at most 1 + 24*3 pushes can succeed.
    for _ in range(73):
        if not queue:
            break
        distance, g = heapq.heappop(queue)
        if distance != distances[g]:
            continue
        for label, cost in zip(labels, (2, 1, 2)):
            h = product[g][label]
            if distance + cost < distances.get(h, 100):
                distances[h] = distance + cost
                heapq.heappush(queue, (distance + cost, h))
    require(not queue and len(distances) == 24, "complete bounded S4 Cayley graph")
    return distances


def lower(p):
    inversion = sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4))
    return inversion + int(p[0] != 0) + int(p[3] != 3)


def right_target(state, a, b, tables):
    return (shift(state & MASK, tables[a])
            | (shift((state >> 24) & MASK, tables[b]) << 24)
            | (shift((state >> 48) & MASK, tables[a]) << 48)
            | (shift(state >> 72, tables[b]) << 72))


def independent_census():
    permutations, product, labels, tables, calls = setup()
    direct = direct_distances(product, labels)
    distances, layers = weighted_ball(calls, tables, 9)
    queries = []
    for a in range(24):
        for b in range(a, 24):
            bill = direct[a] + direct[b]
            bound = lower(permutations[a]) + lower(permutations[b])
            if bill == bound:
                continue
            best, hits = 100, 0
            for state, cost in distances.items():
                other = distances.get(right_target(state, a, b, tables))
                if other is not None:
                    hits += 1
                    best = min(best, cost + other)
            require(best == bill, "independent shorter word or missing direct witness")
            queries.append([a, b, bill, bound, best, hits])
    return {"radius": 9, "layers": [len(layer) for layer in layers],
            "states": len(distances), "queries": queries}


def main():
    result = independent_census()
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    require(result == expected["census"], "independent complete receipt mismatch")
    digest = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
    print("PASS_S4_TWO_PREMIUM_INDEPENDENT states=971369 unordered_gaps=47 " + digest)


if __name__ == "__main__":
    main()

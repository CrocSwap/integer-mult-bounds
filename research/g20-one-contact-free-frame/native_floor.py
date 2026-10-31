#!/usr/bin/env python3
"""Exact all-native catalogue route floor, no predecessor executable imports.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Credits: Ali Romman (#5616/#5708) and the retained native geometry lineage.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
import heapq
from itertools import product
import json
from math import lcm

FRAME_SHA = '0d99fc6b8f45c03dfba5252a03dd9e7fe23be3a7593dfe15368e34da6629a654'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def row_space(rows):
    basis = {}
    for raw in rows:
        need(len(raw) == 8, 'eight rational coordinates')
        row = list(map(Fraction, raw))
        for pivot, old in sorted(basis.items()):
            coefficient = row[pivot]
            row = [a - coefficient * b for a, b in zip(row, old)]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        scale = row[pivot]
        row = [value / scale for value in row]
        for i, old in list(basis.items()):
            coefficient = old[pivot]
            basis[i] = [a - coefficient * b for a, b in zip(old, row)]
        basis[pivot] = row
    return tuple(tuple(row) for _, row in sorted(basis.items()))


def integer_rows(rows):
    out = []
    for raw in rows:
        need(len(raw) == 8, 'eight rational coordinates')
        row = list(map(Fraction, raw))
        denominator = lcm(*(x.denominator for x in row))
        out.append(tuple(int(x * denominator) for x in row))
    return tuple(out)


def native_graph(frames):
    """All proper nested edges in both directions, with exact rational admission."""
    frames = {int(key): value for key, value in frames.items()}
    dims = {key: value['dim'] for key, value in frames.items()}
    need(all(type(value) is int and 0 <= value <= 8 for value in dims.values()), 'frame dimensions')
    a = {key: integer_rows(value['A']) for key, value in frames.items()}
    b = {key: integer_rows(value['B']) for key, value in frames.items()}
    spaces = {key: row_space(value) for key, value in b.items()}
    need(len(set(spaces.values())) == len(spaces), 'distinct physical frames')
    for key in frames:
        need(len(spaces[key]) == dims[key] and len(row_space(a[key])) == 8 - dims[key], 'complement ranks')
        need(all(sum(x * y for x, y in zip(u, v)) == 0 for u in a[key] for v in b[key]), 'orthogonal complements')
    edges = {}
    for low in sorted(frames):
        for high in sorted(frames):
            rank = dims[high] - dims[low]
            if 0 < rank < 8 and all(sum(x * y for x, y in zip(u, v)) == 0 for u in b[low] for v in a[high]):
                edges[low, high] = edges[high, low] = rank
    return edges, dims


def metric(edges, nodes):
    """Exact shortest total-rank distances; verify both lower and upper witnesses."""
    adjacency = {node: [] for node in nodes}
    for (a, b), rank in edges.items():
        need(type(rank) is int and 1 <= rank <= 7 and a != b, 'native edge rank')
        adjacency[a].append((b, rank))
    distances = {}
    for origin in sorted(nodes):
        distance, parent = {origin: 0}, {}
        queue = [(0, origin)]
        while queue:
            value, a = heapq.heappop(queue)
            if value != distance[a]:
                continue
            for b, rank in adjacency[a]:
                proposed = value + rank
                if proposed < distance.get(b, 10**9):
                    distance[b], parent[b] = proposed, (a, rank)
                    heapq.heappush(queue, (proposed, b))
        need(set(distance) == set(nodes), 'connected native catalogue')
        need(distance[origin] == 0 and all(distance[b] > 0 for b in nodes if b != origin), 'separated nonnegative metric')
        # Lower witness: iterating these inequalities along any finite path bounds it.
        need(all(distance[b] <= distance[a] + rank for (a, b), rank in edges.items()), 'all edge potentials')
        # Upper witness: parents strictly decrease and terminate at the origin.
        need(all(distance[b] == distance[a] + rank and distance[a] < distance[b]
                 and edges[a, b] == rank for b, (a, rank) in parent.items()), 'shortest path attainers')
        distances[origin] = distance
    need(all(distances[a][b] == rank for (a, b), rank in edges.items()), 'every direct native edge attains its rank floor')
    return distances


def invoice(records, start, final, owned, distances, direct):
    """Complete chronology, collapsed rank floor; row-zero semantics are exact."""
    rows, state = [1 << index for index in range(len(start))], list(start)
    paid, requests, new_paid = Counter(), set(), set()

    def demand(role, target):
        source = state[role]
        if source == target:
            return
        if source is None:
            need(role in owned and not rows[role], 'whole-zero owned header')
        else:
            rank = distances[source][target]
            need(type(rank) is int and rank > 0, 'positive distinct-frame distance')
            requests.add((source, target))
            if rows[role]:
                paid[rank] += 1
                if (source, target) not in direct:
                    new_paid.add((source, target))
        state[role] = target

    for event in records:
        op, destination = event[:2]
        if op in ('INIT', 'ERASE'):
            need(destination in owned and (op != 'INIT' or not rows[destination]), 'owned scalar event')
            rows[destination], state[destination] = 0, event[2]
            continue
        need(op == 'ADD', 'scalar alphabet')
        source, frame = event[2:]
        if not rows[source]:
            continue
        for role in (destination, source):
            demand(role, frame)
        rows[destination] ^= rows[source]
    for role, frame in enumerate(final):
        if role in owned:
            need(not rows[role], 'owned final zero')
        else:
            demand(role, frame)
        state[role] = frame
    need(state == list(final), 'every final frame included')
    return paid, requests, new_paid


def signed_delta(histogram, base):
    return [[rank, histogram[rank] - base[rank]] for rank in sorted(histogram.keys() | base.keys())
            if histogram[rank] != base[rank]]


@lru_cache(None)
def _cover(available, targets):
    if not targets:
        return (), available
    target = targets[0]
    choices = []
    for group in product(*(range(min(count, (target + rank - 1) // rank) + 1)
                           for rank, count in enumerate(available, 1))):
        weight = sum(rank * count for rank, count in enumerate(group, 1))
        if weight < target:
            continue
        if any(count and weight - rank >= target for rank, count in enumerate(group, 1)):
            continue
        choices.append(group)
    choices.sort(key=lambda group: (sum(rank * count for rank, count in enumerate(group, 1)), sum(group), group))
    for group in choices:
        remaining = tuple(a - b for a, b in zip(available, group))
        tail = _cover(remaining, targets[1:])
        if tail is not None:
            groups, leftovers = tail
            return (group,) + groups, leftovers
    return None


def check_partition(delta, certificate):
    """Validate a sign proof independently of the partition search strategy."""
    need(len({rank for rank, count in delta}) == len(delta), 'unique signed rank entries')
    positive = Counter({rank: count for rank, count in delta if count > 0})
    negative = Counter({rank: -count for rank, count in delta if count < 0})
    need(all(type(rank) is int and rank > 0 and type(count) is int and count for rank, count in delta), 'typed signed ranks')
    actual_positive, actual_negative = Counter(certificate['left']), Counter()
    strict = bool(certificate['left'])
    for target, group in certificate['groups']:
        need(type(target) is int and target > 0 and group and all(type(rank) is int and rank > 0 for rank in group), 'typed partition group')
        need(sum(group) >= target, 'group dominates negative rank')
        actual_positive.update(group)
        actual_negative[target] += 1
        strict |= len(group) > 1 or sum(group) > target
    need(all(type(rank) is int and rank > 0 for rank in certificate['left']), 'typed partition leftovers')
    need(actual_positive == positive and actual_negative == negative, 'partition covers each signed occurrence exactly once')
    need(not delta or strict, 'strict sign for nonzero invoice')
    return 'strict_loss' if strict else 'zero'


def partition(delta):
    positive = Counter({rank: count for rank, count in delta if count > 0})
    negative = tuple(sorted((rank for rank, count in delta for _ in range(-count)), reverse=True))
    maximum = max(positive, default=0)
    found = _cover(tuple(positive[rank] for rank in range(1, maximum + 1)), negative)
    need(found is not None, 'no universal sign certificate found')
    groups, leftover = found
    certificate = {'groups': [[target, [rank for rank, count in enumerate(group, 1) for _ in range(count)]]
                              for target, group in zip(negative, groups)],
                   'left': [rank for rank, count in enumerate(leftover, 1) for _ in range(count)]}
    check_partition(delta, certificate)
    return certificate


def metric_digest(distances):
    rows = [[a, [[b, distances[a][b]] for b in sorted(distances[a])]] for a in sorted(distances)]
    return sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest()

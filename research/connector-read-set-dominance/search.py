"""Bounded joint connector search with continuation-safe dominance.

The read-availability graph is credited to ywz65, PR2538. This file
implements the graph afresh and adds cost-aware superset pruning.
Apache-2.0. Produced by Nick Petalas.
"""

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Problem:
    source: tuple[int, ...]
    colors: tuple[int, ...]
    targets: tuple[int, ...]
    queries: tuple[tuple[int, ...], ...]
    vectors: tuple[int, ...]
    bits: tuple[tuple[int, ...], ...]


def problem(source, colors, targets):
    n = len(colors)
    require(1 <= n <= 6, "one to six source colors required")
    require(all(type(c) is int and c in (1, 2, 3) for c in colors),
            "invalid source color")
    require(len(source) == 2*n and
            all(type(j) is int and 0 <= j < n for j in source) and
            all(source.count(j) == 2 for j in range(n)),
            "each source must occur twice")
    require(0 < len(targets) <= (1 << n)-1 and
            len(set(targets)) == len(targets) and
            all(type(t) is int and 0 < t < 1 << n for t in targets),
            "invalid targets")
    rows, queries = [0, 0], []
    for cut in range(2*n+1):
        queries.append(tuple((a << n) | value for a, value in
                             ((1, rows[0]), (2, rows[1]),
                              (3, rows[0] ^ rows[1]))))
        if cut < 2*n:
            j = source[cut]
            for p in range(2):
                if colors[j] >> p & 1:
                    rows[p] ^= 1 << j
    assert rows == [0, 0]
    vectors = tuple(sorted({v for row in queries for v in row}))
    index = {v: i for i, v in enumerate(vectors)}
    bits = tuple(tuple(1 << index[v] for v in row) for row in queries)
    return Problem(tuple(source), tuple(colors), tuple(targets),
                   tuple(queries), vectors, bits)


def read_paths(vectors, n):
    """Shortest XOR decompositions in a space with at most 256 vertices."""
    previous, queue = {0: ()}, deque([0])
    for _ in range(1 << (n+2)):
        if not queue:
            return previous
        value = queue.popleft()
        for vector in vectors:
            following = value ^ vector
            if following not in previous:
                previous[following] = previous[value] + (vector,)
                queue.append(following)
    require(not queue, "XOR closure exceeded the dimension bound")
    return previous


def edges(instance, state):
    cut, a, b, available = state
    bits = instance.bits
    result = [
        (1, (cut, a ^ b, b, available | bits[cut][(a ^ b)-1]), ("C", 0)),
        (1, (cut, a, a ^ b, available | bits[cut][a-1]), ("C", 1)),
    ]
    if cut < len(instance.source):
        j = instance.source[cut]
        color = instance.colors[j]
        if (a & color).bit_count() % 2 and not (b & color).bit_count() % 2:
            result.append((0, (cut+1, a, b,
                               available | bits[cut+1][a-1]), ("B", j)))
    return result


def dominates(first_set, first_cost, second_set, second_cost):
    return first_cost <= second_cost and first_set | second_set == first_set


def insert(bucket, available, cost):
    """Retain the cost-aware superset frontier at one fixed cut/frame."""
    if any(dominates(old, bill, available, cost)
           for old, bill in bucket.items()):
        return False, 0
    removed = [old for old, bill in bucket.items()
               if dominates(available, cost, old, bill)]
    for old in removed:
        del bucket[old]
    bucket[available] = cost
    return True, len(removed)


def explore(instance, limit, pruning, cap=250000):
    require(type(limit) is int and 0 <= limit <= 24, "invalid transfer limit")
    require(type(pruning) is bool, "invalid pruning selector")
    require(type(cap) is int and 1 <= cap <= 250000, "invalid state cap")
    start = (0, 1, 2, instance.bits[0][0])
    best, parent = {start: 0}, {}
    frontiers = {(0, 1, 2): {start[3]: 0}}
    queue, expanded, rejected, removed = [(0, start)], [0]*(limit+1), 0, 0
    for _ in range(cap*(limit+1)+1):
        if not queue:
            active = {(*key, mask): bill for key, bucket in frontiers.items()
                      for mask, bill in bucket.items()} if pruning else best
            return {"best": best, "active": active, "parent": parent,
                    "expanded": expanded, "rejected": rejected,
                    "removed": removed, "start": start}
        bill, state = heappop(queue)
        if best[state] != bill:
            continue
        if pruning and frontiers[state[:3]].get(state[3]) != bill:
            continue
        expanded[bill] += 1
        for price, following, operation in edges(instance, state):
            cost = bill + price
            if cost > limit or cost >= best.get(following, limit+1):
                continue
            bucket = frontiers.setdefault(following[:3], {})
            if pruning:
                accepted, count = insert(bucket, following[3], cost)
                if not accepted:
                    rejected += 1
                    continue
                removed += count
            require(following in best or len(best) < cap, "graph state cap exceeded")
            best[following] = cost
            parent[following] = (state, operation)
            heappush(queue, (cost, following))
    raise ValueError("bounded queue-pop budget exceeded")


def solution(instance, result):
    n = len(instance.colors)
    all_paths = read_paths(instance.vectors, n)
    require(all(t in all_paths for t in instance.targets), "unreachable target")
    minima = {t: len(all_paths[t]) for t in instance.targets}
    for state, bill in sorted(result["active"].items(), key=lambda row: (row[1], row[0])):
        if state[:3] != (len(instance.source), 1, 2):
            continue
        vectors = [v for i, v in enumerate(instance.vectors) if state[3] >> i & 1]
        paths = read_paths(vectors, n)
        if all(t in paths and len(paths[t]) == minima[t] for t in instance.targets):
            return bill, state, {t: paths[t] for t in instance.targets}, minima
    return None


def emit(instance, result, terminal, paths):
    skeleton, state = [], terminal
    for _ in range(len(result["parent"])+1):
        if state == result["start"]:
            break
        state, operation = result["parent"][state]
        skeleton.append(operation)
    else:
        raise ValueError("parent chain did not reach the initial state")
    wanted = {}
    for target, decomposition in paths.items():
        for vector in decomposition:
            wanted.setdefault(vector, []).append(target)
    program, cut, a, b = [], 0, 1, 2
    for operation in list(reversed(skeleton)) + [None]:
        vector = instance.queries[cut][a-1]
        program.extend(("A", target) for target in wanted.pop(vector, []))
        if operation is not None:
            program.append(operation)
            if operation[0] == "B":
                cut += 1
            elif operation[1] == 0:
                a ^= b
            else:
                b ^= a
    require(not wanted, "read decomposition was not emitted")
    return program

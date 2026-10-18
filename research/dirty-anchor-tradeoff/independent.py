#!/usr/bin/env python3
"""Independent exact finite check of the dirty-anchor tradeoff.

This standalone stdlib checker does not import the package verifier or any
predecessor executable. A target row is a bitmask of formal F2 coefficients of
the independent entry rows a_0,...,a_(q-1), followed by the common symbol p.
Thus equality checks the entire arbitrary-dirt affine map, not sample inputs.

Permitted transitions are row ADD A_d ^= A_s (d != s), and a common oracle
A_d ^= p. The oracle sources are read-only and outside the target rows. ADDs
and oracle calls preserve the complete set of formal source symbols.

The fixed-call search exhausts the reachable graph with at most q oracle
calls, using 0-1 BFS to minimize ADD count at each exact oracle multiplicity.
The weighted search uses positive-cost Dijkstra on the unrestricted affine
state graph, with stationary destination-only ADD and oracle tariffs.

Prepared independently by OpenAI GPT-6.1 Sol for the scoped review.
"""

from collections import deque
from heapq import heappop, heappush
from itertools import product
import json


def entry_rows(q):
    return tuple(1 << i for i in range(q))


def desired_rows(q):
    return tuple((1 << i) | (1 << q) for i in range(q))


def row_add(rows, destination, source):
    if destination == source:
        raise ValueError("row ADD requires distinct destination and source")
    result = list(rows)
    result[destination] ^= result[source]
    return tuple(result)


def common_oracle(rows, destination, q):
    result = list(rows)
    result[destination] ^= 1 << q
    return tuple(result)


def fixed_call_search(q):
    """Exhaust all affine states tagged by an exact call count from 0 to q."""
    start = (entry_rows(q), 0)
    distances = {start: 0}
    pending = deque([start])
    while pending:
        rows, calls = pending.popleft()
        cost = distances[(rows, calls)]
        if calls < q:
            for destination in range(q):
                successor = (
                    common_oracle(rows, destination, q), calls + 1
                )
                if cost < distances.get(successor, float("inf")):
                    distances[successor] = cost
                    pending.appendleft(successor)
        for destination in range(q):
            for source in range(q):
                if destination == source:
                    continue
                successor = (row_add(rows, destination, source), calls)
                if cost + 1 < distances.get(successor, float("inf")):
                    distances[successor] = cost + 1
                    pending.append(successor)

    actual = [distances.get((desired_rows(q), r)) for r in range(1, q + 1)]
    expected = [2 * (q - r) for r in range(1, q + 1)]
    if actual != expected:
        raise RuntimeError(
            f"fixed-call mismatch: q={q}, actual={actual}, expected={expected}"
        )
    if (desired_rows(q), 0) in distances:
        raise RuntimeError("the common symbol appeared without an oracle")
    expected_states = {1: 2, 2: 48, 3: 4032}[q]
    if len(distances) != expected_states:
        raise RuntimeError(
            f"reachable-state count changed: q={q}, states={len(distances)}"
        )
    return {
        "q": q,
        "reachable_tagged_states": len(distances),
        "minimum_adds_by_exact_calls": actual,
    }


def weighted_search(q, alpha, mu):
    """Exact shortest path; positive tariffs make the first goal pop final."""
    if any(price <= 0 for price in alpha + mu):
        raise ValueError("weighted search requires strictly positive tariffs")
    start = entry_rows(q)
    target = desired_rows(q)
    distances = {start: 0}
    pending = [(0, start)]
    while pending:
        cost, rows = heappop(pending)
        if cost != distances[rows]:
            continue
        if rows == target:
            return cost
        for destination in range(q):
            successor = common_oracle(rows, destination, q)
            candidate = cost + mu[destination]
            if candidate < distances.get(successor, float("inf")):
                distances[successor] = candidate
                heappush(pending, (candidate, successor))
            for source in range(q):
                if destination == source:
                    continue
                successor = row_add(rows, destination, source)
                candidate = cost + alpha[destination]
                if candidate < distances.get(successor, float("inf")):
                    distances[successor] = candidate
                    heappush(pending, (candidate, successor))
    raise RuntimeError("the desired affine map was unreachable")


def proposed_subset_price(q, alpha, mu):
    return min(
        sum(
            mu[i] if roots & (1 << i) else 2 * alpha[i]
            for i in range(q)
        )
        for roots in range(1, 1 << q)
    )


def check_weighted_tariffs():
    instances = 0
    counts = []
    for q in range(1, 4):
        count = 0
        for tariffs in product((1, 2, 3), repeat=2 * q):
            alpha, mu = tariffs[:q], tariffs[q:]
            actual = weighted_search(q, alpha, mu)
            expected = proposed_subset_price(q, alpha, mu)
            if actual != expected:
                raise RuntimeError(
                    f"weighted mismatch: q={q}, alpha={alpha}, mu={mu}, "
                    f"actual={actual}, expected={expected}"
                )
            count += 1
        counts.append(count)
        instances += count
    if counts != [9, 81, 729] or instances != 819:
        raise RuntimeError(f"weighted coverage changed: {counts}")
    return {"instances": instances, "by_q": counts, "tariff_values": [1, 2, 3]}


def check_symbolic_constructions():
    instances = 0
    for q in range(1, 13):
        for r in range(1, q + 1):
            rows = list(entry_rows(q))
            adds = 0
            calls = 0
            for root in range(r):
                leaves = [i for i in range(r, q) if (i - r) % r == root]
                for leaf in leaves:
                    rows[leaf] ^= rows[root]
                    adds += 1
                rows[root] ^= 1 << q
                calls += 1
                for leaf in leaves:
                    rows[leaf] ^= rows[root]
                    adds += 1
            if tuple(rows) != desired_rows(q):
                raise RuntimeError(f"common construction failed: q={q}, r={r}")
            if calls != r or adds != 2 * (q - r):
                raise RuntimeError(f"construction invoice failed: q={q}, r={r}")
            for i in range(q):
                rows[i] ^= 1 << (q + 1 + i)
            expected = tuple(
                (1 << i) | (1 << q) | (1 << (q + 1 + i))
                for i in range(q)
            )
            if tuple(rows) != expected:
                raise RuntimeError(f"private-symbol check failed: q={q}, r={r}")
            instances += 1
    if instances != 78:
        raise RuntimeError("symbolic construction coverage changed")
    return {"instances": instances, "q_max": 12, "private_symbols": True}


def check_restoration_control():
    """A tempting one-wave word must fail on arbitrary dirt but pass zero dirt."""
    q = 3
    rows = list(entry_rows(q))
    rows[0] ^= 1 << q
    for i in range(1, q):
        rows[i] ^= rows[0]
    if tuple(rows) == desired_rows(q):
        raise RuntimeError("one-wave corruption was not detected")
    dirt_mask = (1 << q) - 1
    specialized = [row & ~dirt_mask for row in rows]
    if specialized != [1 << q] * q:
        raise RuntimeError("zero-dirt specialization did not isolate the defect")
    return "one_wave_passes_zero_dirt_but_fails_arbitrary_dirt"


def main():
    receipt = {
        "status": "pass",
        "fixed_calls": [fixed_call_search(q) for q in range(1, 4)],
        "weighted": check_weighted_tariffs(),
        "symbolic_constructions": check_symbolic_constructions(),
        "negative_control": check_restoration_control(),
    }
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()

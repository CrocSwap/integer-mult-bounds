#!/usr/bin/env python3
"""Independent finite checks of the type-B consequence; standard library only.

No imports from the producer, predecessor implementations or their receipts.
Signed window permutations, integer Dijkstra and coefficient dictionaries are
used throughout. Written by a separate assisted agent, not a human reviewer.
"""

from __future__ import annotations

import hashlib
import heapq
import itertools
import json


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def identity(n):
    return tuple(range(1, n + 1))


def compose(p, q):
    """p after q, acting on signed coordinate labels."""
    return tuple(p[abs(x) - 1] if x > 0 else -p[abs(x) - 1] for x in q)


def generators(n):
    out = [(-1,) + tuple(range(2, n + 1))]
    for i in range(n - 1):
        p = list(identity(n))
        p[i], p[i + 1] = p[i + 1], p[i]
        out.append(tuple(p))
    return out


def windows(n):
    for p in itertools.permutations(range(1, n + 1)):
        for signs in itertools.product((1, -1), repeat=n):
            yield tuple(a * b for a, b in zip(p, signs))


def lengths(p):
    """Class counts in the B_n window formula, not a Cayley-distance lookup."""
    short = sum(x < 0 for x in p)
    long = sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p)))
    long += sum(p[i] + p[j] < 0 for i in range(len(p)) for j in range(i + 1, len(p)))
    return short, long


def roots(n):
    out = []
    for i in range(n):
        v = [0] * n
        v[i] = 1
        out.append((0, tuple(v)))
    for i in range(n):
        for j in range(i + 1, n):
            for sign in (-1, 1):
                v = [0] * n
                v[i], v[j] = sign, 1
                out.append((1, tuple(v)))
    return out


def root_counts(p):
    counts = [0, 0]
    for kind, v in roots(len(p)):
        image = [0] * len(p)
        for i, x in enumerate(p):
            image[abs(x) - 1] = v[i] * (1 if x > 0 else -1)
        last = next(x for x in reversed(image) if x)
        counts[kind] += last < 0
    return tuple(counts)


def dijkstra(n, prices):
    start = identity(n)
    gs = generators(n)
    distance = {start: 0}
    parent = {}
    queue = [(0, start)]
    while queue:
        value, p = heapq.heappop(queue)
        if distance[p] != value:
            continue
        for label, g in enumerate(gs):
            q = compose(g, p)
            new_value = value + prices[label != 0]
            if new_value < distance.get(q, 10**18):
                distance[q] = new_value
                parent[q] = (p, label)
                heapq.heappush(queue, (new_value, q))
    return distance, parent


def recover(parent, p):
    reverse = []
    while p in parent:
        p, label = parent[p]
        reverse.append(label)
    return tuple(reversed(reverse))


def matrix_identity(r):
    return tuple(1 << i for i in range(r))


def matrix_xor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def matrix_product(a, b):
    rows = []
    for mask in a:
        row = 0
        for j, source in enumerate(b):
            if (mask >> j) & 1:
                row ^= source
        rows.append(row)
    return tuple(rows)


def matrix_inverse(a):
    r = len(a)
    left, right = list(a), list(matrix_identity(r))
    for j in range(r):
        pivot = next((i for i in range(j, r) if (left[i] >> j) & 1), None)
        require(pivot is not None, "singular scalar gauge")
        left[j], left[pivot] = left[pivot], left[j]
        right[j], right[pivot] = right[pivot], right[j]
        for i in range(r):
            if i != j and ((left[i] >> j) & 1):
                left[i] ^= left[j]
                right[i] ^= right[j]
    require(tuple(left) == matrix_identity(r), "inverse elimination")
    return tuple(right)


def scalar_gauge(r):
    rows = list(matrix_identity(r))
    for i in range(1, r):
        rows[i] ^= rows[0]
    for i in range(1, r):
        rows[0] ^= rows[i]
    for i in range(r - 1):
        rows[i] ^= rows[i + 1]
    return tuple(rows)


def add_coefficient(out, g, value):
    new = matrix_xor(out.get(g, (0,) * len(value)), value)
    if any(new):
        out[g] = new
    else:
        out.pop(g, None)


def scalar_left(a, state):
    return {g: product for g, value in state.items()
            if any(product := matrix_product(a, value))}


def paid_left(n, g, state):
    out = dict(state)
    for h, value in state.items():
        change = matrix_product(n, value)
        add_coefficient(out, h, change)
        add_coefficient(out, compose(g, h), change)
    return out


def formal_product(a, b):
    out = {}
    for g, x in a.items():
        for h, y in b.items():
            add_coefficient(out, compose(g, h), matrix_product(x, y))
    return out


def diagonal(targets):
    r = len(targets)
    out = {}
    for j, g in enumerate(targets):
        rows = [0] * r
        rows[j] = 1 << j
        add_coefficient(out, g, tuple(rows))
    return out


def replay(n, r, gauge, calls, omitted=None):
    state = {identity(n): gauge}
    for k, (projector, label) in enumerate(calls):
        if k != omitted:
            state = paid_left(projector, generators(n)[label], state)
    return scalar_left(matrix_inverse(gauge), state)


def actual_columns(state, active):
    mask = (1 << active) - 1
    return {g: rows for g, value in state.items()
            if any(rows := tuple(row & mask for row in value))}


def tariff_counterexample():
    # In S3, adjacent labels are conjugate. Inconsistent prices (2,1)
    # assign 5 to aba, although the identical permutation bab costs 4.
    a, b = (2, 1, 3), (1, 3, 2)
    aba = compose(a, compose(b, a))
    bab = compose(b, compose(a, b))
    require(aba == bab, "odd braid positive control")
    require(2 + 1 + 2 > 1 + 2 + 1, "class-pricing failure control")
    require(compose(compose(a, b), compose(a, compose(b, a))) == b,
            "simple reflections really conjugate")
    return {"first_word_cost": 5, "same_endpoint_cost": 4}


def main():
    summary = []
    digest = hashlib.sha256()
    tariff_comparisons = 0
    root_comparisons = 0
    transition_checks = 0
    saved = {}
    for n in range(1, 6):
        domain = sorted(windows(n))
        for p in domain:
            require(lengths(p) == root_counts(p), f"root-class/window mismatch {p}")
            root_comparisons += 1
        for prices in ((1, 1), (2, 3), (5, 1)):
            distances, parent = dijkstra(n, prices)
            require(set(distances) == set(domain), "incomplete exact domain")
            for p in domain:
                sh, lo = lengths(p)
                require(distances[p] == prices[0] * sh + prices[1] * lo,
                        f"weighted minimum mismatch n={n} p={p} prices={prices}")
                word = recover(parent, p)
                require(sum(k == 0 for k in word) == sh, "short-root count in shortest word")
                require(sum(k != 0 for k in word) == lo, "long-root count in shortest word")
                image = identity(n)
                for k in word:
                    image = compose(generators(n)[k], image)
                require(image == p, "recovered word endpoint")
                for label, g in enumerate(generators(n)):
                    require(distances[compose(g, p)] <= distances[p] + prices[label != 0],
                            "distance transition inequality")
                    transition_checks += 1
                digest.update(json.dumps([n, prices, p, distances[p], sh, lo],
                                         separators=(",", ":")).encode())
                digest.update(b"\n")
                tariff_comparisons += 1
            summary.append({"rank": n, "prices": prices, "states": len(domain),
                            "maximum_distance": max(distances.values())})
            if prices == (2, 3):
                saved[n] = parent

    formal_cases = omitted_controls = paid_calls = dirty_controls = 0
    for n in range(2, 5):
        target_a = (-2, 1) + tuple(range(3, n + 1))
        target_b = tuple(-i for i in range(n, 0, -1))
        for dirty in (1, 2, 3):
            r = 2 + dirty
            gauge = scalar_gauge(r)
            inv_gauge = matrix_inverse(gauge)
            require(matrix_product(gauge, inv_gauge) == matrix_identity(r), "gauge inverse")
            calls = []
            has_active_dirty_coupling = False
            for j, target in enumerate((target_a, target_b)):
                e = tuple((1 << j) if i == j else 0 for i in range(r))
                projector = matrix_product(matrix_product(gauge, e), inv_gauge)
                require(matrix_product(projector, projector) == projector, "idempotent")
                nonzero = set(projector) - {0}
                require(len(nonzero) == 1, "rank-one projector")
                active_mask = 3
                if any(row & ~active_mask for row in projector[:2]) or any(row & active_mask for row in projector[2:]):
                    has_active_dirty_coupling = True
                calls.extend((projector, label) for label in recover(saved[n], target))
            require(has_active_dirty_coupling, "fixture fails to couple dirty roles")
            endpoint = diagonal((target_a, target_b) + (identity(n),) * dirty)
            actual = replay(n, r, gauge, calls)
            require(actual == endpoint, "full formal heterogeneous endpoint")
            inverse = replay(n, r, gauge, tuple(reversed(calls)))
            require(formal_product(inverse, actual) == {identity(n): matrix_identity(r)},
                    "full formal inverse restoration")
            for k in range(len(calls)):
                require(replay(n, r, gauge, calls, k) != endpoint, "omitted paid call accepted")
                omitted_controls += 1
            # A dirty-column leak is invisible when helpers are treated as clean.
            leaking = dict(endpoint)
            rows = (1 << (r - 1),) + (0,) * (r - 1)
            add_coefficient(leaking, identity(n), rows)
            require(actual_columns(leaking, 2) == actual_columns(endpoint, 2),
                    "dirty control should pass clean-only columns")
            require(leaking != endpoint, "dirty-column leak accepted")
            dirty_controls += 1
            require(replay(n, r, gauge, tuple(reversed(calls))) != endpoint,
                    "noncommuting wrong-order control is not discriminating")
            paid_calls += len(calls)
            formal_cases += 1

    result = {"status": "PASS_INDEPENDENT_COXETER_ROOT_TARIFF",
              "scope": "finite B1 through B5; corroboration, not the universal proof",
              "dijkstra_runs": len(summary), "tariff_comparisons": tariff_comparisons,
              "root_class_comparisons": root_comparisons,
              "directed_transition_checks": transition_checks,
              "distance_table_sha256": digest.hexdigest(),
              "formal_heterogeneous_dirty_cases": formal_cases,
              "formal_paid_calls": paid_calls,
              "omitted_paid_call_rejections": omitted_controls,
              "dirty_column_leak_rejections": dirty_controls,
              "wrong_order_rejections": formal_cases,
              "conjugacy_class_pricing_counterexample": tariff_counterexample(),
              "dijkstra_summary": summary, "no_new_kappa": True}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

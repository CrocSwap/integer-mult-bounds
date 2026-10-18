"""Seven-query source-XOR floor for the five-source mutable-source alphabet.

Self-contained relative to PR1898 / PR2455 / the path-lowered 789q invoice.
Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter


def need(ok, message):
    if not ok:
        raise ValueError(message)


def operators(n=5):
    edges = list(itertools.combinations(range(n), 2))
    return [
        (s, t, 1 << edges.index(tuple(sorted((s, t)))))
        for s in range(n)
        for t in range(n)
        if s != t
    ]


def component_count(n, graph):
    labels = list(range(n))
    for k, (s, t) in enumerate(itertools.combinations(range(n), 2)):
        if graph >> k & 1:
            a, b = labels[s], labels[t]
            labels = [a if c == b else c for c in labels]
    return len(set(labels))


def shear(rows, s, t):
    out = list(rows)
    out[t] ^= out[s]
    return tuple(out)


def half_layers(n, depth):
    """All (exact matrix, all-used-edge graph) states at each XOR depth."""
    layers = [{tuple(1 << j for j in range(n)): {0}}]
    for _ in range(depth):
        nxt = {}
        for rows, graphs in layers[-1].items():
            for s, t, bit in operators(n):
                nxt.setdefault(shear(rows, s, t), set()).update(g | bit for g in graphs)
        layers.append(nxt)
    return layers


def meet_census(n=5, bound=6):
    """Restored interaction graphs by XOR length via meet-in-the-middle.

    A word u followed by reverse(v) restores sources exactly when M(u)=M(v);
    its interaction graph is G(u) union G(v). Technique credited to PR2455.
    """
    layers = half_layers(n, (bound + 1) // 2)
    by_length = []
    for length in range(bound + 1):
        a, b = length // 2, (length + 1) // 2
        unions = set()
        for rows, left in layers[a].items():
            unions.update(x | y for x in left for y in layers[b].get(rows, ()))
        components = [component_count(n, g) for g in unions]
        by_length.append(
            {
                "length": length,
                "identity_graphs": len(unions),
                "connected_identity_graphs": sum(c == 1 for c in components),
                "minimum_components": min(components) if components else None,
                "query_floor_n_plus_c": (n + min(components)) if components else None,
                "graphs_sha256": hashlib.sha256(
                    json.dumps(sorted(unions), separators=(",", ":")).encode()
                ).hexdigest(),
            }
        )
    digest_rows = [[list(rows), sorted(gs)] for rows, gs in sorted(layers[-1].items())]
    return {
        "n": n,
        "bound": bound,
        "raw_half_word_counts": [(n * (n - 1)) ** k for k in range(len(layers))],
        "half_distinct_matrices": [len(layer) for layer in layers],
        "half_matrix_graph_states": [sum(len(gs) for gs in layer.values()) for layer in layers],
        "last_layer_sha256": hashlib.sha256(
            json.dumps(digest_rows, separators=(",", ":")).encode()
        ).hexdigest(),
        "by_length": by_length,
    }


def min_even_subset_R(slots):
    """Minimum total even-subset readout count on connector prefix slots."""
    need(type(slots) is tuple and slots and slots[0] == 0, "slots must start at 0")
    n = len(slots)
    best = [99] * 32
    for bits in range(1 << n):
        if bits.bit_count() % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        size = bits.bit_count()
        if size < best[value]:
            best[value] = size
    if any(best[mask] >= 99 for mask in range(1, 32)):
        return None
    return sum(best[1:])


def even_subset_reads(slots):
    n = len(slots)
    reads = {}
    for mask in range(1, 32):
        found = None
        for size in range(2, n + 1, 2):
            for subset in itertools.combinations(range(n), size):
                value = 0
                for i in subset:
                    value ^= slots[i]
                if value == mask:
                    found = subset
                    break
            if found is not None:
                break
        need(found is not None, f"mask {mask} uncovered")
        reads[mask] = found
    return reads


def path_X(closed):
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        need(delta != 0, "zero query edge")
        total += 2 * (delta.bit_count() - 1)
    return total


def path_word(closed):
    need(closed[0] == closed[-1] == 0, "path is not closed")
    slots = tuple(closed[:-1])
    reads = even_subset_reads(slots)
    word = []
    for step, point in enumerate(closed):
        word += [["R", mask] for mask, subset in reads.items() if step in subset]
        if step + 1 >= len(closed):
            break
        delta = point ^ closed[step + 1]
        need(delta != 0, "zero query edge")
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        word += [["X", j, target] for j in donors]
        word.append(["Q", target])
        word += [["X", j, target] for j in reversed(donors)]
    return word


def root_ops(word, n=5):
    out = []
    for event in word:
        kind = event[0]
        if kind == "Q":
            out.append(["B", f"x{event[1]}", "z"])
        elif kind == "R":
            out.append([f"A{event[1]}", "z", f"y{event[1]}"])
        elif kind == "X":
            out.append(["", f"x{event[1]}", f"x{event[2]}"])
        else:
            raise ValueError("unknown root operation")
    return out


def roles(n=5):
    return [f"x{j}" for j in range(n)] + [f"y{m}" for m in range(1, 1 << n)] + ["z"] + [
        f"w{j}" for j in range(3)
    ]


def interpret(operations, names, initial=None):
    state = {r: {(r,)} for r in names} if initial is None else {r: set(p) for r, p in initial.items()}
    for coefficient, source, target in operations:
        need(source in state and target in state and source != target, "invalid port")
        terms = state[source] if coefficient == "" else {(coefficient,) + term for term in state[source]}
        state[target].symmetric_difference_update(terms)
    return state


def expected(n=5):
    state = {r: {(r,)} for r in roles(n)}
    for mask in range(1, 1 << n):
        for j in range(n):
            if mask >> j & 1:
                state[f"y{mask}"].symmetric_difference_update({(f"A{mask}", "B", f"x{j}")})
    return state


def check_identity(word, n=5):
    ops = root_ops(word, n)
    result = interpret(ops, roles(n))
    need(result == expected(n), "dirty root map or restoration failed")
    need(
        interpret(ops[::-1], roles(n), result) == {r: {(r,)} for r in roles(n)},
        "root inverse failed",
    )
    return Counter(event[0] for event in word)


def invoice(word):
    counts = Counter(event[0] for event in word)
    leaves = 28 * counts["Q"] + counts["R"]
    nodes = 9 * counts["Q"]
    dispatch = len(word)
    return {
        "Q": counts["Q"],
        "R": counts["R"],
        "X": counts["X"],
        "map_leaves": leaves,
        "echo_nodes": nodes,
        "root_dispatches": dispatch,
        "borrowed_dirty_rows": 4,
        "tariff": leaves + nodes + counts["X"] + dispatch,
        "complete_prices": {"b": 38, "a": 2, "x": 2},
    }


# Credited path-lowered champion from the 789q invoice lineage (PR1898 alphabet).
CHAMPION_7 = (0, 1, 2, 6, 12, 24, 16, 0)

# Cross-check digests vs open PR2455 RESULT.json for lengths present there.
PR2455_GRAPH_DIGESTS = {
    0: "d0bca111f8628137adc4c16f123496dcdd1d590d06cb5d9acd68b39fe656fb97",
    1: "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    2: "0899bb1953bc4b09e040dbb8308c5c134c718d3cfe052d06ff64baed6062eb7f",
    3: "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    4: "546640ef872e4f0d2ebda17f74c88eeea8ccff09cb9e16de7cff2ff6735cd024",
    5: "defa9e87f9e7cc3a75d63330d451e5d1c8cd011734d1a489ec0d84af6ba68504",
    6: "163a9c5ccd357bfc55f07c641213f247253db4894f6798c6e75c94104e2be060",
}

# PR2455's published last_layer_sha256 is for half-depth 4 (bound=7). This
# package's claim only needs bound=6 (half-depth 3); per-length graph digests
# 0..6 are the load-bearing cross-check.

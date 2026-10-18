#!/usr/bin/env python3
"""Separate direct-word/column-image check; imports no primary implementation.

Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def census():
    n = 5
    calls = list(itertools.permutations(range(n), 2))
    edges = list(itertools.combinations(range(n), 2))
    layers = []
    for length in range(5):
        layer = {}
        # Direct enumeration of every word; no merging of intermediate states.
        for word in itertools.product(calls, repeat=length):
            columns = [1 << j for j in range(n)]
            graph = set()
            for donor, target in word:
                columns = [c ^ (((c >> donor) & 1) << target) for c in columns]
                graph.add(tuple(sorted((donor, target))))
            layer.setdefault(tuple(columns), set()).add(frozenset(graph))
        layers.append(layer)
    result = []
    for length in range(8):
        a, b = length // 2, (length + 1) // 2
        graphs = set()
        for matrix, ls in layers[a].items():
            for left in ls:
                for right in layers[b].get(matrix, ()):
                    graphs.add(left | right)
        component_counts = []
        encoded = []
        for graph in graphs:
            unseen = set(range(n))
            count = 0
            while unseen:
                count += 1
                stack = [unseen.pop()]
                while stack:
                    u = stack.pop()
                    for x, y in graph:
                        v = y if x == u else x if y == u else None
                        if v in unseen:
                            unseen.remove(v)
                            stack.append(v)
            component_counts.append(count)
            encoded.append(sum(1 << edges.index(edge) for edge in graph))
        result.append({"length": length, "identity_graphs": len(graphs),
                       "connected_identity_graphs": component_counts.count(1),
                       "minimum_components": min(component_counts, default=None),
                       "graphs_sha256": hashlib.sha256(json.dumps(sorted(encoded), separators=(",", ":")).encode()).hexdigest()})
    return result, [len(layer) for layer in layers], [sum(map(len, layer.values())) for layer in layers]


def multiply(matrix, value):
    return sum(((row & value).bit_count() % 2) << i for i, row in enumerate(matrix))


def execute(word, state, b, maps):
    out = state[:]
    for event in word:
        if event[0] == "X":
            out[event[2]] ^= out[event[1]]
        elif event[0] == "Q":
            out[5] ^= multiply(b, out[event[1]])
        elif event[0] == "R":
            m = event[1]
            out[5+m] ^= multiply(maps[m], out[5])
        else:
            raise ValueError("unknown event")
    return out


def dirty_checks(word):
    executions = 0
    for dimension in (1, 2, 3):
        limit = (1 << dimension) - 1
        banks = [([1 << j for j in range(dimension)],
                  {m: [1 << j for j in range(dimension)] for m in range(1,32)}),
                 ([(3*j + 3) & limit for j in range(dimension)],
                  {m: [(m*(j+1)+j+1) & limit for j in range(dimension)] for m in range(1,32)})]
        for b, maps in banks:
            inputs = []
            for role in range(37):
                for bit in range(dimension):
                    state = [0] * 37
                    state[role] = 1 << bit
                    inputs.append(state)
            inputs.append([(j*3+1)&limit for j in range(37)])
            for state in inputs:
                expected = state[:]
                for m in range(1,32):
                    source = 0
                    for j in range(5):
                        if m >> j & 1:
                            source ^= state[j]
                    expected[5+m] ^= multiply(maps[m], multiply(b, source))
                for program in (word, list(reversed(word))):
                    need(execute(program, state, b, maps) == expected, "dirty dense map mismatch")
                    executions += 1
    return executions


def main():
    receipt = json.loads((HERE / "RESULT.json").read_text())
    by_length, matrices, states = census()
    need(by_length == receipt["census"]["by_length"], "independent identity-graph census mismatch")
    need(matrices == receipt["census"]["half_distinct_matrices"], "matrix count mismatch")
    need(states == receipt["census"]["half_matrix_graph_states"], "matrix/graph count mismatch")
    need(all(r["connected_identity_graphs"] == 0 for r in by_length), "short connected identity exists")
    word = receipt["root_word"]
    need({k: sum(e[0] == k for e in word) for k in ("Q","R","X")} == {"Q":6,"R":96,"X":8}, "invoice mismatch")
    executions = dirty_checks(word)
    need(6*38 + 96*2 + 8*2 == receipt["abstract_tariff_38_2_2"], "tariff mismatch")
    # An actual basis witness rejects omitted source restoration, despite correct outputs.
    initial = [0]*37
    initial[1] = 1
    maps = {m: [1] for m in range(1,32)}
    good, bad = execute(word, initial, [1], maps), execute(word[:-1], initial, [1], maps)
    need(good[6:] == bad[6:] and good != bad, "source restoration control failed")
    print(f"PASS_SIX_QUERY_COLUMNS raw_half_words=168421 dirty_executions={executions} min_x=8")


if __name__ == "__main__":
    main()

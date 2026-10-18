#!/usr/bin/env python3
"""Optional bounded discovery replay; certificate verification needs no solver.

Uses NetworkX 3.6.1's Edmonds/Galil matching implementation without modifying it.
Prepared for Gareth Davidson (@bitplane), with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import inspect
from pathlib import Path
import random
import runpy
import sys

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))
need = C["need"]
SOURCE_SHA = "41930910962d79c5da2da89788ead7819730daccb2858d72df3df7c55d893ee1"


def suffix(word, values):
    values = list(values)
    for section in ("A", "scatter", "B", "C"):
        if section == "scatter":
            for i, row in enumerate(word["scatter"]):
                values[word["v"] + i] += sum(values[word["ret"][j]] for j in row)
        else:
            for _, d, sources in word[section]:
                values[d] += sum(values[s] for s in sources)
    return values


def run(root, output):
    import networkx as nx
    C["pins"](root)
    need(nx.__version__ == "3.6.1", "nomination requires NetworkX 3.6.1")
    source_hash = hashlib.sha256(inspect.getsource(nx.algorithms.matching.max_weight_matching).encode()).hexdigest()
    need(source_hash == SOURCE_SHA, "matching implementation source changed")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    build = C["module"]("matching_builder", C["HERE"] / "build.py")
    parent = C["load"](C["HERE"] / "vendor/pr915/candidate.json.gz")
    v, helpers, count = parent["v"], parent["R"], 306
    n = 2 * v + helpers
    columns = [0] * helpers
    for _, d, sources in parent["D"][count:count + v]:
        for s in sources:
            columns[s - 2 * v] ^= 1 << (d - v)
    tail = suffix(parent, [1] * n)
    pivot = max(list(range(v)) + list(range(2 * v, n)), key=lambda j: tail[j])
    cost = []
    for j in range(helpers):
        vector = [0] * n
        vector[2 * v + j] = 1
        cost.append(suffix(parent, vector)[pivot])
    edges = []
    for a in range(helpers):
        for b in range(a + 1, helpers):
            distance = (columns[a] ^ columns[b]).bit_count()
            ab, ba = columns[b].bit_count() - distance - 2, columns[a].bit_count() - distance - 2
            if max(ab, ba) > 0:
                edges.append((a, b, ab, ba))

    def charges(pairs):
        word = build.assemble(parent, pairs)
        forward, backward = build.positive(word), build.positive(word, True)
        total = 6220 + sum(len(g[2]) for g in word["D"])
        local, nine = 64 * forward ** 3 * backward ** 2, (1 << 18) * forward ** 5 * backward ** 4
        return dict(ADDs=total, gain=13208 - total, F=forward, B=backward,
                    payload_bits=local.bit_length(), nine_bits=nine.bit_length(),
                    admitted=local < 1 << 104 and nine < 1 << 192)

    nominations, primary_dual = [], None
    multiplier = 1 + sum(cost)
    for variant in ("lexicographic", "seed4", "forward_proxy"):
        rng = random.Random(4)
        nodes, ordered_edges = list(range(helpers)), list(edges)
        if variant != "lexicographic":
            rng.shuffle(nodes)
            rng.shuffle(ordered_edges)
        graph, orientation = nx.Graph(), {}
        graph.add_nodes_from(nodes)
        for a, b, ab, ba in ordered_edges:
            if ab > ba:
                pair = (a, b)
            elif ba > ab:
                pair = (b, a)
            elif variant == "lexicographic":
                pair = (a, b)
            elif variant == "seed4":
                pair = (a, b) if rng.getrandbits(1) else (b, a)
            else:
                pair = min(((a, b), (b, a)), key=lambda p: (cost[p[0]], p))
            orientation[a, b] = pair
            weight = max(ab, ba)
            if variant == "forward_proxy":
                weight = weight * multiplier - cost[pair[0]]
            graph.add_edge(a, b, weight=weight)
        captured = {}

        def profile(frame, event, argument):
            # Source-hashed discovery introspection only. The default verifier
            # independently validates these plain integers, not solver internals.
            if event == "return" and frame.f_code.co_name == "max_weight_matching" and "dualvar" in frame.f_locals:
                local = frame.f_locals
                captured["vertex_prices_2"] = [local["dualvar"][i] for i in range(helpers)]
                captured["odd_sets"] = [dict(vertices=sorted(b.leaves()), price_2=2 * z)
                                         for b, z in local["blossomdual"].items() if z]

        previous = sys.getprofile()
        sys.setprofile(profile)
        try:
            matching = nx.max_weight_matching(graph)
        finally:
            sys.setprofile(previous)
        pairs = sorted(orientation[min(a, b), max(a, b)] for a, b in matching)
        nominations.append(dict(variant=variant, pairs=pairs, **charges(pairs)))
        need(captured, "matching dual was not captured")
        if variant == "lexicographic":
            primary_dual = captured
        print(variant, "pairs", len(pairs), "ADDs", nominations[-1]["ADDs"], flush=True)

    trials, best = [], None
    for ni, nomination in enumerate(nominations):
        for removed in range(-1, len(nomination["pairs"])):
            pairs = [pair for i, pair in enumerate(nomination["pairs"]) if i != removed]
            bill = charges(pairs)
            row = dict(nomination=ni, removed_index=removed, **bill)
            trials.append(row)
            key = (bill["ADDs"], bill["nine_bits"], bill["F"], bill["B"], ni, removed)
            if bill["admitted"] and (best is None or key < best[0]):
                best = key, pairs, row
    need(best is not None, "no admitted candidate in bounded family")
    result = dict(networkx=nx.__version__, seed=4, networkx_matching_source_sha256=source_hash,
                  positive_edges=len(edges), proxy_pivot=pivot, proxy_cost=cost,
                  lexicographic_multiplier=multiplier, nominations=nominations, primary_dual=primary_dual,
                  trials=trials, selected=best[2], selected_pairs=best[1])
    C["write"](output / "NOMINATION.json", result)
    need(C["canonical"](result) == C["canonical"](C["load"](C["HERE"] / "NOMINATION.json")),
         "nomination differs from committed record")
    print("PASS_R439_MATCHING_NOMINATION: three optima; 598 deletions; 601 priced words", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=C["ROOT"])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.source_root, args.output)

#!/usr/bin/env python3
"""Optional three-objective discovery; default verification needs no NetworkX.

Edmonds/Galil dual capture follows Gareth Davidson's PR941 technique, applied
to the different, unchanged PR589 target basis. Apache-2.0; @CubeJerry/Codex.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("copyshare_core", HERE / "core.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def nominate():
    import networkx as nx
    C.need(nx.__version__ == "3.6.1", "requires NetworkX 3.6.1")
    digest = hashlib.sha256(inspect.getsource(nx.max_weight_matching).encode()).hexdigest()
    C.need(digest == "41930910962d79c5da2da89788ead7819730daccb2858d72df3df7c55d893ee1",
           "matching source digest")
    word = C.load_word()
    col = C.columns(word)
    nodes = sorted(col)
    edges = []
    for i, a in enumerate(nodes):
        for b in nodes[i+1:]:
            distance = (col[a] ^ col[b]).bit_count()
            ab = col[b].bit_count() - distance - 2
            ba = col[a].bit_count() - distance - 2
            if max(ab, ba) > 0:
                edges.append((a, b, ab, ba))
    n = 2*word["v"] + word["R"]
    tail = C.suffix(word, [1]*n)
    # Targets receive a D-dependent term; choose the maximal source/helper
    # endpoint, as in PR941. This is a proxy, not an asserted exact F objective.
    pivot = max(list(range(word["v"])) + nodes, key=lambda j: tail[j])
    cost = {}
    for a in nodes:
        e = [0]*n
        e[a] = 1
        cost[a] = C.suffix(word, e)[pivot]
    multiplier = 1 + sum(cost.values())
    nominations = []
    primary_dual = None
    for variant in ("sorted", "seed3", "forward_proxy"):
        rng = random.Random(3)
        nn, ee = list(nodes), list(edges)
        if variant != "sorted":
            rng.shuffle(nn)
            rng.shuffle(ee)
        graph, orientations = nx.Graph(), {}
        graph.add_nodes_from(nn)
        for a, b, ab, ba in ee:
            if ab != ba:
                pair = (a, b) if ab > ba else (b, a)
            elif variant == "forward_proxy":
                pair = min(((a, b), (b, a)), key=lambda p: (cost[p[0]], p))
            elif variant == "seed3":
                pair = (a, b) if rng.getrandbits(1) else (b, a)
            else:
                pair = (a, b)
            orientations[a, b] = pair
            w = max(ab, ba)
            if variant == "forward_proxy":
                w = multiplier*w - cost[pair[0]]
            graph.add_edge(a, b, weight=w)
        capture = {}

        def profile(frame, event, arg):
            if event == "return" and frame.f_code.co_name == "max_weight_matching" and "dualvar" in frame.f_locals:
                f = frame.f_locals
                capture["vertex_prices_2"] = [[i, f["dualvar"][i]] for i in nodes]
                capture["odd_sets"] = sorted(
                    [{"vertices": sorted(b.leaves()), "price_2": 2*z}
                     for b, z in f["blossomdual"].items() if z],
                    key=lambda x: x["vertices"])

        previous = sys.getprofile()
        sys.setprofile(profile)
        try:
            matching = nx.max_weight_matching(graph)
        finally:
            sys.setprofile(previous)
        C.need(bool(capture), "missing captured dual")
        pairs = [list(p) for p in sorted(orientations[min(a,b), max(a,b)] for a,b in matching)]
        saving = sum(col[b].bit_count() - (col[a]^col[b]).bit_count() - 2 for a,b in pairs)
        bill = C.invoice(C.construct(word, pairs))
        nominations.append({"variant": variant, "pairs": pairs, "saving": saving, "invoice": bill})
        if variant == "sorted":
            primary_dual = capture
        print(variant, "pairs", len(pairs), "saving", saving, bill, flush=True)
    feasible = [x for x in nominations if x["invoice"]["local_guard"] and x["invoice"]["nine_stage_guard"]]
    C.need(feasible, "no precision-feasible nomination; stop")
    selected = min(feasible, key=lambda x: (-x["saving"], x["invoice"]["F"], x["invoice"]["B"], x["variant"]))
    return {"networkx": nx.__version__, "source_sha256": digest, "assignment_seed": 3,
            "nodes": len(nodes), "positive_unordered_edges": len(edges),
            "proxy_pivot": pivot, "proxy_costs": [[a,cost[a]] for a in nodes],
            "proxy_multiplier": multiplier, "nominations": nominations,
            "primary_dual": primary_dual, "selected": selected["variant"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new file; refuses overwrite")
    args = parser.parse_args()
    C.need(not args.output.exists(), "output already exists")
    result = nominate()
    with args.output.open("x") as f:
        f.write(json.dumps(result, indent=2) + "\n")
    frozen = json.loads((HERE / "MATCHING.json").read_text())
    C.need(result == frozen, "discovery differs from frozen MATCHING.json")
    print("PASS_R439_COPYSHARE_NOMINATION three_optima=6372")

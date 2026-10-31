#!/usr/bin/env python3
"""Independent shortest-path audit of the frozen G20 route graph.

Prepared for @CubeJerry with substantial OpenAI Codex assistance by worker B.
Apache-2.0. No author or predecessor implementation is imported.
"""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from hashlib import sha256
from heapq import heappop, heappush
import json
from pathlib import Path

SOURCE_SHA256 = "f4dd58b78121040b1f054c0f7a626b25f6ef8d39f3de044d3456ea7dea8a6a5e"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check(routes):
    adjacency, incoming, nodes = defaultdict(list), Counter(), set()
    for key, route in routes.items():
        need(len(route) == 1, "singleton route")
        a, b, rank = route[0]
        need(all(type(x) is int for x in (a, b, rank)), "integer edge")
        need(key == str(a) + ":" + str(b) and a != b and rank > 0, "edge contract")
        adjacency[a].append((b, rank))
        incoming[b] += 1
        nodes.update((a, b))
    roots = sorted(v for v in nodes if not incoming[v])
    need(roots == [1], "unique root")

    def distances(source):
        result, queue = {source: 0}, [(0, source)]
        while queue:
            cost, current = heappop(queue)
            if result[current] != cost:
                continue
            for target, weight in adjacency[current]:
                candidate = cost + weight
                if candidate < result.get(target, 10**9):
                    result[target] = candidate
                    heappush(queue, (candidate, target))
        return result

    level = distances(1)
    need(set(level) == nodes, "root reaches all vertices")
    for source, edges in adjacency.items():
        for target, rank in edges:
            need(level[target] - level[source] == rank, "potential edge identity")
    positive_pairs, maximum_hops = 0, 0
    order = sorted(nodes, key=lambda v: level[v])
    for source in sorted(nodes):
        shortest = distances(source)
        for target, value in shortest.items():
            need(value == level[target] - level[source], "all-pairs telescoping distance")
            positive_pairs += target != source
        longest = {source: 0}
        for current in order:
            if current in longest:
                for target, _rank in adjacency[current]:
                    longest[target] = max(longest.get(target, 0), longest[current] + 1)
        maximum_hops = max(maximum_hops, max(longest.values()))
    return {"nodes": len(nodes), "edges": len(routes), "root": roots[0],
            "levels": sorted(set(level.values())),
            "level_counts": dict(sorted(Counter(level.values()).items())),
            "positive_reachable_pairs": positive_pairs,
            "all_pairs_including_identity": positive_pairs + len(nodes),
            "maximum_route_hops": maximum_hops}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", type=Path, required=True)
    args = parser.parse_args()
    raw = args.paths.read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_SHA256, "frozen source bytes")
    routes = json.loads(raw)
    result = check(routes)
    need(result["nodes"] == 636 and result["edges"] == 2369, "graph size")
    need(result["positive_reachable_pairs"] == 23560, "reachable pair count")
    need(result["maximum_route_hops"] == 6, "longest path")
    need(result["levels"] == [0, 1, 2, 4, 6, 7, 8], "level values")
    first = next(iter(routes))
    mutants = []
    bad = deepcopy(routes); bad[first][0][2] += 1; mutants.append(("rank change", bad))
    bad = deepcopy(routes); a, b, r = bad[first][0]; bad[str(b)+":"+str(a)] = [[b,a,r]]; mutants.append(("back edge", bad))
    bad = deepcopy(routes); bad[first][0][2] = 0; mutants.append(("zero rank", bad))
    bad = deepcopy(routes); bad[first].append(bad[first][0][:]); mutants.append(("nonsingleton", bad))
    for label, mutant in mutants:
        try:
            check(mutant)
        except ValueError:
            continue
        raise ValueError("accepted negative control: " + label)
    result["negative_controls"] = [label for label, _ in mutants]
    result["method"] = "636 independent Dijkstra searches and a separate DAG longest-hop pass"
    print(json.dumps(result, sort_keys=True))
    print("PASS_INDEPENDENT_G20_ROUTE_POTENTIAL")


if __name__ == "__main__":
    main()

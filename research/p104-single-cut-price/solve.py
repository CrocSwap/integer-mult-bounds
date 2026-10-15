"""Optional exact min-cost optimizer; acceptance uses a separate certificate check.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import heapq
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p104_price_model", HERE / "model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


def optimize(graph, requested=104):
    n = len(graph.labels)
    adj = [[] for _ in range(n)]
    capacity, target, costs = [], [], []
    for u, v, cap, price, _ in graph.edges:
        a = len(target)
        adj[u].append(a)
        adj[v].append(a + 1)
        target.extend((v, u))
        capacity.extend((cap, 0))
        costs.extend((price, -price))
    potential = [0] * n
    value = cost = 0
    frontier = [[0, 0]]
    while value < requested:
        dist = [None] * n
        prev = [-1] * n
        dist[0] = 0
        queue = [(0, 0)]
        while queue:
            du, u = heapq.heappop(queue)
            if dist[u] != du:
                continue
            for a in adj[u]:
                if not capacity[a]:
                    continue
                v = target[a]
                rc = costs[a] + potential[u] - potential[v]
                model.need(rc >= 0, "optimizer reduced cost")
                dv = du + rc
                if dist[v] is None or dv < dist[v]:
                    dist[v] = dv
                    prev[v] = a
                    heapq.heappush(queue, (dv, v))
        if dist[1] is None:
            break
        far = max(x for x in dist if x is not None)
        potential = [p + (far if d is None else d) for p, d in zip(potential, dist)]
        u = 1
        amount = requested - value
        path = []
        while u:
            a = prev[u]
            model.need(a >= 0, "optimizer predecessor")
            path.append(a)
            amount = min(amount, capacity[a])
            u = target[a ^ 1]
        unit_cost = sum(costs[a] for a in path)
        for a in path:
            capacity[a] -= amount
            capacity[a ^ 1] += amount
        for _ in range(amount):
            value += 1
            cost += unit_cost
            frontier.append([value, cost])
    flow = [e[2] - capacity[2 * i] for i, e in enumerate(graph.edges)]
    return {"value": value, "cost": cost, "flow": flow, "potential": potential,
            "frontier": frontier, "graph_sha256": graph.fingerprint()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, required=True, help="new certificate path; refuses overwrite")
    args = parser.parse_args()
    w = model.load_source()
    graph = model.build(w)
    solution = optimize(graph)
    baseline = optimize(model.build(w, paid=False))
    result = {"schema_version": 1, "source_sha256": model.SOURCE_HASH,
              "facts": graph.facts, "baseline": baseline, "paid": solution}
    with args.write.open("x") as f:
        json.dump(result, f, sort_keys=True, separators=(",", ":"))
        f.write("\n")
    print(f"GENERATED_P104_SINGLE_CUT_PRICE flow={solution['value']} cost={solution['cost']} "
          f"baseline={baseline['value']} nodes={len(graph.labels)} edges={len(graph.edges)}")


if __name__ == "__main__":
    main()

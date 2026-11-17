"""Exact acquisition for binary edge queries on a simple cactus graph.

Produced by Nick Petalas. Apache-2.0.
"""
import argparse
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(n, edges, costs, targets):
    require(type(n) is int and 1 <= n <= 128, "vertex capacity: 1..128")
    require(isinstance(edges, (list, tuple)) and len(edges) <= 192,
            "edge capacity: at most 192")
    require(isinstance(costs, (list, tuple)) and len(costs) == len(edges),
            "one price per edge required")
    require(isinstance(targets, (list, tuple)) and len(targets) <= 128,
            "target capacity: at most 128")
    seen = set()
    for edge in edges:
        require(isinstance(edge, (list, tuple)) and len(edge) == 2,
                "edge must have two endpoints")
        u, v = edge
        require(type(u) is int and type(v) is int and 0 <= u < v < n,
                "edges require canonical distinct endpoints")
        require((u, v) not in seen, "duplicate edge")
        seen.add((u, v))
    require(all(type(c) is int and 0 <= c <= 10**12 for c in costs),
            "integer prices must be in 0..10^12")
    require(all(type(t) is int and 0 <= t < 1 << n for t in targets),
            "target outside vertex coordinates")


def forest(n, edges):
    adjacency = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adjacency[u].append((v, i))
        adjacency[v].append((u, i))
    parent, parent_edge, depth = [-1] * n, [-1] * n, [0] * n
    order, roots, tree = [], [], set()
    for root in range(n):
        if parent[root] != -1:
            continue
        parent[root] = root
        roots.append(root)
        queue = [root]
        for v in queue:
            order.append(v)
            for w, edge in adjacency[v]:
                if parent[w] == -1:
                    parent[w], parent_edge[w] = v, edge
                    depth[w] = depth[v] + 1
                    tree.add(edge)
                    queue.append(w)
    require(len(order) == n, "forest missed a vertex")
    return parent, parent_edge, depth, order, roots, tree


def cycle_blocks(edges, parent, parent_edge, depth, tree):
    cycles, used = [], set()
    for edge, (u, v) in enumerate(edges):
        if edge in tree:
            continue
        block = [edge]
        for _ in range(len(parent)):
            if u == v:
                break
            if depth[u] < depth[v]:
                u, v = v, u
            block.append(parent_edge[u])
            u = parent[u]
        require(u == v, "tree path did not terminate")
        require(len(block) >= 3 and not used.intersection(block),
                "graph is not a cactus")
        used.update(block)
        cycles.append(tuple(sorted(block)))
    return tuple(cycles), used


def base_rows(n, targets, edges, parent, parent_edge, order, roots):
    values = [sum(((t >> v) & 1) << j for j, t in enumerate(targets))
              for v in range(n)]
    rows = [0] * len(edges)
    for v in reversed(order):
        if parent[v] != v:
            rows[parent_edge[v]] = values[v]
            values[parent[v]] ^= values[v]
    require(all(values[root] == 0 for root in roots),
            "target has odd parity on a connected component")
    return tuple(rows)


def bucket_choice(block, rows, costs):
    buckets = {}
    for edge in block:
        label = rows[edge]
        buckets[label] = buckets.get(label, 0) + costs[edge]
    shift = min(buckets, key=lambda z: (-buckets[z], z))
    return shift, buckets[shift]


def optimize(n, edges, costs, targets):
    validate(n, edges, costs, targets)
    parent, parent_edge, depth, order, roots, tree = forest(n, edges)
    cycles, cyclic_edges = cycle_blocks(edges, parent, parent_edge, depth, tree)
    rows = base_rows(n, targets, edges, parent, parent_edge, order, roots)
    chosen, shifts, savings = list(rows), [], []
    for block in cycles:
        shift, saving = bucket_choice(block, rows, costs)
        shifts.append(shift)
        savings.append(saving)
        for edge in block:
            chosen[edge] ^= shift
    selected = [i for i, row in enumerate(chosen) if row]
    bridge_bill = sum(costs[i] for i, row in enumerate(rows)
                      if i not in cyclic_edges and row)
    formula = bridge_bill + sum(sum(costs[i] for i in block) - saving
                                for block, saving in zip(cycles, savings))
    bill = sum(costs[i] for i in selected)
    require(bill == formula, "cost decomposition failed")
    result = {"cost": bill, "selected": selected, "rows": chosen,
              "base_rows": list(rows), "cycles": [list(c) for c in cycles],
              "shifts": shifts, "savings": savings, "bridge_bill": bridge_bill}
    check(n, edges, costs, targets, result)
    return result


def check(n, edges, costs, targets, result):
    """Check a saved optimum certificate, without optimizer or price sorting."""
    validate(n, edges, costs, targets)
    require(isinstance(result, dict) and set(result) == {
        "cost", "selected", "rows", "base_rows", "cycles", "shifts",
        "savings", "bridge_bill"}, "certificate fields")
    parent, pe, depth, order, roots, tree = forest(n, edges)
    cycles, cyclic_edges = cycle_blocks(edges, parent, pe, depth, tree)
    require(result["cycles"] == [list(c) for c in cycles], "cycle certificate")
    base = base_rows(n, targets, edges, parent, pe, order, roots)
    require(result["base_rows"] == list(base), "base coefficient certificate")
    rows, shifts, savings = result["rows"], result["shifts"], result["savings"]
    require(isinstance(rows, list) and len(rows) == len(edges), "row count")
    require(all(type(r) is int and 0 <= r < 1 << len(targets) for r in rows),
            "coefficient row domain")
    require(isinstance(shifts, list) and len(shifts) == len(cycles), "shift count")
    require(isinstance(savings, list) and len(savings) == len(cycles), "saving count")
    for k, block in enumerate(cycles):
        z = shifts[k]
        require(type(z) is int and 0 <= z < 1 << len(targets), "shift domain")
        require(all(rows[i] == base[i] ^ z for i in block), "cycle shift")
        earned = sum(costs[i] for i in block if base[i] == z)
        require(type(savings[k]) is int and savings[k] == earned, "saving value")
        for label in {base[i] for i in block}:
            require(earned >= sum(costs[i] for i in block if base[i] == label),
                    "nonmaximal saving bucket")
    require(all(rows[i] == base[i] for i in range(len(edges))
                if i not in cyclic_edges), "bridge coefficient")
    selected = [i for i, row in enumerate(rows) if row]
    require(result["selected"] == selected, "selected support")
    require(type(result["cost"]) is int and result["cost"] ==
            sum(costs[i] for i in selected), "total bill")
    bridge_bill = sum(costs[i] for i in range(len(edges))
                      if i not in cyclic_edges and base[i])
    require(type(result["bridge_bill"]) is int and
            result["bridge_bill"] == bridge_bill, "bridge bill")
    delivered = [0] * len(targets)
    for edge, (u, v) in enumerate(edges):
        for j in range(len(targets)):
            if rows[edge] >> j & 1:
                delivered[j] ^= (1 << u) | (1 << v)
    require(delivered == list(targets), "target reconstruction")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    require(args.problem.stat().st_size <= 131072, "problem file capacity")
    problem = json.loads(args.problem.read_text())
    require(isinstance(problem, dict) and set(problem) ==
            {"vertices", "edges", "costs", "targets"}, "problem fields")
    values = [problem[k] for k in ("vertices", "edges", "costs", "targets")]
    if args.check:
        require(args.check.stat().st_size <= 131072, "certificate file capacity")
        check(*values, json.loads(args.check.read_text()))
        print("PASS_CACTUS_PARTIAL_QUERY_CERTIFICATE")
    else:
        print(json.dumps(optimize(*values), sort_keys=True))


if __name__ == "__main__":
    main()

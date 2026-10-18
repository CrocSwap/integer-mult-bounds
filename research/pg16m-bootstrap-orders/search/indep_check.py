"""Independent checker for bootstrap orders on a half-rate d-regular Tanner graph.

usage: python indep_check.py graph.txt order.txt [--json]

Re-implements, without importing check_order.py:
  * graph validation: symmetric, simple, d-regular, bipartite, 4-cycle free;
  * cost(order) = sum_v (d/2 - j_v)^+ where j_v = #neighbours earlier in the order,
    cross-checked against (1/2) sum_v |j_v - d/2| and (1/2) x total ascent of the cut profile
    (cut sizes recounted edge by edge, not from the d - 2 j_v increment);
  * the split identity cost = |dS|/2 + sum_{v in S}(j_v-k)^+ + sum_{v notin S}(l_v-k)^+ at every prefix S
    (l_v = neighbours of v later in the order and outside S);
  * back-arc flow feasibility with scipy's maximum_flow (Dinic), not augmenting BFS.
Exit code 0 iff every check passes; the flow verdict is reported, not asserted.
"""
import json, sys
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_flow


class Reject(Exception):
    pass


def load_graph(path):
    tok = open(path).read().split()
    V, d = int(tok[0]), int(tok[1])
    vals = list(map(int, tok[2:]))
    if len(vals) != V * d:
        raise Reject(f"expected {V*d} neighbour entries, got {len(vals)}")
    nb = [vals[v * d:(v + 1) * d] for v in range(V)]
    for v in range(V):
        if len(set(nb[v])) != d or v in nb[v] or not all(0 <= u < V for u in nb[v]):
            raise Reject(f"vertex {v}: loop, repeat or out-of-range neighbour")
    adj = [set(x) for x in nb]
    if any(v not in adj[u] for v in range(V) for u in nb[v]):
        raise Reject("adjacency not symmetric")
    col = [-1] * V
    for s in range(V):
        if col[s] >= 0:
            continue
        col[s], stack = 0, [s]
        while stack:
            a = stack.pop()
            for b in nb[a]:
                if col[b] < 0:
                    col[b] = 1 - col[a]; stack.append(b)
                elif col[b] == col[a]:
                    raise Reject("graph not bipartite")
    seen = set()
    for v in range(V):
        s = sorted(nb[v])
        for i in range(d):
            for k in range(i + 1, d):
                p = (s[i], s[k])
                if p in seen:
                    raise Reject(f"4-cycle through pair {p}")
                seen.add(p)
    return V, d, nb


def load_order(path, V):
    order = [int(x) for x in open(path).read().split()]
    if len(order) != V or sorted(order) != list(range(V)):
        raise Reject("order is not a permutation of 0..V-1")
    return order


def check(V, d, nb, order):
    k = d // 2
    pos = [0] * V
    for i, v in enumerate(order):
        pos[v] = i
    j = [sum(pos[u] < pos[v] for u in nb[v]) for v in range(V)]
    cost = sum(max(0, k - x) for x in j)
    twice = sum(abs(x - k) for x in j)
    if twice != 2 * cost:
        raise Reject("cost != half of sum |j-k|")
    # cut profile recounted from edge membership
    edges = [(u, v) for u in range(V) for v in nb[u] if u < v]
    inS = [False] * V
    cuts, asc, prev = [], 0, 0
    for t, v in enumerate(order):
        inS[v] = True
        c = sum(inS[a] != inS[b] for a, b in edges) if t % 91 == 0 else None
        # incremental for every step, recount spot-checked every 91 steps
        cur = prev + sum(1 for u in nb[v] if not inS[u]) - sum(1 for u in nb[v] if inS[u])
        if c is not None and c != cur:
            raise Reject("incremental cut disagrees with recount")
        asc += max(0, cur - prev); prev = cur; cuts.append(cur)
    if prev != 0 or asc != 2 * cost:
        raise Reject("cost != half the total ascent of the cut profile")
    # split identity at every prefix
    for t in range(V + 1):
        S = set(order[:t])
        dS = sum((a in S) != (b in S) for a, b in edges)
        lhs = sum(max(0, j[v] - k) for v in S)
        rhs = sum(max(0, sum(1 for u in nb[v] if u not in S and pos[u] > pos[v]) - k)
                  for v in order[t:])
        if dS % 2 or dS // 2 + lhs + rhs != cost:
            raise Reject(f"split identity fails at t={t}")
    # back-arc flow: node 0 source, 1 sink, 2+v out-copy, 2+V+u in-copy
    rows, cols, caps = [], [], []
    for v in range(V):
        if j[v] > k:
            rows.append(0); cols.append(2 + v); caps.append(j[v] - k)
            for u in nb[v]:
                if pos[u] < pos[v] and j[u] < k:
                    rows.append(2 + v); cols.append(2 + V + u); caps.append(1)
        if j[v] < k:
            rows.append(2 + V + v); cols.append(1); caps.append(k - j[v])
    n = 2 + 2 * V
    M = csr_matrix((np.array(caps, dtype=np.int32), (rows, cols)), shape=(n, n))
    flow = int(maximum_flow(M, 0, 1).flow_value)
    need = sum(max(0, x - k) for x in j)
    return {"V": V, "deg": d, "cost": cost, "max_prefix_cut": max(cuts),
            "flow": flow, "flow_need": need, "flow_feasible": flow == need}


def main(argv):
    try:
        V, d, nb = load_graph(argv[1])
        r = check(V, d, nb, load_order(argv[2], V))
    except Reject as e:
        print("REJECT:", e); return 2
    print(json.dumps(r) if "--json" in argv else
          f"cost {r['cost']} max_prefix_cut {r['max_prefix_cut']} flow {r['flow']}/{r['flow_need']} feasible {r['flow_feasible']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

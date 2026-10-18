"""Stdlib verifier for the PG(2,16)-M bootstrap-order package.

Checks, all with exact integers:
 1. The graph: D' + {59} is a perfect difference set mod 273; G = Singer incidence of PG(2,16) minus the invariant
    matching point i -- line i+59; its text form hashes to the pinned SHA256 of limits-1/bootstrap/xl/graph16_59.txt.
    G is 16-regular, bipartite and 4-cycle free.
 2. The cyclic order (multiplier 118, line offset 81, alternating) hashes to the pinned SHA256 of ord784.txt.
 3. For every order in RESULT.json: cost = sum (8-j)^+ = (1/2) sum |j-8| = (1/2) total ascent of the cut profile;
    the split identity cost = |dS|/2 + sum_S (j-8)^+ + sum_{V-S} (l-8)^+ at every prefix; back-arc flow by Dinic.
    Recorded value and flow verdict must match; every cost must be >= 772 (consistency with dim C <= Boot, imported).
 4. Merge DP replay for the recorded multiplier/offset triples (exact optimum within those merge families).
 5. Failure controls: corrupted orders and graphs are rejected; a two-swap of the cyclic order is flow-infeasible.
"""
import hashlib, json, os, sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
N, K, DEG = 273, 8, 16
DPRIME = [39, 78, 83, 89, 91, 118, 125, 156, 166, 178, 181, 182, 199, 227, 236, 250]
DELTA = 59
GRAPH_SHA = "6a12ff61f721449228957ea9ab691536fbaa24f45c30bdf3a8fcbf8655f36a6e"
ORD784_SHA = "7637858829c02a819219028a366fd95f98263ab6eba4c4264e1d22f147f93a8c"


def graph_text():
    lines = [f"{2 * N} {DEG}"]
    for i in range(N):
        lines.append(" ".join(str(N + (i + d) % N) for d in DPRIME))
    for x in range(N):
        lines.append(" ".join(str(u) for u in sorted((x - d) % N for d in DPRIME)))
    return "\n".join(lines) + "\n"


def parse_graph(text):
    tok = text.split()
    V, d = int(tok[0]), int(tok[1])
    vals = list(map(int, tok[2:]))
    assert len(vals) == V * d, "wrong number of neighbour entries"
    nb = [vals[v * d:(v + 1) * d] for v in range(V)]
    for v in range(V):
        assert len(set(nb[v])) == d and v not in nb[v] and all(0 <= u < V for u in nb[v]), f"bad row {v}"
    adj = [set(x) for x in nb]
    assert all(v in adj[u] for v in range(V) for u in nb[v]), "not symmetric"
    assert all((v < N) != (u < N) for v in range(V) for u in nb[v]), "not bipartite points/lines"
    seen = set()
    for v in range(V):
        s = sorted(nb[v])
        for a in range(d):
            for b in range(a + 1, d):
                assert (s[a], s[b]) not in seen, "4-cycle"
                seen.add((s[a], s[b]))
    return nb


def cyclic_order(m=118, c=81):
    o = []
    for s in range(N):
        o += [(m * s) % N, N + (m * s + c) % N]
    return o


def dinic(n, edges, s, t):
    g = [[] for _ in range(n)]
    for a, b, cap in edges:
        g[a].append([b, cap, len(g[b])]); g[b].append([a, 0, len(g[a]) - 1])
    flow = 0
    while True:
        lvl = [-1] * n; lvl[s] = 0; q = deque([s])
        while q:
            a = q.popleft()
            for b, cap, _ in g[a]:
                if cap > 0 and lvl[b] < 0:
                    lvl[b] = lvl[a] + 1; q.append(b)
        if lvl[t] < 0:
            return flow
        it = [0] * n

        def push(a, f):
            if a == t:
                return f
            while it[a] < len(g[a]):
                e = g[a][it[a]]
                if e[1] > 0 and lvl[e[0]] == lvl[a] + 1:
                    r = push(e[0], min(f, e[1]))
                    if r:
                        e[1] -= r; g[e[0]][e[2]][1] += r
                        return r
                it[a] += 1
            return 0
        while True:
            f = push(s, 10 ** 9)
            if not f:
                break
            flow += f


def evaluate(nb, order):
    V = len(nb)
    assert sorted(order) == list(range(V)), "order is not a permutation"
    pos = [0] * V
    for i, v in enumerate(order):
        pos[v] = i
    j = [sum(pos[u] < pos[v] for u in nb[v]) for v in range(V)]
    cost = sum(max(0, K - x) for x in j)
    assert sum(abs(x - K) for x in j) == 2 * cost
    inS = [False] * V; cut = asc = mx = 0
    for v in order:
        inS[v] = True
        new = cut + sum(not inS[u] for u in nb[v]) - sum(inS[u] for u in nb[v])
        asc += max(0, new - cut); cut = new; mx = max(mx, cut)
    assert cut == 0 and asc == 2 * cost, "ascent identity"
    edges = [(u, v) for u in range(V) for v in nb[u] if u < v]
    for t in range(V + 1):
        S = set(order[:t])
        dS = sum((a in S) != (b in S) for a, b in edges)
        rhs = dS // 2 + sum(max(0, j[v] - K) for v in S) + sum(
            max(0, sum(1 for u in nb[v] if u not in S and pos[u] > pos[v]) - K) for v in order[t:])
        assert dS % 2 == 0 and rhs == cost, f"split identity at t={t}"
    fe = []
    for v in range(V):
        if j[v] > K:
            fe.append((0, 2 + v, j[v] - K))
            fe += [(2 + v, 2 + V + u, 1) for u in nb[v] if pos[u] < pos[v] and j[u] < K]
        if j[v] < K:
            fe.append((2 + V + v, 1, K - j[v]))
    flow = dinic(2 + 2 * V, fe, 0, 1)
    return dict(cost=cost, max_prefix_cut=mx, flow=flow, flow_feasible=flow == sum(max(0, x - K) for x in j))


def merge_dp(nb, mp, ml, c):
    inv = next(t for t in range(1, N) if (ml * t) % N == 1)
    cP = [[0] * (N + 1) for _ in range(N)]; cL = [[0] * (N + 1) for _ in range(N)]
    for i in range(N):
        p = (mp * i) % N
        for d in DPRIME:
            l = (inv * ((p + d) % N - c)) % N
            cP[i][l + 1] += 1; cL[l][i + 1] += 1
    for row in cP + cL:
        for a in range(1, N + 1):
            row[a] += row[a - 1]
    INF = 1 << 40
    f = [[INF] * (N + 1) for _ in range(N + 1)]; f[0][0] = 0
    for i in range(N + 1):
        for l in range(N + 1):
            x = f[i][l]
            if i < N:
                y = x + max(0, K - cP[i][l])
                if y < f[i + 1][l]: f[i + 1][l] = y
            if l < N:
                y = x + max(0, K - cL[l][i])
                if y < f[i][l + 1]: f[i][l + 1] = y
    return f[N][N]


def main():
    diffs = sorted((a - b) % N for a in DPRIME + [DELTA] for b in DPRIME + [DELTA] if a != b)
    assert diffs == list(range(1, N)), "D' + {59} is not a perfect difference set"
    gt = graph_text()
    assert hashlib.sha256(gt.encode()).hexdigest() == GRAPH_SHA, "graph bytes differ from limits-1 graph16_59.txt"
    nb = parse_graph(gt)
    with open(os.path.join(HERE, "graph16_59.txt"), "rb") as fh:
        assert fh.read() == gt.encode(), "packaged graph16_59.txt differs from the rebuild"
    o784 = cyclic_order()
    assert hashlib.sha256("\n".join(map(str, o784)).encode()).hexdigest() == ORD784_SHA, "ord784 rebuild differs"
    r = evaluate(nb, o784)
    assert (r["cost"], r["max_prefix_cut"], r["flow_feasible"]) == (784, 1568, True), r
    print("positive control: cyclic order cost 784, max cut 1568, flow 784/784")
    res = json.load(open(os.path.join(HERE, "RESULT.json")))
    for rec in res["orders"]:
        e = evaluate(nb, rec["order"])
        assert (e["cost"], e["max_prefix_cut"], e["flow"], e["flow_feasible"]) == (
            rec["cost"], rec["max_prefix_cut"], rec["flow"], rec["flow_feasible"]), (rec["name"], e)
        assert e["cost"] >= 772, f"{rec['name']} below dim C: imported theorem or dimension wrong"
        print(f"order {rec['name']}: cost {e['cost']} max cut {e['max_prefix_cut']} flow {e['flow']} feasible {e['flow_feasible']}")
    for t in res["merge_dp"]["replay_triples"]:
        v = merge_dp(nb, t["mp"], t["ml"], t["c"])
        assert v == t["value"], (t, v)
        print(f"merge DP (mp={t['mp']}, ml={t['ml']}, c={t['c']}): optimum {v}")
    # failure controls
    bad = 0
    for name, o in [("duplicate", o784[:-1] + [o784[0]]), ("short", o784[:-1])]:
        try:
            evaluate(nb, o)
        except AssertionError:
            bad += 1
    sw = o784[:]; sw[10], sw[400] = sw[400], sw[10]
    e = evaluate(nb, sw)
    assert (e["cost"], e["flow_feasible"]) == (789, False), e
    try:
        parse_graph(gt.replace("\n" + gt.split("\n")[1] + "\n", "\n" + " ".join(gt.split("\n")[1].split()[:-1]) + "\n", 1))
    except AssertionError:
        bad += 1
    rows = gt.split("\n")
    # rewire: give point 0 the line of point 1's first unique neighbour (degree preserving 4-cycle control)
    nbx = [list(map(int, x.split())) for x in rows[1:2 * N + 1]]
    a, b = 0, nbx[0][0]; c1 = 1; d1 = [y for y in nbx[1] if y not in nbx[0]][0]
    nbx[a][nbx[a].index(b)] = d1; nbx[d1][nbx[d1].index(c1)] = a
    nbx[c1][nbx[c1].index(d1)] = b; nbx[b][nbx[b].index(a)] = c1
    try:
        parse_graph(rows[0] + "\n" + "\n".join(" ".join(map(str, x)) for x in nbx))
    except AssertionError:
        bad += 1
    assert bad == 4, f"only {bad}/4 corrupted inputs rejected"
    print("failure controls: 4/4 corrupted inputs rejected; two-swap order cost 789, flow-infeasible")
    print("PASS_PG16M_BOOT_ORDERS")


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    main()

"""Can per-session Levi sign gauges rescue a frame embedding of the Braverman-He PG(2,9) coding-gap instance?

Instance: Braverman-He, arXiv:2610.10108 (Section 4, Appendix A). The incidence graph of PG(2,9) has 182 vertices
and 910 edges. The deleted set R (175 edges) and the vertex order pi are transcribed from the paper into
../data/bh_pg29_lists.json. R splits into 157 sessions B, 9 constant-zero edges C and 9 dropped edges J. The other
735 edges are physical, and every session has hop distance 5 in the physical graph.

Frame model at m = 5 with rank-one edges (one child per physical edge). If session i has endpoint frame difference
C_i (an invertible lower-triangular Levi target) and hop distance 5 = m, then along every shortest path the five
edge differences are C_i P_j with P_j orthogonal rank-one idempotents (rank-one matrices C_i^-1 D_e summing to I).
With a common target C_i = I, an edge used by two sessions in opposite directions would be both P and -P'.
Sign gauges C_i = c_i C0 (c_i = +-1, both legal Levi targets) allow it, provided c_i * s_e = sigma(i, e) for
every session i whose geodesics use edge e in direction sigma (s_e = the edge's own sign).
This script checks that sign system. Standard library only."""
import json
import os
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
lists = json.load(open(os.path.join(HERE, '..', 'data', 'bh_pg29_lists.json')))


# F9 = F3[t]/(t^2 + 1), elements as pairs (a, b) = a + b t
def add(x, y):
    return ((x[0] + y[0]) % 3, (x[1] + y[1]) % 3)


def mul(x, y):
    a, b = x
    c, d = y
    return ((a * c - b * d) % 3, (a * d + b * c) % 3)


ZERO, ONE = (0, 0), (1, 0)


def eta(r):
    return (r % 3, r // 3)


T = [(ZERO, ZERO, ONE)] + [(ZERO, ONE, eta(r)) for r in range(9)] + \
    [(ONE, eta(r), eta(s)) for r in range(9) for s in range(9)]
assert len(T) == 91


def dot(p, l):
    s = ZERO
    for i in range(3):
        s = add(s, mul(p[i], l[i]))
    return s


nbr = {i: sorted(j for j in range(91) if dot(T[i], T[j]) == ZERO) for i in range(91)}
edges = [(i, 91 + nbr[i][r]) for i in range(91) for r in range(10)]   # point i -- line j
assert len(edges) == 910

R = lists['R']
if len(R) == 176 and R[-1] == 13:      # trailing page number in the transcription
    R = R[:-1]
pi = lists['pi']
C = {102, 163, 164, 341, 386, 406, 476, 513, 862}
J = {103, 349, 470, 517, 603, 606, 674, 716, 861}
Rs = set(R)
assert len(R) == 175 and C <= Rs and J <= Rs
B = sorted(Rs - C - J)
assert len(B) == 157
pos = {v: k for k, v in enumerate(pi)}
phys = [q for q in range(910) if q not in Rs]
assert len(phys) == 735
sess = []
for q in B:
    u, v = edges[q]
    if pos[u] > pos[v]:
        u, v = v, u
    sess.append((u, v))

adj = defaultdict(list)
for q in phys:
    u, v = edges[q]
    adj[u].append(v)
    adj[v].append(u)


def bfs(s):
    dist = {s: 0}
    dq = deque([s])
    while dq:
        x = dq.popleft()
        for y in adj[x]:
            if y not in dist:
                dist[y] = dist[x] + 1
                dq.append(y)
    return dist


inc = defaultdict(dict)          # session -> {edge: sigma}
both = 0
dists = defaultdict(int)
for i, (s, t) in enumerate(sess):
    ds, dt = bfs(s), bfs(t)
    L = ds[t]
    dists[L] += 1
    for e in phys:
        a, b = edges[e]
        for (x, y, sg) in ((a, b, 1), (b, a, -1)):
            if ds.get(x, 99) + 1 + dt.get(y, 99) == L:
                if e in inc[i] and inc[i][e] != sg:
                    both += 1
                inc[i].setdefault(e, sg)
print('session hop distances:', dict(dists))
print('session/edge pairs used in both directions:', both)

# constraint c_i * s_e = sigma on the bipartite incidence graph; count violations of a BFS 2-colouring
nodes = defaultdict(list)
for i, m in inc.items():
    for e, sg in m.items():
        nodes[('s', i)].append((('e', e), sg))
        nodes[('e', e)].append((('s', i), sg))
colour = {}
violations = 0
components = 0
for start in list(nodes):
    if start in colour:
        continue
    components += 1
    colour[start] = 1
    dq = deque([start])
    while dq:
        x = dq.popleft()
        for y, sg in nodes[x]:
            want = colour[x] * sg
            if y not in colour:
                colour[y] = want
                dq.append(y)
            elif colour[y] != want:
                violations += 1
print('edges on some session geodesic:', len({e for m in inc.values() for e in m}), 'of', len(phys))
print('components:', components, ' violated sign constraints (each counted twice):', violations)
print('sign gauges consistent:', violations == 0)

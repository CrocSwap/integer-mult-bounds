"""(a) nonlinear (tame / Jonquieres) frames, smallest case m = 1, Q = 3.
Address set X = (Z/3)^2 = {(h, d)}, h before d in tape order.
Free group B: (h, d) -> (u h + a, v d + beta(h)), u, v units, beta ANY function (Lemma ordered-affine-streams).
Paid generator: the interchange tau: (h, d) -> (d, h).
Compute c(g) = min #tau over the whole group Gamma = <B, tau> by 0-1 BFS (left multiplication),
then check Lemma R (c >= r_1, r_1 = log_Q of the prefix-image count) and the costs of specific maps."""
from collections import deque
import itertools
import math

Q = 3
PTS = [(h, d) for h in range(Q) for d in range(Q)]
IDX = {p: i for i, p in enumerate(PTS)}


def perm_from_map(fn):
    return tuple(IDX[fn(h, d)] for (h, d) in PTS)


def compose(p, q):
    """(p o q)(x) = p(q(x)); perms as tuples image-of-index."""
    return tuple(p[q[i]] for i in range(len(q)))


IDP = tuple(range(Q * Q))
gens_B = [
    perm_from_map(lambda h, d: ((2 * h) % Q, d)),
    perm_from_map(lambda h, d: ((h + 1) % Q, d)),
    perm_from_map(lambda h, d: (h, (2 * d) % Q)),
]
for j in range(Q):
    gens_B.append(perm_from_map(lambda h, d, j=j: (h, (d + (1 if h == j else 0)) % Q)))
tau = perm_from_map(lambda h, d: (d, h))

# enumerate B explicitly for a size check
Bset = {IDP}
frontier = [IDP]
while frontier:
    nxt = []
    for x in frontier:
        for g in gens_B:
            y = compose(g, x)
            if y not in Bset:
                Bset.add(y)
                nxt.append(y)
    frontier = nxt
print("|B| =", len(Bset), "(expected", 2 * Q * 2 * Q ** Q, ")")

# 0-1 BFS
INF = 10 ** 9
dist = {IDP: 0}
dq = deque([IDP])
while dq:
    x = dq.popleft()
    dx = dist[x]
    for g in gens_B:
        y = compose(g, x)
        if dist.get(y, INF) > dx:
            dist[y] = dx
            dq.appendleft(y)
    y = compose(tau, x)
    if dist.get(y, INF) > dx + 1:
        dist[y] = dx + 1
        dq.append(y)
print("|Gamma| =", len(dist), " (|S_9| = 362880, |A_9| = 181440)")
hist = {}
for v in dist.values():
    hist[v] = hist.get(v, 0) + 1
print("cost histogram c(g):", dict(sorted(hist.items())))


def r1_count(p):
    best = 0
    for h in range(Q):
        imgs = {PTS[p[IDX[(h, d)]]][0] for d in range(Q)}
        best = max(best, len(imgs))
    return best


viol = 0
for p, c in dist.items():
    if r1_count(p) > Q ** c:
        viol += 1
print("Lemma R violations (N_1 > Q^c):", viol)

named = {
    "linear shear (h+d, d)": lambda h, d: ((h + d) % Q, d),
    "nonlinear shear (h+d^2, d)": lambda h, d: ((h + d * d) % Q, d),
    "Feistel (d, h+d^2)": lambda h, d: (d, (h + d * d) % Q),
    "swap (d, h)": lambda h, d: (d, h),
    "(h + 2d^2 + d, d)": lambda h, d: ((h + 2 * d * d + d) % Q, d),
}
for name, fn in named.items():
    p = perm_from_map(fn)
    print(f"c[{name}] = {dist.get(p)}   N_1 = {r1_count(p)}")

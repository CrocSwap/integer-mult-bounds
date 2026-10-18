import sys, itertools, random, collections
sys.path.insert(0, sys.argv[1])
from e8lib import N, G, frames, tetrads
size = int(sys.argv[2])
def clique(size):
    for start in range(N):
        for order in range(200):
            rnd = random.Random(order); K = [start]
            for u in rnd.sample(range(N), N):
                if u not in K and all(G[u][k] != 0 for k in K) and len(K) < size: K.append(u)
            if len(K) == size and all(any(G[v][k] == 0 for k in K) for v in range(N) if v not in K): return sorted(K)
K = clique(size); Ks = set(K); L = [u for u in range(N) if u not in Ks]
sg = lambda u, f: 1 if G[u][f] > 0 else -1
stat = collections.Counter(); first = {}
FRL = frames(L)
for idxF, F in enumerate(FRL[:50]):
    miss = []
    cls = 0; pat = 0; emptypair = 0
    for key, lines in tetrads(F).items():
        T = sorted(key)
        for a, b in itertools.combinations(T, 2):
            for e in (1, -1):
                if not any(u not in Ks for u in lines if sg(u, a) * sg(u, b) == e): cls += 1
        for a, b, c in itertools.combinations(T, 3):
            for e1, e2 in itertools.product((1, -1), repeat=2):
                if not any(u not in Ks for u in lines if sg(u, a) * sg(u, b) == e1 and sg(u, b) * sg(u, c) == e2): pat += 1; miss.append(((a, b, c), (e1, e2)))
    tk = collections.Counter(frozenset(f for f in F if G[k][f] != 0) for k in K)
    stat[(cls, pat, tuple(sorted(tk.values())))] += 1
    first.setdefault((cls, pat), (idxF, F, miss))
print(stat)
for k2, v2 in sorted(first.items()): print('first frame of type (cls,pat)=%s: frames(L)[%d] = %s, missing triple patterns %s' % (k2, v2[0], v2[1], v2[2]))

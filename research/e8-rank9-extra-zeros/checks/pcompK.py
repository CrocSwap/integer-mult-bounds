# CHECK: frames inside L' = E8 \ K that are P-compatible w.r.t. L' (BSTAR §3 definition), K = the rkz.py clique rep of given size.
import sys, itertools, random
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
good = 0; FR = frames(L)
for F in FR:
    ok = True
    for key, lines in tetrads(F).items():
        T = sorted(key)
        for a, b in itertools.combinations(T, 2):
            for e in (1, -1):
                if not any(u not in Ks for u in lines if sg(u, a) * sg(u, b) == e): ok = False
        for a, b, c in itertools.combinations(T, 3):
            for e1, e2 in itertools.product((1, -1), repeat=2):
                if not any(u not in Ks for u in lines if sg(u, a) * sg(u, b) == e1 and sg(u, b) * sg(u, c) == e2): ok = False
    good += ok
print('K', K, 'frames inside L\'', len(FR), 'P-compatible w.r.t. L\'', good)

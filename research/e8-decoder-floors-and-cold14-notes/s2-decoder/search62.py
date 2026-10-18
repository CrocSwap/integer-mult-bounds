import sys, random, time
from dec9sat import *
from e8units import f2_rank_rows
seed = int(sys.argv[1]); N = int(sys.argv[2]); rng = random.Random(seed)
found = 0
for it in range(N):
    # biased: grow a set preferring lines orthogonal to many chosen ones
    P = [rng.randrange(NL)]
    while len(P) < 9:
        cand = [l for l in range(NL) if l not in P and f2_rank_rows([uint[x] for x in P + [l]]) == len(P) + 1]
        w = [1 + 3 * sum(G[l, x] == 0 for x in P) for l in cand]
        P.append(rng.choices(cand, weights=w)[0])
    northo = sum(G[a, b] == 0 for a in P for b in P if a < b)
    r = check_budget(P, 62, verbose=False)
    print(it, sorted(P), 'orth pairs', northo, 'cost<=62' if r else 'no', r if r else '', flush=True)
    if r: found += 1
print('found', found)

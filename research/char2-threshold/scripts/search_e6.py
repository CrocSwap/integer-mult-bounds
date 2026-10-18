"""Authors' script (NOT run by verify.sh): looks for a basis of E6 and a local modification of the full orthogonal pattern B0 with F2 cost 36 = v
(B0 itself costs 37 in every basis tried).  Random basis, random single-entry flips of free entries accepted if the cost does not rise; writes data/e6_best.json."""
import sys, os, json, random
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'lib'))
from roots import *; from units import *
L = unit('E6'); v = len(L); rng = random.Random(5)
for tr in range(1000):
    idx = list(range(v)); rng.shuffle(idx); bidx = []
    for i in idx:
        if rank([L[k] for k in bidx + [i]]) > len(bidx): bidx.append(i)
        if len(bidx) == 6: break
    P, Q = decoder(L, bidx); B = b0(L)
    free = [(t, s) for t in range(v) for s in range(v) if t != s and dot(L[t], L[s]) == 0]
    c = sum(block_ranks(P, Q, B)); print(tr, c, flush=True)
    for it in range(400):
        t, s = rng.choice(free); B[t][s] ^= 1; c2 = sum(block_ranks(P, Q, B))
        if c2 <= c: c = c2
        else: B[t][s] ^= 1
        if c <= 36: break
    if c <= 36:
        json.dump({'basis': bidx, 'rows': [sum(B[t][s] << s for s in range(v)) for t in range(v)], 'cost': c}, open(os.path.join(H, '..', 'data', 'e6_best.json'), 'w')); print('found', c); break

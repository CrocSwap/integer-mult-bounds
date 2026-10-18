"""Local search over Q (support of the extra total, beta = <L, g> on Q) maximising the number of relaxed targets that can
share ONE rank-1 extra total (identical sink rows on Q).  Complex P112 unit, frame decoder."""
import numpy as np, random, sys, time
from collections import defaultdict
from geo import *
LIVE = list(range(8, 120)); LIVEMASK = sum(1 << i for i in LIVE)
Lf = L.astype(float)
TW = [(t, w) for t in LIVE for w in range(1, 512) if w != uint[t] and lab_dot(w, uint[t])]
ZL = {tw: np.array(members(Rmask[tw[1]] & LIVEMASK & ~(1 << tw[0]))) for tw in TW}
PINV = {tw: np.linalg.pinv(Lf[ZL[tw]]) for tw in TW}
def evaluate(Q, g):
    Qa = np.zeros(NL); Qa[list(Q)] = 1
    beta = (Lf @ g) * Qa
    groups = defaultdict(set)
    for (t, w) in TW:
        Z = ZL[(t, w)]
        h = PINV[(t, w)] @ beta[Z]
        if np.abs(Lf[Z] @ h - beta[Z]).max() > 1e-7: continue
        if abs(beta[t] - Lf[t] @ h) < 1e-7: continue
        row = tuple(sorted(S for S in Q if (Rmask[w] >> S) & 1))
        if not row: continue
        groups[row].add(t)
    if not groups: return 0, None
    row, ts = max(groups.items(), key=lambda kv: len(kv[1]))
    return len(ts), (row, sorted(ts))
if __name__ == '__main__':
    d0, e, seed, iters = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    g = Lf[d0]; rng = random.Random(seed)
    Q = set(S for S in LIVE if L[S] @ L[e] == 0 and L[S] @ L[d0] != 0)
    cand = [S for S in LIVE if L[S] @ L[d0] != 0]
    best = evaluate(Q, g); cur = best[0]
    print('start', best[0], best[1][1] if best[1] else None, flush=True)
    t0 = time.time()
    for it in range(iters):
        Q2 = set(Q)
        S = rng.choice(cand)
        if S in Q2: Q2.remove(S)
        else: Q2.add(S)
        if not Q2: continue
        r = evaluate(Q2, g)
        if r[0] >= cur:
            Q, cur = Q2, r[0]
            if r[0] > best[0]:
                best = r; print(it, 'best', r[0], r[1][1], 'Q', sorted(Q), round(time.time() - t0), flush=True)
    print('final', best[0], best[1])

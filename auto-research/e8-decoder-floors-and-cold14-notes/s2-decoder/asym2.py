from asym import *
import time
for e, d0 in [(0, 75), (0, 76), (0, 77), (0, 8), (0, 20), (0, 50), (0, 100)]:
    g = L[d0]
    Q = [S for S in LIVE if L[S] @ L[e] == 0 and L[S] @ g != 0]
    t0 = time.time()
    res = feasible_pairs(Q, g)
    k, ts = best_rank1(res)
    print('e', e, 'd0', d0, '|Q|', len(Q), 'feasible (t,w)', len(res), 'targets', len({r[0] for r in res}), 'best rank-1 group', k, ts, round(time.time()-t0,1), flush=True)

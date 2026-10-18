"""Beam search over prefix sets. Score of a prefix = exact cost of its greedy completion:
realised prefix cost + peel penalty of the complement (the suffix cost-to-go is exactly P(G[V-S]); the peel bounds it above).
usage: python beam.py TAG WIDTH CAND NRUNS"""
import json, sys, time
import numpy as np
from multiprocessing import Pool
from numba import njit
from core import load, peel, order_cost, K

G = "graph16_59.txt"


@njit(cache=True)
def beam(nbr, W, C, seed):
    np.random.seed(seed)
    V, d = nbr.shape
    key = np.random.permutation(V).astype(np.int64)
    zob = np.random.randint(1, 2**62, V).astype(np.int64)
    masks = np.zeros((W, V), np.bool_); cnt = np.zeros((W, V), np.int64)
    orders = np.zeros((W, V), np.int64); g = np.zeros(W, np.int64); hs = np.zeros(W, np.int64)
    nw = 1
    best = 1 << 30; best_order = np.zeros(V, np.int64)
    for t in range(V):
        M = nw * C
        sc = np.empty(M, np.int64); par = np.empty(M, np.int64); vv = np.empty(M, np.int64); hh = np.empty(M, np.int64)
        m = 0
        for w in range(nw):
            pri = np.empty(V); 
            for v in range(V):
                pri[v] = 1e9 if masks[w, v] else max(0, K - cnt[w, v]) + np.random.random() * 0.9
            idx = np.argsort(pri)
            for c in range(min(C, V - t)):
                v = idx[c]
                masks[w, v] = True
                pen, rest = peel(nbr, masks[w], False, key)
                masks[w, v] = False
                inc = max(0, K - cnt[w, v])
                s = g[w] + inc + pen
                sc[m] = s; par[m] = w; vv[m] = v; hh[m] = hs[w] ^ zob[v]
                if s < best:
                    best = s
                    best_order[:t] = orders[w, :t]; best_order[t] = v
                    best_order[t + 1:] = rest
                m += 1
        # select top W unique (score, then realised cost as tie-break)
        tie = np.empty(m)
        for i in range(m):
            tie[i] = sc[i] * 1e4 + (g[par[i]]) + np.random.random() * 0.5
        idx = np.argsort(tie[:m])
        nm = np.zeros((W, V), np.bool_); nc = np.zeros((W, V), np.int64); no = np.zeros((W, V), np.int64)
        ng = np.zeros(W, np.int64); nh = np.zeros(W, np.int64)
        k = 0
        for i in idx:
            if k == W:
                break
            dup = False
            for q in range(k):
                if nh[q] == hh[i]:
                    dup = True; break
            if dup:
                continue
            w = par[i]; v = vv[i]
            nm[k] = masks[w]; nm[k, v] = True
            nc[k] = cnt[w]
            for u in nbr[v]:
                nc[k, u] += 1
            no[k] = orders[w]; no[k, t] = v
            ng[k] = g[w] + max(0, K - cnt[w, v]); nh[k] = hh[i]
            k += 1
        masks, cnt, orders, g, hs, nw = nm, nc, no, ng, nh, k
    return best, best_order


def job(a):
    tag, W, C, seed = a
    nbr = load(G)
    t = time.time()
    b, o = beam(nbr, W, C, seed)
    c = order_cost(nbr, o)
    assert c == b, (c, b)
    return dict(tag=tag, W=W, C=C, seed=seed, best=int(b), sec=round(time.time() - t, 1), order=o.tolist())


if __name__ == "__main__":
    tag, W, C, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    base = int(time.time()) % 100000
    with Pool(int(sys.argv[5]) if len(sys.argv) > 5 else 8) as p, open(f"runs_{tag}.jsonl", "a") as out:
        for r in p.imap_unordered(job, [(tag, W, C, base + i) for i in range(n)]):
            out.write(json.dumps(r) + "\n"); out.flush()
            print(r["tag"], "W", W, "C", C, "seed", r["seed"], "best", r["best"], "sec", r["sec"], flush=True)

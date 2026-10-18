"""Partition annealing: minimise f(S) = |dS|/2 + peel(G[S]) + peel(G[V-S]); f(S) is the exact cost of a concrete order.
usage: python sa_part.py TAG ITERS T0 T1 NRUNS START(peak|random|file:mask.npy)"""
import json, sys, time
import numpy as np
from multiprocessing import Pool
from numba import njit
from core import load, objective, mask_to_order, order_cost, cut_size

G = "graph16_59.txt"
O784 = None  # the 784 order is rebuilt below (multiplier 118, line offset 81)


@njit(cache=True)
def anneal(nbr, mask0, key, iters, T0, T1, seed):
    np.random.seed(seed)
    V = nbr.shape[0]
    mask = mask0.copy()
    f = objective(nbr, mask, key)
    best = f
    bestm = mask.copy()
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        v = np.random.randint(V)
        if np.random.random() < 0.5:
            mask[v] = not mask[v]
            g = objective(nbr, mask, key)
            if g <= f or np.random.random() < np.exp((f - g) / T):
                f = g
            else:
                mask[v] = not mask[v]
        else:  # swap a vertex with a neighbour on the other side
            u = nbr[v, np.random.randint(nbr.shape[1])]
            if mask[u] == mask[v]:
                continue
            mask[v] = not mask[v]; mask[u] = not mask[u]
            g = objective(nbr, mask, key)
            if g <= f or np.random.random() < np.exp((f - g) / T):
                f = g
            else:
                mask[v] = not mask[v]; mask[u] = not mask[u]
        if f < best:
            best = f
            bestm = mask.copy()
    return best, bestm


def start_mask(nbr, kind, rng):
    V = nbr.shape[0]
    if kind == "random":
        return rng.random(V) < 0.5
    if kind.startswith("file:"):
        return np.load(kind[5:])
    o = np.array([x for s in range(273) for x in ((118 * s) % 273, 273 + (118 * s + 81) % 273)], dtype=np.int64)
    m = np.zeros(V, np.bool_); best = (-1, None)
    for v in o:
        m[v] = True
        c = cut_size(nbr, m)
        if c > best[0]:
            best = (c, m.copy())
    return best[1]


def job(a):
    tag, iters, T0, T1, start, seed = a
    nbr = load(G)
    rng = np.random.default_rng(seed)
    key = rng.permutation(nbr.shape[0]).astype(np.int64)
    m0 = start_mask(nbr, start, rng)
    t = time.time()
    best, bm = anneal(nbr, m0, key, iters, T0, T1, seed)
    o = mask_to_order(nbr, bm, key)
    c = order_cost(nbr, o)
    assert c == best
    return dict(tag=tag, seed=seed, start=start, iters=iters, T0=T0, T1=T1, best=int(best), sec=round(time.time() - t, 1),
                size=int(bm.sum()), cut=int(cut_size(nbr, bm)), order=o.tolist())


if __name__ == "__main__":
    tag, iters, T0, T1, n, start = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    base = int(time.time()) % 100000
    with Pool(8) as p, open(f"runs_{tag}.jsonl", "a") as out:
        for r in p.imap_unordered(job, [(tag, iters, T0, T1, start, base + i) for i in range(n)]):
            out.write(json.dumps(r) + "\n"); out.flush()
            print(r["tag"], r["seed"], r["start"], "best", r["best"], "size", r["size"], "cut", r["cut"], "sec", r["sec"], flush=True)

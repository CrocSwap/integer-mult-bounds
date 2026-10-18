"""Exact-cost order annealing with insertion moves (window W), started from given orders.
usage: python polish.py TAG IN.jsonl TOPN ITERS T0 T1 WINDOW REPEATS"""
import json, sys, time
import numpy as np
from multiprocessing import Pool
from numba import njit
from core import load, order_cost, K

G = "graph16_59.txt"


@njit(cache=True)
def anneal_order(nbr, order0, iters, T0, T1, Wn, seed):
    np.random.seed(seed)
    V = nbr.shape[0]
    order = order0.copy()
    pos = np.empty(V, np.int64)
    for i in range(V):
        pos[order[i]] = i
    j = np.zeros(V, np.int64)
    for v in range(V):
        for u in nbr[v]:
            if pos[u] < pos[v]:
                j[v] += 1
    f = 0
    for v in range(V):
        f += max(0, K - j[v])
    best = f; bo = order.copy()
    for it in range(iters):
        T = T0 * (T1 / T0) ** (it / iters)
        a = np.random.randint(V)
        b = a + np.random.randint(-Wn, Wn + 1)
        if b < 0 or b >= V or b == a:
            continue
        v = order[a]
        dlt = 0
        dj_v = 0
        for u in nbr[v]:
            pu = pos[u]
            if a < b and a < pu <= b:      # v moves after u
                dlt += max(0, K - (j[u] - 1)) - max(0, K - j[u]); dj_v += 1
            elif b < a and b <= pu < a:    # v moves before u
                dlt += max(0, K - (j[u] + 1)) - max(0, K - j[u]); dj_v -= 1
        dlt += max(0, K - (j[v] + dj_v)) - max(0, K - j[v])
        if dlt <= 0 or np.random.random() < np.exp(-dlt / T):
            for u in nbr[v]:
                pu = pos[u]
                if a < b and a < pu <= b:
                    j[u] -= 1
                elif b < a and b <= pu < a:
                    j[u] += 1
            j[v] += dj_v
            if a < b:
                for i in range(a, b):
                    order[i] = order[i + 1]; pos[order[i]] = i
            else:
                for i in range(a, b, -1):
                    order[i] = order[i - 1]; pos[order[i]] = i
            order[b] = v; pos[v] = b
            f += dlt
            if f < best:
                best = f; bo = order.copy()
    return best, bo


def job(a):
    tag, src, o, iters, T0, T1, W, seed = a
    nbr = load(G)
    t = time.time()
    b, bo = anneal_order(nbr, np.array(o, np.int64), iters, T0, T1, W, seed)
    assert order_cost(nbr, bo) == b
    return dict(tag=tag, src=src, start=int(order_cost(nbr, np.array(o, np.int64))), best=int(b), seed=seed,
                iters=iters, T0=T0, T1=T1, W=W, sec=round(time.time() - t, 1), order=bo.tolist())


if __name__ == "__main__":
    tag, inp, top, iters, T0, T1, W, rep = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8])
    rows = sorted((json.loads(l) for f in inp.split(",") for l in open(f)), key=lambda r: r["best"])[:top]
    base = int(time.time()) % 100000
    jobs = [(tag, f"{r.get('tag')}:{r.get('seed')}", r["order"], iters, T0, T1, W, base + 17 * i + k) for i, r in enumerate(rows) for k in range(rep)]
    with Pool(8) as p, open(f"runs_{tag}.jsonl", "a") as out:
        for r in p.imap_unordered(job, jobs):
            out.write(json.dumps(r) + "\n"); out.flush()
            print(r["tag"], r["src"], "start", r["start"], "best", r["best"], "sec", r["sec"], flush=True)

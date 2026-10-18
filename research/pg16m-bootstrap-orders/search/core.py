"""Shared numba kernels: graph load, exact order cost, greedy degeneracy peel, partition objective."""
import numpy as np
from numba import njit

K = 8


def load(path):
    tok = open(path).read().split()
    V, d = int(tok[0]), int(tok[1])
    return np.array(tok[2:], dtype=np.int64).reshape(V, d)


@njit(cache=True)
def order_cost(nbr, order):
    V, d = nbr.shape
    pos = np.empty(V, np.int64)
    for i in range(V):
        pos[order[i]] = i
    c = 0
    for v in range(V):
        j = 0
        for u in nbr[v]:
            if pos[u] < pos[v]:
                j += 1
        if j < K:
            c += K - j
    return c


@njit(cache=True)
def peel(nbr, mask, want, key):
    """Min-degree peel of G[{v: mask[v]==want}]. Returns (sum (deg_at_removal-K)^+, removal order).
    Prefix use: reversed removal order. Suffix use: removal order as is."""
    V, d = nbr.shape
    alive = np.zeros(V, np.bool_)
    n = 0
    for v in range(V):
        if mask[v] == want:
            alive[v] = True
            n += 1
    deg = np.zeros(V, np.int64)
    for v in range(V):
        if alive[v]:
            for u in nbr[v]:
                if alive[u]:
                    deg[v] += 1
    head = -np.ones(d + 1, np.int64)
    nxt = -np.ones(V, np.int64)
    prv = -np.ones(V, np.int64)
    for i in range(V - 1, -1, -1):
        v = key[i]
        if alive[v]:
            b = deg[v]
            nxt[v] = head[b]
            if head[b] >= 0:
                prv[head[b]] = v
            prv[v] = -1
            head[b] = v
    out = np.empty(n, np.int64)
    pen = 0
    for cnt in range(n):
        b = 0
        while head[b] < 0:
            b += 1
        v = head[b]
        head[b] = nxt[v]
        if nxt[v] >= 0:
            prv[nxt[v]] = -1
        alive[v] = False
        out[cnt] = v
        if b > K:
            pen += b - K
        for u in nbr[v]:
            if alive[u]:
                bu = deg[u]
                if prv[u] >= 0:
                    nxt[prv[u]] = nxt[u]
                else:
                    head[bu] = nxt[u]
                if nxt[u] >= 0:
                    prv[nxt[u]] = prv[u]
                deg[u] = bu - 1
                nxt[u] = head[bu - 1]
                if head[bu - 1] >= 0:
                    prv[head[bu - 1]] = u
                prv[u] = -1
                head[bu - 1] = u
    return pen, out


@njit(cache=True)
def cut_size(nbr, mask):
    V, d = nbr.shape
    c = 0
    for v in range(V):
        for u in nbr[v]:
            if mask[u] != mask[v]:
                c += 1
    return c // 2


@njit(cache=True)
def objective(nbr, mask, key):
    pa, _ = peel(nbr, mask, True, key)
    pb, _ = peel(nbr, mask, False, key)
    return cut_size(nbr, mask) // 2 + pa + pb


@njit(cache=True)
def mask_to_order(nbr, mask, key):
    _, a = peel(nbr, mask, True, key)
    _, b = peel(nbr, mask, False, key)
    return np.concatenate((a[::-1], b))

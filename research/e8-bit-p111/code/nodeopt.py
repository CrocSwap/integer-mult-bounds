# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Bill-aware realisation of a block node: wires start as unit vectors e_0..e_{n-1} (the keepers' lines), and must end
holding the rows of N in some order.  A realisation is a list of ops (a, b): wire a ^= wire b.  Cost = max
cancellation-free norm over the op list followed by its literal reverse (both bill passes see sigma then sigma^rev),
starting from unit norms.  Candidates: LU with random row/column relabellings, and a hub scheme."""
import random


def lu_ops(rows, n):
    """rows: list of n ints (target rows, in the unit basis, row k = output on wire k).  Returns ops realising
    wire k := rows[k] from wire k = e_k, as U (increasing) then L (decreasing) [no pivoting], or None."""
    A = [[(rows[k] >> j) & 1 for j in range(n)] for k in range(n)]
    Lm = [[0] * n for _ in range(n)]
    for col in range(n):
        if not A[col][col]:
            return None
        for r in range(col + 1, n):
            if A[r][col]:
                Lm[r][col] = 1
                A[r] = [x ^ y for x, y in zip(A[r], A[col])]
    ops = []
    for i in range(n):
        for j in range(i + 1, n):
            if A[i][j]:
                ops.append((i, j))
    for i in range(n - 1, -1, -1):
        for j in range(i):
            if Lm[i][j]:
                ops.append((i, j))
    return ops


def apply(ops, n):
    cur = [1 << k for k in range(n)]
    for a, b in ops:
        cur[a] ^= cur[b]
    return cur


def cost(ops, n, start=None):
    nm = list(start) if start else [1] * n
    mx = max(nm)
    for a, b in ops + list(reversed(ops)):
        nm[a] += nm[b]
        mx = max(mx, nm[a])
    return mx


def pivot_perm(N, order, rng):
    """Random row pivoting: walk the wires in 'order' (columns); for each, pick a random remaining output whose
    reduced row has a 1 there.  Returns perm (output k -> wire perm[k]) such that LU without pivoting succeeds in
    'order', or None."""
    n = len(N)
    rows = list(range(n))
    red = {k: N[k] for k in range(n)}
    perm = [None] * n
    remaining = set(range(n))
    for i in range(n):
        w = order[i]
        cand = [k for k in remaining if red[k] >> w & 1]
        if not cand:
            return None
        k = rng.choice(cand)
        perm[k] = w
        remaining.discard(k)
        for k2 in remaining:
            if red[k2] >> w & 1:
                red[k2] ^= red[k]
    return perm


def realise(N, rng, tries=3000):
    """N: list of n ints over n bits (outputs in the inputs' unit basis).  Returns (best_cost, ops, assign) where
    assign[k] = wire holding N[k]."""
    n = len(N)
    best = None
    for _ in range(tries):
        order = list(range(n))
        rng.shuffle(order)              # process wires in this order (relabel)
        perm = pivot_perm(N, order, rng)
        if perm is None:
            continue
        rows = [0] * n
        for k in range(n):
            rows[perm[k]] = N[k]
        rr = []
        for i in range(n):
            w = order[i]
            v = rows[w]
            nv = 0
            for j in range(n):
                if v >> order[j] & 1:
                    nv |= 1 << j
            rr.append(nv)
        ops = lu_ops(rr, n)
        if ops is None:
            continue
        ops = [(order[a], order[b]) for a, b in ops]
        c = cost(ops, n)
        if best is None or c < best[0]:
            cur = apply(ops, n)
            assert all(cur[perm[k]] == N[k] for k in range(n))
            best = (c, ops, perm)
    return best


if __name__ == "__main__":
    import sys
    rng = random.Random(0)
    n = 12
    # random dense test matrix of full rank
    import itertools
    while True:
        N = [rng.randrange(1, 1 << n) | (1 << n) - 1 & rng.randrange(1 << n) for _ in range(n)]
        b = []
        for v in N:
            for x in b:
                v = min(v, v ^ x)
            if v:
                b.append(v)
        if len(b) == n:
            break
    r = realise(N, rng, tries=int(sys.argv[1]) if len(sys.argv) > 1 else 2000)
    print("best cost bits", r[0].bit_length(), "ops", len(r[1]))

"""Experimental alternative matchings (radical idea I-matching). Controlled by env IMB_MATCH = JSON:
  {"carrier": {"mode": "hk"|"random"|"weighted"|"steiner_target"|"steiner_value", "seed": int, "w": "J"|"rt"|"-rt"|"root"|"op", "m": 100},
   "reuse": {"mode": "tiered"|"tiered_random"|"hk"|"hk_random"|"tiers"|"weighted_noise", "seed": int, "bounds": [..]},
   "stats": "/path/to/stats.json"}
"""
import json, os, random, math
from collections import deque


def cfg():
    s = os.environ.get('IMB_MATCH')
    return json.loads(s) if s else {}


def write_stats(key, obj):
    c = cfg()
    p = c.get('stats')
    if not p:
        return
    try:
        d = json.loads(open(p).read()) if os.path.exists(p) else {}
    except Exception:
        d = {}
    d[key] = obj
    open(p, 'w').write(json.dumps(d))


def hopcroft_karp(adj, nleft, nright):
    INF = 1 << 30
    mL, mR = [-1] * nleft, [-1] * nright
    while True:
        dist = [INF] * nleft
        dq = deque(u for u in range(nleft) if mL[u] < 0)
        for u in dq:
            dist[u] = 0
        found = False
        while dq:
            u = dq.popleft()
            for w in adj[u]:
                m = mR[w]
                if m < 0:
                    found = True
                elif dist[m] == INF:
                    dist[m] = dist[u] + 1
                    dq.append(m)
        if not found:
            return mL
        it = [0] * nleft
        for u0 in range(nleft):
            if mL[u0] >= 0:
                continue
            stack = [u0]
            while stack:
                u = stack[-1]
                if it[u] < len(adj[u]):
                    w = adj[u][it[u]]
                    it[u] += 1
                    m = mR[w]
                    if m < 0:
                        ws = w
                        for uu in reversed(stack):
                            prev = mL[uu]
                            mL[uu], mR[ws] = ws, uu
                            ws = prev
                        break
                    if dist[m] == dist[u] + 1:
                        stack.append(m)
                else:
                    dist[u] = INF
                    stack.pop()


def shuffled_hk(adj, nleft, nright, seed):
    """Random maximum matching: random donor order and random adjacency order, then Hopcroft-Karp."""
    rng = random.Random(seed)
    perm = list(range(nleft)); rng.shuffle(perm)
    adj2 = []
    for i in perm:
        l = list(adj[i]); rng.shuffle(l); adj2.append(l)
    m2 = hopcroft_karp(adj2, nleft, nright)
    mL = [-1] * nleft
    for k, i in enumerate(perm):
        mL[i] = m2[k]
    return mL


def min_weight_full(adj, nleft, nright, weight, seed=None, noise=0.0):
    """Minimum-total-weight matching that covers every left vertex having an edge (requires that a full matching of
    those exists, which holds when every maximum matching covers them). weight(i, j) -> float. Returns mL."""
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import min_weight_full_bipartite_matching
    rng = random.Random(seed) if seed is not None else None
    rows, cols, vals = [], [], []
    left = [i for i in range(nleft) if adj[i]]
    lidx = {i: k for k, i in enumerate(left)}
    for i in left:
        for j in adj[i]:
            w = weight(i, j)
            if rng is not None and noise:
                w += noise * rng.random()
            rows.append(lidx[i]); cols.append(j); vals.append(w)
    vals = np.array(vals, dtype=float)
    vals = vals - vals.min() + 1.0   # strictly positive (zero would mean no edge)
    B = csr_matrix((vals, (rows, cols)), shape=(len(left), nright))
    r, c = min_weight_full_bipartite_matching(B)
    mL = [-1] * nleft
    for k, j in zip(r, c):
        mL[left[k]] = int(j)
    return mL


def J(r, m):
    return 0.0 if r <= 0 else r * math.log(m / r)


def augment_from(adj, nleft, matchL, matchR):
    gained = 0
    for u0 in range(nleft):
        if matchL[u0] >= 0:
            continue
        seen, stack, path, found = set(), [(u0, iter(adj[u0]))], [], None
        while stack:
            u, it = stack[-1]
            w = next(it, None)
            if w is None:
                stack.pop()
                if path:
                    path.pop()
                continue
            if w in seen:
                continue
            seen.add(w)
            v2 = matchR.get(w, -1)
            path.append((u, w))
            if v2 < 0:
                found = list(path)
                break
            stack.append((v2, iter(adj[v2])))
        if found:
            for u, w in found:
                matchL[u] = w; matchR[w] = u
            gained += 1
    return gained


def tiered(adj, nleft, key, seed=None):
    rng = random.Random(seed) if seed is not None else None
    if rng is not None:
        adj = [list(l) for l in adj]
        for l in adj:
            rng.shuffle(l)
    tiers = sorted({key(d) for lst in adj for d in lst}, reverse=True)
    matchL, matchR = [-1] * nleft, {}
    order = list(range(nleft))
    if rng is not None:
        rng.shuffle(order)
    for t in tiers:
        sub = [[d for d in lst if key(d) >= t] for lst in adj]
        if rng is None:
            while augment_from(sub, nleft, matchL, matchR):
                pass
        else:
            # same algorithm with a random start order (permute left side)
            sub2 = [sub[i] for i in order]
            mL2 = [matchL[i] for i in order]
            while augment_from(sub2, nleft, mL2, matchR):
                pass
            for k, i in enumerate(order):
                matchL[i] = mL2[k]
    return matchL

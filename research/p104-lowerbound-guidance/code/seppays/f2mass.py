"""SEPPAYS f2mass.py (own code): exact F2 decoder mass of odd-cell patterns (Dijkstra over patterns) vs rank_F2(Q o Rec)."""
import itertools, heapq, sys
dot = lambda a, b: bin(a & b).count('1') & 1
def rank2(rows):
    piv = {}; r = 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv: v ^= piv[h]
            else: piv[h] = v; r += 1; break
    return r
def setup(P):
    T = len(P); odd = [(t, s) for t in range(T) for s in range(T) if dot(P[t], P[s])]
    idx = {c: i for i, c in enumerate(odd)}
    rows = {}
    for D in range(1, 1 << T):
        for S in range(1, 1 << T):
            pat = 0
            for (t, s), i in idx.items():
                if D >> t & 1 and S >> s & 1: pat |= 1 << i
            if not pat: continue
            M = [sum(1 << j for j in range(T) if S >> j & 1 and dot(P[t], P[j])) for t in range(T) if D >> t & 1]
            pr = rank2(M)
            if pat not in rows or rows[pat] > pr: rows[pat] = pr
    return odd, idx, rows
def all_mass(P):
    odd, idx, rows = setup(P); N = len(odd)
    dist = {0: 0}; pq = [(0, 0)]
    while pq:
        d, x = heapq.heappop(pq)
        if dist.get(x, 1e9) < d: continue
        for r, p in rows.items():
            y = x ^ r
            if d + p < dist.get(y, 1e9): dist[y] = d + p; heapq.heappush(pq, (d + p, y))
    return odd, idx, dist
def rankQ(P, odd, pat):
    T = len(P); M = [0] * T
    for i, (t, s) in enumerate(odd):
        if pat >> i & 1: M[t] |= 1 << s
    return rank2(M)
if __name__ == '__main__':
    for P in [[1, 2, 7], [1, 2, 4, 7], [1, 2, 4, 8, 7], [1, 2, 4, 8, 14], [1, 2, 7, 11, 13]]:
        odd, idx, dist = all_mass(P)
        gap = [(pat, m, rankQ(P, odd, pat)) for pat, m in dist.items() if m > rankQ(P, odd, pat)]
        print(P, 'odd cells', len(odd), 'patterns', len(dist), 'mass>rank', len(gap), 'max gap', max((m - r for _, m, r in gap), default=0))

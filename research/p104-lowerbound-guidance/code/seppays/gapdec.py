from f2mass import *
import heapq
P = [1, 2, 7, 11, 13]
odd, idx, rows = setup(P)
T = 5
# rows with witness supports
wit = {}
for D in range(1, 1 << T):
    for S in range(1, 1 << T):
        pat = 0
        for (t, s), i in idx.items():
            if D >> t & 1 and S >> s & 1: pat |= 1 << i
        if not pat: continue
        M = [sum(1 << j for j in range(T) if S >> j & 1 and dot(P[t], P[j])) for t in range(T) if D >> t & 1]
        pr = rank2(M)
        if pat not in wit or wit[pat][0] > pr: wit[pat] = (pr, D, S)
target = 0
M = [[0, 0, 1, 1, 0], [0, 0, 0, 0, 0], [1, 1, 1, 0, 0], [1, 1, 0, 1, 0], [0, 0, 0, 0, 0]]
for (t, s), i in idx.items():
    if M[t][s]: target |= 1 << i
dist = {0: (0, None, None)}; pq = [(0, 0)]
while pq:
    d, x = heapq.heappop(pq)
    if dist[x][0] < d: continue
    if x == target: break
    for r, (p, D, S) in wit.items():
        y = x ^ r
        if y not in dist or d + p < dist[y][0]: dist[y] = (d + p, x, (p, D, S)); heapq.heappush(pq, (d + p, y))
x = target
while x:
    d, px, (p, D, S) = dist[x]
    print('row price', p, 'D', [t for t in range(T) if D >> t & 1], 'S', [s for s in range(T) if S >> s & 1])
    x = px

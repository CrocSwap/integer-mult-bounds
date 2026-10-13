import numpy as np
from bitp import *
P = [39, 52, 57, 71, 76, 78, 103, 109, 114]
Ps = set(P)
live = np.ones(NL, bool); live[P] = False
R = {p: [int(i) for i in RLIST[p][live[RLIST[p]]]] for p in range(1, 512)}
D = [p for p in range(1, 512) if rankQ_lines(R[p]) < 8]
print('deficient', D, 'labels of punctured', [uint[y] for y in P])
print('G among punctured:'); print(G[np.ix_(P, P)])
# cost table for pairs with a deficient side
from collections import Counter
cnt = Counter()
for d in D:
    for q in range(1, 512):
        cnt[('p=d', rankG(R[d], R[q]))] += 1
        cnt[('q=d', rankG(R[q], R[d]))] += 1
print(cnt)
print('d-d costs'); print(np.array([[rankG(R[a], R[b]) for b in D] for a in D]))

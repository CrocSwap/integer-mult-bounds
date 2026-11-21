from f2mass import *
import collections
P = [1, 2, 7, 11, 13]
odd, idx, dist = all_mass(P)
c = collections.Counter(); ex = {}
for pat, m in dist.items():
    r = rankQ(P, odd, pat)
    if m > r:
        c[(r, m)] += 1
        if (r, m) not in ex or bin(pat).count('1') < bin(ex[(r, m)]).count('1'): ex[(r, m)] = pat
print('odd cells', odd)
print(c)
for k, pat in sorted(ex.items()):
    M = [[0]*5 for _ in range(5)]
    for i, (t, s) in enumerate(odd):
        if pat >> i & 1: M[t][s] = 1
    print(k, M)

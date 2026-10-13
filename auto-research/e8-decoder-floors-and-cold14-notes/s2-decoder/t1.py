from geo import *
from collections import Counter
c = Counter()
for p in ALLP:
    m = members(Rmask[p]); c[(len(m), rankQ_lines(m))] += 1
print(sorted(c.items()))
# check reflections preserve G
import random
P = REFL[5]; assert all(abs(G[P[i],P[j]])==abs(G[i,j]) for i in range(120) for j in range(120))
print('ok')

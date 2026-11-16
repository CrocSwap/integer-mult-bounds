from cov2 import *
import time
ws=[6,6,6,6,6,6,6,6,6,4,1,1,1] # placeholder
E6=None
for I in itertools.combinations(range(8),6):
    if len(parabolic(I))==36: E6=I;break
print(E6)
T=[t for t in range(n) if t not in set(parabolic(E6))]
print(len(T))
for comp in ([6,6,6,5,5,1,1,1],[6,6,6,6,4,1,1,1,1]):
    t0=time.time(); print(comp,sum(g[w] for w in comp),cover_set(T,comp,verbose=True),round(time.time()-t0,1),flush=True)

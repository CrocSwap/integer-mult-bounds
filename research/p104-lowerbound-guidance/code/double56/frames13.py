import sys,numpy as np,collections; sys.path.insert(0,'../orbitlp')
from geo import Q, frames
from rho import f2rank,toint
F=frames()
# find 13 disjoint frames
def disj(F):
    best=None
    def rec(chosen,used,start):
        nonlocal best
        if len(chosen)==13: best=list(chosen); return True
        for i in range(start,len(F)):
            if not (set(F[i])&used):
                if rec(chosen+[F[i]],used|set(F[i]),i+1): return True
        return False
    rec([],set(),0); return best
P=disj(F); print('13 disjoint frames found',P is not None)
np.save('frames13.npy',np.array(P))
c=collections.Counter()
for i in range(13):
  for j in range(13):
    if i!=j:
      B=Q[np.ix_(P[i],P[j])]; c[(tuple(sorted(B.sum(1))),f2rank([toint(r) for r in B]))]+=1
print(c)

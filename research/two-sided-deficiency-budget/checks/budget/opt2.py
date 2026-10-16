# Lows: sizes a_k <= G(sigma_k); q independent; y2-matroid corank b, |Lo| <= t+b.
# Constraint (deletion): removing any j < b lows leaves a code of dim >= b-j supported on the rest:
#   sum of all but the j largest sizes >= d_{b-j}.  Minimise sum sigma; need >= 6b.
import itertools
Gs={0:2,1:4,2:8,3:12,4:20,5:36}   # max |A| for saving sigma (w=sigma+2; w<=2 -> 2 lines)
d={1:53,2:76,3:92,4:100,5:106,6:109,7:111,8:112}
def feasible(sig,b):
    a=sorted((Gs[x] for x in sig),reverse=True)
    return all(sum(a[j:])>=d[b-j] for j in range(b))
for b in range(1,9):
  for t in range(1,7):
    K=t+b; best=None
    for k in range(1,K+1):
      for sig in itertools.combinations_with_replacement(range(6),k):
        if feasible(sig,b):
          s=sum(sig)
          if best is None or s<best[0]: best=(s,sig)
    print(b,t,best, 'ok' if best is None or best[0]>=6*b else 'FAIL')

# min sum sigma over multisets of low weights w in 1..7 with sum g(w) >= target, size <= K
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}; sig=lambda w:max(0,w-2)
from functools import lru_cache
@lru_cache(None)
def best(target,K):
    if target<=0: return (0,())
    if K==0: return (10**9,())
    r=(10**9,())
    for w in range(1,8):
        v,ms=best(target-g[w],K-1)
        if v+sig(w)<r[0]: r=(v+sig(w),(w,)+ms)
    return r
d={1:53,2:76,3:92,4:100,5:106,6:109,7:111,8:112}
for b in range(1,9):
    row=[]
    for t in range(1,7):
        v,ms=best(d[b],t+b); row.append((t,v,6*b,ms))
    print('b=%d d_b=%d'%(b,d[b]),[(t,v,'ok' if v>=6*b else 'FAIL',ms) for t,v,_,ms in row])

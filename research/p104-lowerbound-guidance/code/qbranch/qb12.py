import sys
exec(open('qb1.py').read().split("if __name__")[0])
from collections import Counter
for k in map(int,sys.argv[1:]):
    c,sup=solve(k,False); print(k,'LP',c)
    for x,D,P in sup:
        cnt=Counter(int(t) for t in P); print('  x=%.5f D=%d pieces=%s'%(x,D,dict(cnt)))

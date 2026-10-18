# Lemma S size-relaxation: maximise sum d over nonincreasing d_1>=...>=d_n (1..8), n<=8+e,
# s.t. for i=1..8 with e+i<=n: sum_{j<=e+i} f(d_j) >= g(i). Independent DP (prefix f-sum capped at 120).
from functools import lru_cache
f={1:64,2:36,3:20,4:12,5:8,6:4,7:2,8:1}
Nd={0:0,1:1,2:3,3:6,4:12,5:20,6:36,7:63}
g={i:120-Nd[8-i] for i in range(1,9)}
print('g',g)
import sys
sys.setrecursionlimit(10000)
def solve(e):
    nmax=8+e
    @lru_cache(None)
    def best(j,dprev,fs):
        # j items placed (positions 1..j), last d = dprev, fs = capped prefix f-sum; returns max additional sum d (or -inf)
        # option stop: remaining constraints vacuous since n=j
        res=0
        if j==nmax: return 0
        for d in range(1,dprev+1):
            nfs=min(120,fs+f[d]); pos=j+1
            i=pos-e
            if 1<=i<=8 and nfs<g[i]: continue
            r=best(pos,d,nfs)
            if r is not None and r+d>res: res=r+d
        return res
    return best(0,8,0)
bad=[]
for e in range(0,113):
    v=solve(e)
    ok = v<=9*e
    if e in (0,1,2,13,14,15,16,30,63,64,100,112) or (not ok and e>=15): print('e',e,'max sum d',v,'9e',9*e,'OK' if ok else 'VIOLATES')
    if not ok and e>=15: bad.append(e)
print('violations for e>=15:',bad)
assert not bad and solve(15) == 135 == 9 * 15 and all(solve(e) <= 9 * e for e in range(15, 113)) and solve(14) > 9 * 14
print('PASS Lemma S DP: max sum d <= 9e for every e in [15,112]; equality at e=15 (135); violated at e=14 (127 > 126)')

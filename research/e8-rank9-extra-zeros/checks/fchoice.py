# ZPIN3 fchoice.py: for every X' (lines != f1,f2, <=6 lines; only those in the 30 lines orthogonal to f1,f2 matter) and a=#{f1,f2} in X, does a frame through {f1,f2} with good I exist?
import sys, itertools
from blib import *
FR=frames(); f1=0; f2=min(O[0]); thr=[F for F in FR if f1 in F and f2 in F]
E12=sorted({x for F in thr for x in F if x not in (f1,f2)}); pos={c:i for i,c in enumerate(E12)}
# partner pairs of each frame: tetrads through {f1,f2}
part=[]
for F in thr:
    TT=tetrads(F); ps=set()
    for T in TT:
        fs=[f for f in F if f in T]
        if f1 in fs and f2 in fs: ps.add(frozenset(f for f in fs if f not in (f1,f2)))
    assert len(ps)==3; part.append(ps)
frm=[frozenset(x for x in F if x not in (f1,f2)) for F in thr]
def good(Ip,a):
    # Ip = F∩X' ; a = number of {f1,f2} in X (0,1,2)
    n=len(Ip)+a
    if n>2: return False
    if a==0 and len(Ip)==2: return None  # decided by partner test
    return True
fails=0; tot=0
for a,kmax in ((0,6),(1,5),(2,4)):
    for k in range(0,kmax+1):
        for X in itertools.combinations(E12,k):
            Xs=set(X); tot+=1; ok=False
            for i,fr in enumerate(frm):
                Ip=fr&Xs; g=good(Ip,a)
                if g is None: g = Ip not in part[i]
                if g: ok=True;break
            if not ok: fails+=1; print('FAIL a',a,'X',X)
print('configs',tot,'fails',fails)

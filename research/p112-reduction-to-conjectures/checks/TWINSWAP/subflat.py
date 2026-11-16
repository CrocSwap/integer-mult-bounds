import sys
from flat7p import run, flats, rank
from lib import *
par=lambda x: bin(x).count('1')&1
res=set()
for a in range(1,512):
    for b in range(a+1,512):
        if (a^b)<b: continue
        Yl=frozenset(t for t in range(n) if not par(a&LAB[t]) and not par(b&LAB[t]))
        if len(Yl)>=36: res.add(Yl)
res=sorted(res,key=lambda s:sorted(s))
Y=list(res[int(sys.argv[1])])
from collections import Counter
cnt=Counter(); worst=(-99,)
seen=set()
for F,w in flats(Y):
    if w<int(sys.argv[3]) or w>int(sys.argv[4]) or len(F)<int(sys.argv[2]): continue
    c,prof=run(list(F)); q=len(prof)
    cnt[(w,len(F),q,c)]+=1
    if len(F)-c>worst[0]: worst=(len(F)-c,w,len(F),c,prof)
print('subflats (rank,|F|,dimT,cost_w):count',dict(cnt)); print('max |F|-cost_w',worst)

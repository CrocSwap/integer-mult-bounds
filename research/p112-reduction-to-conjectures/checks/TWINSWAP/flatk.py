# cost_w(C'|_Y) vs |Y| for Y = lines of label w-flats (w = 5,6), all such flats with max line count (and all with >= thr lines).
import sys, itertools
from flat7p import run, rank
from lib import *
par=lambda x: bin(x).count('1')&1
def flats_codim(c,thr):
    res=set()
    for fs in itertools.combinations(range(1,512),c):
        # require independence & canonical: skip if dependent
        if rank_f2(fs)<c: continue
        Yl=frozenset(t for t in range(n) if all(not par(a&LAB[t]) for a in fs))
        if len(Yl)>=thr: res.add(Yl)
    return res
def rank_f2(vs):
    b=[]
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
c,thr=int(sys.argv[1]),int(sys.argv[2])
from collections import Counter
cnt=Counter(); worst=None
for Y in flats_codim(c,thr):
    q=rank([C[t] for t in Y]); cst,prof=run(Y)
    cnt[(len(Y),q,cst)]+=1
    if worst is None or len(Y)-cst>worst[0]: worst=(len(Y)-cst,len(Y),cst,prof)
print('codim',c,'thr',thr,'(|Y|,Qrank,cost_w):count',dict(cnt),'max |Y|-cost',worst)

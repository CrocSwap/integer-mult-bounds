# liveness profile of a bitE8/1 word: helpers live between first and last gate in A+B
import json,gzip,sys
from collections import Counter
w=json.load(gzip.open(sys.argv[1]))
v,R=w['v'],w['R']
print('keys',sorted(w.keys()))
A,B=w['A'],w['B']
gates=[('A',g) for g in A]+[('S',None)]+[('B',g) for g in B]
first={};last={}
for k,(ph,g) in enumerate(gates):
    if g is None: continue
    f,d,srcs=g[0],g[1],g[2]
    for r in [d]+list(srcs):
        if r>=2*v:
            first.setdefault(r,k); last[r]=k
ks=len(A)  # scatter index
ret=set(w['ret'])
# count distinct lifetimes per slot: slot reused => multiple intervals; approximate with first/last
live_at_scatter=sum(1 for r in first if first[r]<ks<last[r])
print('R',R,'helpers touched',len(first),'live across scatter',live_at_scatter,'totals',len(ret))
# frames dims
fr=w['frames']
import itertools
dims=[len(f) for f in fr]
# per slot: number of distinct "births" (gate at frame where slot content zero?) approximate by reuse insert tags
print('A gates',len(A),'B gates',len(B))

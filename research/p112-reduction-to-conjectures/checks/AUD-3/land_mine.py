# AUD-3 independent post-filter re-implementation over dpX enum + symlp (imports shared; filters mine)
import sys, os
from collections import Counter
from itertools import combinations
from math import comb
sys.path.insert(0,'../OS-CHARGE2'); os.chdir('../OS-CHARGE2')
exec(open('dpX.py').read().split("NE8=[0,1,3,6,12,20,36,63]")[0])
from symlp import lp
NE8=[0,1,3,6,12,20,36,63]; GG_A3={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
K=int(sys.argv[1]); ES=[int(x) for x in sys.argv[2].split(',')]
def two_bins(s):  # can multiset s be split into two parts each of sum <= 6
    tot=sum(s); sums={0}
    for x in s: sums|={a+x for a in sums}
    return any(a<=6 and tot-a<=6 for a in sums)
def bkill(ws,d,e):
    if d<4: return False
    for sub in combinations(ws,e):
        if two_bins(sub): return True
        if 1 in sub:
            l=list(sub); l.remove(1)
            if two_bins(l): return True
    return False
res=Counter(); surv={}
for d in range(1,9):
    for wt,ws in enum(d,8*d+K+1,112):
        k=wt-8*d; e=len(ws)-d
        if k<0 or e not in ES: continue
        _,bd=lp(Counter(ws),codim=8-d,NL=112)
        need=112-(NE8[8-d] if d<8 else 0)
        if bd<need-1e-9: res[(e,d,k,'LP')]+=1; continue
        if bkill(ws,d,e): res[(e,d,k,'B')]+=1; continue
        small=sorted(ws)[:e-1]
        if d>=3 and e>=2 and sum(GG_A3[w] for w in small)<=4: res[(e,d,k,'P')]+=1; continue
        if e==2 and comb(len([w for w in ws if w<=6]),3)>8: res[(e,d,k,'T')]+=1; continue
        surv.setdefault((e,d,k),[]).append(ws)
for e in ES:
    tot=sum(len(v) for kk,v in surv.items() if kk[0]==e)
    print('e',e,'total survivors',tot,'by d',[sum(len(v) for kk,v in surv.items() if kk[0]==e and kk[1]==d) for d in range(1,9)])
    print(' slack0 survivors',[ (kk,v) for kk,v in surv.items() if kk[0]==e and kk[2]==0])
    print(' LP-only survivors at slack0 (before B/P/T):',sum(res[(e,d,0,t)] for d in range(1,9) for t in 'BPT'))
if 2 in ES: print('e2 list',sorted((kk[1],kk[2],v) for kk,vs in surv.items() if kk[0]==2 for v in vs))
print('slack0 B/P/T kills',[(kk,v) for kk,v in res.items() if kk[2]==0 and kk[3] in 'BPT'])
print('e1 surv',[(kk,v) for kk,v in surv.items() if kk[0]==1])

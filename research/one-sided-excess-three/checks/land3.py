# slack-k landscape (usage: python land3.py K) (P112, eps-free T-level): DP (dpX ok, NL=112) -> symmetric LP -> Basis-kill (S66+t) -> Pencil -> e=2 triple rule
import sys, itertools
import os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
src=open(os.path.join(HERE,'dpX.py')).read().split("NE8=[0,1,3,6,12,20,36,63]")[0]
exec(src)
from symlp import lp
from math import comb
NE8=[0,1,3,6,12,20,36,63]
gg={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
K=int(sys.argv[1])
def packable(sub):
    # sub: e weights; two bins of capacity 6 (span of union <= sum of dims) plus at most one extra 1-piece
    sub=list(sub)
    opts=[sub]
    if 1 in sub:
        s2=list(sub); s2.remove(1); opts.append(s2)
    for s in opts:
        n=len(s)
        for mask in range(1<<n):
            a=sum(s[i] for i in range(n) if mask>>i&1); b=sum(s)-a
            if a<=6 and b<=6: return True
    return False
def basis_kill(ws,d,e):
    if d<4: return False
    for sub in set(itertools.combinations(sorted(ws),e)):
        if packable(sub): return True
    return False
for d in range(1,9):
    surv=enum(d,8*d+K+1,112); need=112-(NE8[8-d] if d<8 else 0)
    from collections import Counter as Cn
    tally=Cn(); left=[]
    for wt,ws in surv:
        k=wt-8*d
        if k<0: continue
        val,bd=lp(Counter(ws),codim=8-d,NL=112)
        if bd<need-1e-9: tally[(k,'LP')]+=1; continue
        a=len(ws); e=a-d
        if basis_kill(ws,d,e): tally[(k,'BASIS')]+=1; continue
        anchors=sorted(ws)[:e-1]
        if d>=3 and e>=2 and sum(gg[w] for w in anchors)<=4: tally[(k,'PENCIL')]+=1; continue
        if e==2 and comb(sum(1 for w in ws if w<=6),3)>8: tally[(k,'E2TRIPLE')]+=1; continue
        tally[(k,'SURV')]+=1; left.append((k,ws,e))
    for k in range(K+1):
        print('d',d,'slack',k,{t:tally[(k,t)] for t in ('LP','BASIS','PENCIL','E2TRIPLE','SURV')},[x for x in left if x[0]==k][:8],flush=True)

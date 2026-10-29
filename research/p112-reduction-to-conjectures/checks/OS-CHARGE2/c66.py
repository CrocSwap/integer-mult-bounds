# lift-level cost-66 classification inputs: d>=1 multisets with cost(T) <= 8d+2 passing DP -> LP -> Pencil -> e=2 6-triple rule
import sys
sys.argv=['x','0']
exec(open('dpX.py').read().split("NE8=[0,1,3,6,12,20,36,63]")[0])
from symlp import lp
from math import comb
NE8=[0,1,3,6,12,20,36,63]
gg={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
for d in range(1,9):
    surv=enum(d,8*d+3,112); need=112-(NE8[8-d] if d<8 else 0)
    for wt,ws in surv:
        val,bd=lp(Counter(ws),codim=8-d,NL=112)
        if bd<need: continue
        a=len(ws); e=a-d
        anchors=sorted(ws)[:e-1]; Lsz=sum(gg[w] for w in anchors)
        if d>=3 and Lsz<=4: verdict='PENCIL-KILLED'
        elif e==2 and comb(ws.count(6)+sum(1 for w in ws if w<=5),3)>8 and False: verdict='?'
        elif e==2 and comb(sum(1 for w in ws if w<=6),3)>8: verdict='E2-TRIPLE-KILLED'
        else: verdict='SURVIVES'
        print(d,wt,ws,'LP',round(val,2),'e',e,'anchor lines',Lsz,verdict,flush=True)

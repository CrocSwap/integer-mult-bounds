# LANDSPANC1 lc2: (a) t7669 vs the DP: realised origin-priced stop weight; (b) kappa ceilings for S values (rg1 rung formulas)
import sys, signal, io, contextlib; signal.alarm(900)
sys.path.insert(0,'code/fewstops')
from load import *
from collections import defaultdict
t=0.01; s=1-t; pR=lambda R:(R-R**s)/(R-1); p8=pR(8)
dimof=lambda i: len(F[i]); # frames: basis lists
chain=defaultdict(list); cur=list(W['initial'])
for r in range(n): chain[r].append(cur[r])
for e in P:
    if e[0]=='MOVE' and e[1]<n: chain[e[1]].append(e[3])
tot=0.0; cnt=0; byk=defaultdict(int); mains=helpers=0
for r in range(n):
    ch=chain[r]
    for i in range(1,len(ch)-1):          # intermediate stops
        d=dimof(ch[i-1]); tot+=pR(min(8,9-d)); cnt+=1
        if kind(r)=='H': helpers+=1
        else: mains+=1
print('public regs',n,'intermediate stops',cnt,'helper',helpers,'main/hosted',mains)
print('origin-priced stop weight (previous-chart origin, t=.01) / p8 =',round(tot/p8,2))
# frontier statement: DP floor S=865.58 per call vs measured; also minimal-weight (every stop at p(2)) bound
print('count-based: stops*p(2)/p8 =', round(cnt*pR(2)/p8,2))
with contextlib.redirect_stdout(io.StringIO()):
    sys.path.insert(0,'<research-tree>/cards/WILD/UNIMODEL/runggen'); import rg1
from rg1 import *
for S in ('865.58','1792.25'):
    for hs in (True,False):
        f=add((1,C7113),(-1,nat(112,D(S),hs))); print(f'#7113 X112 S={S} HS={hs}:',fm(ceiling(f)))

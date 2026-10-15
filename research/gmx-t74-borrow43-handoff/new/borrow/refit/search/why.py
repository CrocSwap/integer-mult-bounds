import sys,json
from collections import Counter
from bounds import Bounds,regs
from collections import defaultdict
b=Bounds(sys.argv[1]);Wd=b.Wd;w=Wd.w;v=Wd.v;ev=b.ev
restored={int(q) for q in w.get('helper_final',{})};lenders_now={r[1] for r in w['warps']}
touch=defaultdict(list)
for t,(sec,e) in enumerate(ev):
    for q in ((e[1],) if e[0]=='warp' else regs(e)):touch[q].append((t,sec))
c=Counter();fl=set()
for h in Wd.helpers:
    T=touch[h]
    if h in restored or h in lenders_now or any(s not in('B','restore','Bwarp') for t,s in T):continue
    g=[x for x in b.byreg[h] if x[1]=='gate'][0][0];F1=len(Wd.gateframe[g]);hi=len(b.hi[g])
    for L in Wd.live:
        if v<=L<2*v or L in restored or any(s=='restore' for t,s in touch[L]) or L==h:continue
        if not touch[L][-1][0]<g:continue
        lf=b.byreg[L][-1];U=len(Wd.gateframe[lf[0]]);lo=len(b.lo[lf[0]])
        if U<=F1:k='fixed-ok'
        elif lo<=hi:k='refit-ok'
        else:k='blocked: lender floor lo=%d > follower ceiling hi=%d'%(lo,hi)
        c[(k,'follower F1=%d hi=%d'%(F1,hi))]+=1
for k,n in sorted(c.items()):print(n,k)

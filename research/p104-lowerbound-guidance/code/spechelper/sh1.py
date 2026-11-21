# SPECHELPER sh1: spec-valid helper floor (C1 hub stops, no deaths at V, no rank-8 restriction), exact Fractions; DP over shared trees
# with node charge p2/u(d,m) per non-leaf node (>=2 children) and top P_t charge p2 (one stop at P_t, u=1); then rung ceilings via rg1.
import os, sys, io, contextlib, signal
signal.alarm(900)
from fractions import Fraction as Fr
from decimal import Decimal as D, getcontext, ROUND_FLOOR, ROUND_CEILING
LS='<research-tree>/cards/WILD/UNIMODEL/claspec/landspan'
os.chdir(LS); sys.path.insert(0,LS)
with contextlib.redirect_stdout(io.StringIO()): import ls2
n,M,UU,NT=ls2.n,ls2.M,ls2.UU,ls2.NT
getcontext().prec=50
def pq(t,R,mode):
    sD=1-D(str(t)); v=(D(R)-D(R)**sD)/(R-1); return Fr(v.quantize(D(10)**-40,rounding=mode))
def dp(hubcost, topcost, Z):
    # best[d][m][k]: k = 1 (single child) or 2 (>=2 children) tracked implicitly: a node with >=2 children pays hubcost/u; single-child node pays 0 (no new content).
    best={1:{1:Z}}
    for d in range(2,n-1):
        items=[(e,m,v) for e in best for m,v in best[e].items()]; res={}
        for mt in range(1,M+1):
            uu=UU[(d,mt)]
            if uu==0: continue
            # exactly-mt knapsack tracking item count (1 or >=2)
            K1={}; K2={}
            for (e,m,v) in items:
                if m<=mt and (m not in K1 or v<K1[m]): K1[m]=v
            # K2[mm] = min cost of >=2 items summing to mm (items cost v)
            Kall={0:Z}
            for mm in range(1,mt+1):
                for (e,m,v) in items:
                    if m<=mm and (mm-m) in Kall:
                        c=Kall[mm-m]+v
                        # need >=2 items: from Kall[mm-m] with >=1 item
                        pass
            # simple exact DP over (sum, cnt capped 2)
            S={(0,0):Z}
            for mm in range(0,mt+1):
                for c in (0,1,2):
                    if (mm,c) not in S: continue
                    base=S[(mm,c)]
                    for (e,m,v) in items:
                        if mm+m<=mt:
                            key=(mm+m,min(2,c+1)); val=base+v
                            if key not in S or val<S[key]: S[key]=val
            cands=[]
            if (mt,1) in S: cands.append(S[(mt,1)])
            if (mt,2) in S: cands.append(S[(mt,2)]+hubcost(d)/uu)
            if cands: res[mt]=min(cands)
        best[d]=res
    items=[(e,m,v) for e in best for m,v in best[e].items()]
    K={0:Z}
    for mm in range(1,M+1):
        bv=None
        for (e,m,v) in items:
            if m<=mm and (mm-m) in K:
                c=K[mm-m]+v
                if bv is None or c<bv: bv=c
        if bv is not None: K[mm]=bv
    return K[M]+topcost
def S_of(t,topc=True,hub=True):
    p2=pq(t,2,ROUND_FLOOR); p8=pq(t,8,ROUND_CEILING)
    v=dp((lambda d:p2) if hub else (lambda d:Fr(0)), p2 if topc else Fr(0), Fr(0))
    return NT*v/p8, NT*p2/p8
if __name__=='__main__':
    print('NT',NT,'M',M)
    for t in ('0.0075','0.01'):
        a,b=S_of(t); a0,_=S_of(t,hub=False); print(f't={t}: DP(C1 hubs + top stop) S >= {float(a):.4f} ; top-only 104p2/p8 = {float(b):.4f}; DP(no hub charge)={float(a0):.4f}; equal={a==b}')
        z,_=S_of(t,topc=False); print('   (top charge dropped) DP S =',float(z))

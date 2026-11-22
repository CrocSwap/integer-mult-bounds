# X_I = P112 ∪ {f_i : i∈I}: need eps-free cost(X_I) >= 64+|I|.  Peel at 7: cost >= cost(T7) + 8(8-d).
# DP constraints (dp3 P112, all transfer to X_I since every X_I target contains the P112 target; NL=112+|I|):
# then symmetric LP (NL lines, E8 N_u, g) on survivors.
import sys
from symlp import lp
from collections import Counter
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36}; G={1:1,2:2,3:4,4:8,5:12,6:20,7:32}
N={0:0,1:1,2:3,3:6,4:12,5:20,6:36}
def k1(ws):
    W=sum(ws); sG=sum(G[w] for w in ws); sg=sum(g[w] for w in ws)
    nf= W>=14 and sG>=56
    nr= W>=15 and sG>=53 and len(ws)>=3 and not (len(ws)==3 and max(ws)<=6)
    no= W>=14 and sg>=70
    return nf or nr or no
def ok(ws,d,NL):
    a=len(ws)
    if a<d: return False
    if d>=2 and a<d+2: return False
    if not k1(ws[d-1:]): return False
    for k in range(2,d+1):
        if sum(g[w] for w in ws[d-k:]) < NL-N[8-k]: return False
    if d==8 and sum(g[w] for w in ws)+a<2*NL: return False
    if d==7 and sum(g[w] for w in ws)+3*a<2*(NL-1): return False
    return True
def enum(d,target,NL):
    Ws=[7,6,5,4,3,2,1]; out=[]
    def rec(i,cnt,wt):
        if wt>=target: return
        if i==len(Ws):
            ws=sorted([w for w in Ws for _ in range(cnt[w])],reverse=True)
            if ok(ws,d,NL): out.append((wt,ws))
            return
        w=Ws[i]
        for c in range(0,(target-wt)//w+1):
            cnt[w]=c; rec(i+1,cnt,wt+c*w)
        cnt[w]=0
    rec(0,{w:0 for w in Ws},0); return out
NE8=[0,1,3,6,12,20,36,63]
for I in [int(x) for x in sys.argv[1].split(',')]:
    NL=112+I
    for d in range(1,9):
        surv=enum(d,8*d+I,NL)
        need=NL-NE8[8-d] if d<8 else NL
        bad=[]
        for wt,ws in surv:
            val,bd=lp(Counter(ws),codim=8-d,NL=NL)
            if bd>=need: bad.append((wt,ws,round(val,2)))
        print(f'I={I} d={d} DP-survivors={len(surv)} LP-survivors={len(bad)}',bad[:6],flush=True)

# TWOSIDE bk1: b_Q>=5 cells. Enumerate ALL sigma-multisets (sigma=(w-2)^+, w<=7) with sum<6b passing the size/cap
# deletion constraints, then apply Basis-kill (Lemma B + S66, SIX §3). Implementation 1 (own code; no covm).
import itertools, sys
g={0:2,1:4,2:8,3:12,4:20,5:36}            # global caps g(w), w=sigma+2 (sigma=0 -> w<=2)
c72={0:2,1:4,2:8,3:12,4:20,5:32}          # caps on every |Off|<=72 target (I1) and on E6 level-2 targets (chk6)
d={1:53,2:78,3:92,4:100,5:106,6:109,7:111,8:112}
def size_ok(s,b):                         # s sorted descending
    for j in range(b):                    # level b-j: all but j largest must reach d_{b-j}
        X=s[j:]; lev=b-j
        if lev==1:
            if not (sum(c72[x] for x in X)>=53 or sum(g[x] for x in X)>=73): return False
        elif lev==2:
            if not (sum(c72[x] for x in X)>=78 or sum(g[x] for x in X)>=82): return False
        elif sum(g[x] for x in X)<d[lev]: return False
    return True
def packs(ws):                            # two bins of capacity 6 (weights as given)
    ws=sorted(ws,reverse=True)
    def rec(i,a,b_):
        if i==len(ws): return True
        w=ws[i]
        if a+w<=6 and rec(i+1,a+w,b_): return True
        if b_+w<=6 and a!=b_ and rec(i+1,a,b_+w): return True
        if b_+w<=6 and a==b_ and False: return True
        return False
    return rec(0,0,0)
def bkill(s,b):
    rho=len(s)-b
    if b<4: return False
    X0=sorted(s)[:rho]                    # rho smallest
    if sum(g[x] for x in X0)>=53: return False   # lambda-independence not guaranteed
    return packs([x+2 for x in X0])
for b in range(5,9):
  for t in range(1,7):
    surv=[]
    for K in range(b,t+b+1):
      for sig in itertools.combinations_with_replacement(range(6),K):
        if sum(sig)>=6*b: continue
        s=sorted(sig,reverse=True)
        if size_ok(s,b) and not bkill(s,b): surv.append(tuple(s))
    best=min((sum(x) for x in surv),default=None)
    print(b,t,'nsurv',len(surv),'deficit',0 if best is None else 6*b-best, sorted(surv,key=sum)[:3],flush=True)

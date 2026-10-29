# deletion-lemma optimisation; level-1 (single codeword) test = EXACT cover oracle on targets |Off|<=72 (complete list, 4 orbit reps),
# size test with global caps for |Off|>=73. Levels >=2: size test (BUDGET-X, global g, d_b).
import itertools, json, pickle, sys, os, time
from covm import *
Gs={0:2,1:4,2:8,3:12,4:20,5:36}
d={1:53,2:76,3:92,4:100,5:106,6:109,7:111,8:112}
reps=json.load(open('reps.json'))
TG=[Target(off(H[i])) for i in reps if len(off(H[i]))<=72]
print('exact targets',[len(t.T) for t in TG],flush=True)
MEMO='memo5.pkl'; memo=pickle.load(open(MEMO,'rb')) if os.path.exists(MEMO) else {}
def oracle(sig):
    sig=tuple(sorted(sig,reverse=True))
    if sum(Gs[x] for x in sig)>=73: return True
    if sig not in memo:
        ws=[x+2 for x in sig]
        memo[sig]=any(tg.covers(ws) for tg in TG)
        pickle.dump(memo,open(MEMO,'wb'))
    return memo[sig]
def feasible(sig,b):
    a=sorted((Gs[x] for x in sig),reverse=True)
    for j in range(b-1):
        if sum(a[j:])<d[b-j]: return False
    return oracle(sorted(sig,reverse=True)[b-1:])
cells=[(b,t) for b in (3,4) for t in range(1,7)]
for b,t in cells:
    K=t+b; best=None; arg=None
    cand=[]
    for k in range(1,K+1):
        for sig in itertools.combinations_with_replacement(range(6),k):
            if sum(sig)<6*b: cand.append(sig)
    cand.sort(key=sum)
    for sig in cand:
        a=sorted((Gs[x] for x in sig),reverse=True)
        if any(sum(a[j:])<d[b-j] for j in range(b-1)): continue
        if feasible(sig,b): best=sum(sig); arg=sig; break
    print(b,t,'deficit',0 if best is None else 6*b-best,arg,flush=True)

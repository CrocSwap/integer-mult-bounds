# B167 plane-partner certificate (pure counting, any horizon) for every S1 block.
# Claim: a register z whose end-of-A row has support hull = a 4-point flat Pi (plane) and whose shipped bound is Pi must, at the meeting where
# its frame first exceeds a pair, meet a partner whose bound contains Pi (bound = whole, or another register bound exactly Pi).  If all
# plane-stoppers have DISTINCT planes, a whole-bound partner can serve at most one (after serving Pi1, its frame >= Pi1, so Pi1 <= Pi2).
# => #whole-bound registers >= #plane-stoppers.  This is Hall/matching on (stopper -> candidate partners).
exec(open((__import__('os').environ['HM_ROOT']+'/cards/B98c/work/gate.py')).read().split("good=[")[0])
import itertools
A=[list(e) for e in d['A']]
st=d['start']
cur=list(d['start'])
for e in A:
    f=e[-1]
    for q in regs(e):f=F.join(f,cur[q])
    for q in regs(e):cur[q]=f
def spanset(basis):
    s={0}
    for b in basis: s|={x^b for x in s}
    return s
rep=[]
for bn,rr in blocks.items():
    scr=list(rr); cols=sorted({j for r in scr for j in rows0[r]})
    if len(cols)!=8: rep.append((bn,'cols',len(cols))); continue
    vec={l:F.fr[st[l]][0] for l in cols}
    def hull(pts):
        sp=spanset([vec[p] for p in pts]); return frozenset(l for l in cols if vec[l] in sp)
    regsb=cols+scr
    B={r:frozenset(l for l in cols if vec[l] in spanset(F.fr[cur[r]])) for r in regsb}
    S={r:frozenset(rows0[r].keys()) for r in regsb}
    H={r:hull(S[r]) if S[r] else frozenset() for r in regsb}
    planes=[r for r in regsb if len(H[r])==4 and B[r]==H[r]]
    wide=[r for r in regsb if len(B[r])==8]
    pairs=[r for r in regsb if len(B[r])==2]
    # partner candidates for stopper z: registers != z with bound >= H[z]
    cand={z:[u for u in regsb if u!=z and H[z]<=B[u]] for z in planes}
    # max bipartite matching
    match={}
    def aug(z,seen):
        for u in cand[z]:
            if u in seen: continue
            seen.add(u)
            if u not in match or aug(match[u],seen): match[u]=z; return True
        return False
    msize=sum(aug(z,set()) for z in planes)
    distinct=len({H[z] for z in planes})==len(planes)
    rep.append((bn,len(cols),'scratch',len(scr),'wide',len(wide),'plane-stoppers',len(planes),'distinct',distinct,'matching',msize,'wide-scratch',len([r for r in wide if r in scr]),'cand-eq-wide',all(set(cand[z])==set(wide) for z in planes)))
for r in rep: print(r)

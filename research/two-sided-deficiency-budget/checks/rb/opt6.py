# opt5 + level-2 exact: 2-dim subcode supports with |S|<=81 are exactly P112\E6 (sizes 78/80, e6t.py); |S|>=82 size test, global caps.
exec(open('opt5.py').read().split('cells=')[0])
d[2]=78
E6=[Target(s) for s in json.load(open('e6reps.json'))]
MEMO2='memo6.pkl'; memo2=pickle.load(open(MEMO2,'rb')) if os.path.exists(MEMO2) else {}
def oracle2(sig):
    sig=tuple(sorted(sig,reverse=True))
    if sum(Gs[x] for x in sig)>=82: return True
    if sig not in memo2:
        memo2[sig]=any(tg.covers([x+2 for x in sig]) for tg in E6); pickle.dump(memo2,open(MEMO2,'wb'))
    return memo2[sig]
for b,t in [(4,t) for t in range(1,7)]:
    K=t+b; found=None
    cand=sorted([s for k in range(1,K+1) for s in itertools.combinations_with_replacement(range(6),k) if sum(s)<6*b],key=sum)
    for sig in cand:
        a=sorted((Gs[x] for x in sig),reverse=True); ss=sorted(sig,reverse=True)
        if any(sum(a[j:])<d[b-j] for j in range(b-1)): continue
        if b>=3 and not oracle2(ss[b-2:]): continue
        if oracle(ss[b-1:]): found=sig; break
    print(b,t,'deficit',0 if found is None else 6*b-sum(found),found,flush=True)

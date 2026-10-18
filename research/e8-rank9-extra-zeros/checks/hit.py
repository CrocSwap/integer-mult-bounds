# ZPIN3 hit.py: exact counts of frames avoiding given lines. E8 = 120 lines, 2025 frames.
import sys, itertools
from blib import *
FR=frames(); print('frames',len(FR))
# W(E8) is transitive on lines, on orthogonal pairs (CHECK: 3780 pairs all in frames); use the representative pair
f1=0; f2=min(O[0])
thr=[F for F in FR if f1 in F and f2 in F]; thf=[F for F in FR if f1 in F]
print('through line',len(thf),'through orth pair',len(thr))
# lines per frame count
from collections import Counter
cnt=Counter(x for F in thr for x in F if x not in (f1,f2)); print('pair: lines in frames through pair:',sorted(Counter(cnt.values()).items()),'#lines',len(cnt))
cnt1=Counter(x for F in thf for x in F if x!=f1); print('line: per-line counts',sorted(Counter(cnt1.values()).items()))
def hitnum(frs,cands,kmax):
    # min k such that k candidate lines meet every frame in frs; exact
    sets={c:frozenset(i for i,F in enumerate(frs) if c in F) for c in cands}
    full=frozenset(range(len(frs)))
    for k in range(1,kmax+1):
        for S in itertools.combinations(cands,k):
            if frozenset().union(*[sets[c] for c in S])==full: return k
    return None
print('pair: hitting number (lines != f1,f2) =',hitnum(thr,sorted(cnt),7))
print('line: hitting number through f1 (lines != f1) =',hitnum(thf,sorted(cnt1),4))
# frames through an orthogonal triple / minimal count avoiding up to 6 lines of pair frames: max coverage by k lines
for k in range(1,7):
    best=0
    sets={c:frozenset(i for i,F in enumerate(thr) if c in F) for c in cnt}
    for S in itertools.combinations(sorted(cnt),k):
        best=max(best,len(frozenset().union(*[sets[c] for c in S])))
    print('k',k,'max pair-frames killed',best,'of',len(thr))

"""SLACK run5 [C-param]: k>=1 survivors priced with rank 2 ONLY on intervals starting at the pair entry a=k (where rank 2 is EXACT, PROOF H),
rank 4 elsewhere; vs k=0 survivors with rank 3 only in the open case (ii)."""
import sys, io, contextlib; sys.path.insert(0,'.')
with contextlib.redirect_stdout(io.StringIO()):
    import step1
from icap import *
exec(open('run4.py').read().split('rows=[]')[0].split('import step1')[1].replace('from icap import *','').replace('from layout_price import invoice',''))
def mk(ms,k,d):
    Z=Zs(ms); K=d+1
    def r(a,b):
        ZI=frozenset.intersection(*Z[a:b+1])
        if any(Z[q]<=ZI or Z[q+1]<=ZI for q in range(a,b)): return 4
        return 2 if (a==k and b>=K) else 4
    return r
out=[]
for c in (2,1):
  for d in range(1,nl-2):
    for je in range(0,d+1):
      for eend in (d,nl-1):
        ms=step1.dying([('L',1,d,c,0)]); ms.append(set(range(je,eend+1)))
        if killed(ms,c,1,d): continue
        out.append((g(pr(ms,mk(ms,1,d))),'c=%d k=1 d=%d slack %d..%d'%(c,d,je,eend)))
  for d in range(2,nl-2):
    ms=step1.dying([('L',1,d,c,0)]); out.append((g(pr(ms,mk(ms,1,d))),'c=%d k=1 d=%d NO slack (DYINGPAIR-dead)'%(c,d)))
out.sort(reverse=True)
for t in out[:10]: print('  %+.2f  %s'%t)

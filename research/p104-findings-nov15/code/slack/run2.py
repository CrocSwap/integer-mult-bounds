"""SLACK run2 [C-param]: interval caps with r=4 wherever the Crossing Lemma provably applies on Z_I (some consecutive k,k+1 in I with
Z_k <= Z_I (X_k inside) or Z_k+1 <= Z_I (dual, Y_k+1 inside)), else r = rfail in {4,3,2}.  Layouts: step1b slack menu + lone roles."""
import sys, io, contextlib; sys.path.insert(0,'.')
with contextlib.redirect_stdout(io.StringIO()):
    import step1
from icap import *
from layout_price import invoice
def mk_r(ms, rfail):
    Z=[frozenset(i for i,m in enumerate(ms) if k in m) for k in range(L)]
    def r(a,b):
        ZI=frozenset.intersection(*Z[a:b+1])
        if any(Z[k]<=ZI or Z[k+1]<=ZI for k in range(a,b)): return 4
        return rfail
    return r
B=None
def row(ms):
    T,P,Z=invoice(ms,L,step1.capS(ms)); o=[price(T,P,'',quiet=True)]
    for rf in (4,3,2):
        T,P,Z=invoice_iv(ms,mk_r(ms,rf)); o.append(price(T,P,'',quiet=True))
    return o
B=row(two_arm())[0]
g=lambda r:100*(min(x/y for x,y in zip(r,B))-1)
print('cols: boundary-cap(old) | interval r_fail=4 | r_fail=3 | r_fail=2   (min ratio over td/sh/rel vs B, %)')
res=[]
for c in (2,1):
  for k in (0,1):
    for d in range(max(k,1),nl-2):
      for je in range(k+1 if k==0 else 0, d+1):
        for eend in (d, nl-1):
          ms=step1.dying([('L',k,d,c,0)]); ms.append(set(range(je,eend+1)))
          o=row(ms); res.append((g(o[0]),'c=%d k=%d d=%d slack %d..%d'%(c,k,d,je,eend),[g(x) for x in o]))
for je in range(0,nl-1):
  for ee in range(je+1,nl-1):
    ms=two_arm(); ms.append(set(range(je,ee+1))); o=row(ms); res.append((g(o[0]),'B + lone %d..%d'%(je,ee),[g(x) for x in o]))
res.sort(reverse=True)
for t in sorted(res,key=lambda t:-t[2][1])[:6]+[t for t in res if "lone" in t[1]][:8]: print('%-32s'%t[1], ' | '.join('%+.2f'%x for x in t[2]))
print('max over all layouts per column:', ['%+.2f'%max(t[2][i] for t in res) for i in range(4)])

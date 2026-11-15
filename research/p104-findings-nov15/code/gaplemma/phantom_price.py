"""GAPLEMMA phantom_price.py [C-param]: price family A (c=1 k=1 d, slack 0..d) as modelled (run6 caps) vs with the
dying single D made a PHANTOM (empty left mask: content only in thin units), lone-role rank 4 caps (PROOF E)."""
import sys, io, contextlib, os
_SLACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'slack'); os.chdir(_SLACK); sys.path.insert(0, _SLACK)
with contextlib.redirect_stdout(io.StringIO()):
    import step1
from icap import *
def pr(ms,r):
    T,P,Z=invoice_iv(ms,r); return price(T,P,'',quiet=True)
B=pr(two_arm(),lambda a,b:4); g=lambda x:100*(min(p/q for p,q in zip(x,B))-1)
for d in range(1,6):
    ms=step1.dying([('L',1,d,1,0)]); ms.append(set(range(0,d+1)))
    a=g(pr(ms,lambda a,b:4))
    i=[j for j,m in enumerate(ms) if m==set(range(1,d+1))][0]; ms2=list(ms); ms2[i]=set()
    try: b=g(pr(ms2,lambda a,b:4))
    except Exception as ex: b=float('nan'); print('err',ex)
    print('d=%d  modelled(rank4) %+.2f   phantom D %+.2f'%(d,a,b))
print('--- phantom case priced with run6 conservative caps but D excluded from u (inert D gives no constraint row):')
def Zs(ms): return [frozenset(i for i,m in enumerate(ms) if k in m) for k in range(L)]
for d in range(1,6):
    ms=step1.dying([('L',1,d,1,0)]); ms.append(set(range(0,d+1))); Z=Zs(ms); idx=range(len(ms))
    Di=[j for j,m in enumerate(ms) if m==set(range(1,d+1))][0]
    def mk(skipD):
        def r(a,b):
            ZI=frozenset.intersection(*Z[a:b+1])
            if any(Z[q]<=ZI or Z[q+1]<=ZI for q in range(a,b)): return 4
            Om=[i for i in idx if min(ms[i])<=a and i not in ZI and not (skipD and i==Di)]
            return 4-min(2,len(Om))
        return r
    print('d=%d  run6-style caps %+.2f   D inert (u counts s only) %+.2f'%(d,g(pr(ms,mk(False))),g(pr(ms,mk(True)))))
print('--- phantom case, PROVED caps (PROOF.md P3): rank 4 on every interval except a=0 across the death (rank >= 3):')
for d in range(1,6):
    ms=step1.dying([('L',1,d,1,0)]); ms.append(set(range(0,d+1))); Z=Zs(ms)
    si=len(ms)-1
    def r(a,b):
        ZI=frozenset.intersection(*Z[a:b+1])
        if any(Z[q]<=ZI or Z[q+1]<=ZI for q in range(a,b)): return 4
        return 3 if (a==0 and si not in ZI) else 4
    print('d=%d  phantom proved caps %+.2f'%(d,g(pr(ms,r))))
print('--- family A, b=2 (open case), PROVED caps P4: rank >= 3 on every interval across the death (x~_0s != 0 kills the 2-drop):')
for d in range(1,6):
    ms=step1.dying([('L',1,d,1,0)]); ms.append(set(range(0,d+1))); Z=Zs(ms)
    def r(a,b):
        ZI=frozenset.intersection(*Z[a:b+1])
        return 4 if any(Z[q]<=ZI or Z[q+1]<=ZI for q in range(a,b)) else 3
    print('d=%d  b=2 caps r>=3 %+.2f'%(d,g(pr(ms,r))))
print("--- family A' (slack survives, Delta={D}): run6 caps vs r=3")
for je in (0,1):
  for d in range(1,6):
    ms=step1.dying([('L',1,d,1,0)]); ms.append(set(range(je,nl))); Z=Zs(ms)
    def r(a,b):
        ZI=frozenset.intersection(*Z[a:b+1])
        return 4 if any(Z[q]<=ZI or Z[q+1]<=ZI for q in range(a,b)) else 3
    print("A' je=%d d=%d  r=3 caps %+.2f"%(je,d,g(pr(ms,r))))

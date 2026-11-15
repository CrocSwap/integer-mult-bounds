"""SLACK run4 [C-param on P-caps, PROOF.md G]: survivors of run3 repriced with the PROVED interval ranks:
 r=4 (Lemma B criterion, or PROOF G) except: (i) intervals starting at a=k>=1 (pair entry): r=2 [unproved];
 (ii) slack dying at K with je<=a<=d, je>k: r=3 [G: drop <= 1, case t(v)=a open]; (iii) slack entering <= k: r=2 [not analysed]."""
import sys, io, contextlib; sys.path.insert(0,'.')
with contextlib.redirect_stdout(io.StringIO()):
    import step1
from icap import *
from layout_price import invoice
def Zs(ms): return [frozenset(i for i,m in enumerate(ms) if k in m) for k in range(L)]
def mkr(ms,k,d,je,eend,mode):
    Z=Zs(ms); K=d+1
    def r(a,b):
        ZI=frozenset.intersection(*Z[a:b+1])
        if any(Z[q]<=ZI or Z[q+1]<=ZI for q in range(a,b)): return 4
        if not (a<=d and b>=K): return 4 if mode=='opt' else 2   # no death crossed but criterion fails: not expected
        if a==k and k>=1: return 2 if mode!='opt' else 4
        if je<=k: return 2 if mode!='opt' else 4
        if eend==d and je<=a<=d: return 3 if mode!='opt' else 4
        return 4
    return r
B=None
def pr(ms,r):
    T,P,Z=invoice_iv(ms,r); return price(T,P,'',quiet=True)
B=pr(two_arm(),lambda a,b:4)
g=lambda x:100*(min(p/q for p,q in zip(x,B))-1)
def U(ms,j): return sum(1 for m in ms if min(m)<=j)
left=lambda ms:[m for m in ms if max(m)<nl]
def killed(ms,c,k,d):
    K=d+1; ZK=sum(1 for m in ms if K in m); Dall=sum(1 for m in left(ms) if min(m)<=d and K not in m)
    return ZK+Dall-c<=2*K+3 and all(U(ms,j-1)<=2*j+2 for j in range(k+1,d+1))
rows=[]
for c in (2,1):
  for k in (0,1):
    for d in range(max(k,1),nl-2):
      for je in range(k+1 if k==0 else 0, d+1):
        for eend in (d, nl-1):
          ms=step1.dying([('L',k,d,c,0)]); ms.append(set(range(je,eend+1)))
          if killed(ms,c,k,d): continue
          rows.append(('c=%d k=%d d=%d slack %d..%d'%(c,k,d,je,eend), g(pr(ms,mkr(ms,k,d,je,eend,'proved'))), g(pr(ms,mkr(ms,k,d,je,eend,'opt')))))
rows.sort(key=lambda t:-t[1])
print('survivors: proved-cap ceiling | all-rank-4 price')
for t in rows[:12]: print('  %-28s %+.2f | %+.2f'%t)
print('max proved-cap ceiling %+.2f; count >= +0.5%%: %d of %d'%(rows[0][1], sum(1 for t in rows if t[1]>=0.5), len(rows)))
k0=[t for t in rows if ' k=0 ' in t[0]]
print('k=0 only: max proved %+.2f (%s); >=0.5: %d of %d'%(k0[0][1],k0[0][0],sum(1 for t in k0 if t[1]>=0.5),len(k0)))
for t in k0[:5]: print('  %-28s %+.2f | %+.2f'%t)

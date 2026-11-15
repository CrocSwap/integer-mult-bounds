"""SLACK run3 [P-criterion + C-param]: apply the refined DYINGPAIR kill (PROOF.md here) to the slack menu, price the survivors.
Kill (dying set D of c roles entering k, dead at K=d+1; D_all = all left roles of U_d absent from Z_K):
 (S1) |Z_K| + |D_all| - c <= 2K+3   (forces 0 != v in V cap R^D)   and   (S3') |U_{j-1}| <= 2j+2 for every k < j <= d.
Lone role (no dying pair): killed iff window length 1 (top index = entry stage, sum-zero)."""
import sys, io, contextlib; sys.path.insert(0,'.')
with contextlib.redirect_stdout(io.StringIO()):
    import step1
from icap import *
from layout_price import invoice
def mk_r(ms, rfail):
    Z=[frozenset(i for i,m in enumerate(ms) if k in m) for k in range(L)]
    def r(a,b):
        ZI=frozenset.intersection(*Z[a:b+1])
        return 4 if any(Z[k]<=ZI or Z[k+1]<=ZI for k in range(a,b)) else rfail
    return r
def row(ms):
    T,P,Z=invoice(ms,L,step1.capS(ms)); o=[price(T,P,'',quiet=True)]
    for rf in (4,3,2):
        T,P,Z=invoice_iv(ms,mk_r(ms,rf)); o.append(price(T,P,'',quiet=True))
    return o
B=row(two_arm())[0]
g=lambda r:100*(min(x/y for x,y in zip(r,B))-1)
left=lambda ms:[m for m in ms if min(m)<nl and max(m)<nl]
def U(ms,j): return sum(1 for m in ms if min(m)<=j)
def killed(ms,c,k,d):
    K=d+1; ZK=sum(1 for m in ms if K in m); Dall=sum(1 for m in left(ms) if min(m)<=d and K not in m)
    return ZK+Dall-c<=2*K+3 and all(U(ms,j-1)<=2*j+2 for j in range(k+1,d+1))
surv=[]; nk=0; nall=0
for c in (2,1):
  for k in (0,1):
    for d in range(max(k,1),nl-2):
      for je in range(k+1 if k==0 else 0, d+1):
        for eend in (d, nl-1):
          ms=step1.dying([('L',k,d,c,0)]); ms.append(set(range(je,eend+1))); nall+=1
          if killed(ms,c,k,d): nk+=1; continue
          o=row(ms); surv.append(('c=%d k=%d d=%d slack %d..%d'%(c,k,d,je,eend),[g(x) for x in o]))
for je in range(0,nl-1):
  for ee in range(je+1,nl-1):
    ms=two_arm(); ms.append(set(range(je,ee+1))); o=row(ms); surv.append(('B + lone %d..%d'%(je,ee),[g(x) for x in o]))
print('slack menu: killed %d of %d by refined theorem'%(nk,nall))
print('survivors (cols: old boundary caps | interval r_fail=4 | 3 | 2), top by r_fail=4 then r_fail=3:')
for t in sorted(surv,key=lambda t:-t[1][1])[:8]: print('  %-30s'%t[0],' | '.join('%+.2f'%x for x in t[1]))
for t in sorted(surv,key=lambda t:-t[1][2])[:5]: print('  %-30s'%t[0],' | '.join('%+.2f'%x for x in t[1]))
print('max over survivors per column:', ['%+.2f'%max(t[1][i] for t in surv) for i in range(4)])

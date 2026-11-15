"""SLACK run6 [P-caps + C-param]: CONSERVATIVE proved interval ranks for the whole pair/single + slack menu.
 r(I) = 4 if Lemma B criterion; else 4 - min(2, u), u = #roles of Omega_a = U_a \\ Z_I NOT certified touched by X_{<a}
 (PROOF.md H: test (1); certified = the dying set entering k<a when |U_k| = 2k+4, since X~_k[D] is then invertible by F1).
 Kills: refined DYINGPAIR (run3) OR generalized G-kill: Delta = all roles of U_d dead at K, all entering at one stage k', 2K+4-|Z_K| >= 1,
 |U_{t-1}| <= 2t+2 for k' < t <= d (top index on v in V cap R^Delta; recursion at k')."""
import sys, io, contextlib; sys.path.insert(0,'.')
with contextlib.redirect_stdout(io.StringIO()):
    import step1
from icap import *
def Zs(ms): return [frozenset(i for i,m in enumerate(ms) if k in m) for k in range(L)]
def pr(ms,r):
    T,P,Z=invoice_iv(ms,r); return price(T,P,'',quiet=True)
B=pr(two_arm(),lambda a,b:4); g=lambda x:100*(min(p/q for p,q in zip(x,B))-1)
def U(ms,j): return sum(1 for m in ms if min(m)<=j)
left=lambda ms:[m for m in ms if max(m)<nl]
def killed(ms,c,k,d):
    K=d+1; ZK=sum(1 for m in ms if K in m); Dl=[m for m in left(ms) if min(m)<=d and K not in m]
    old= ZK+len(Dl)-c<=2*K+3 and all(U(ms,j-1)<=2*j+2 for j in range(k+1,d+1))
    ents={min(m) for m in Dl}
    new= len(ents)==1 and 2*K+4-ZK>=1 and all(U(ms,t-1)<=2*t+2 for t in range(min(ents)+1,d+1))
    return old or new
def mkr(ms,k,d,c):
    Z=Zs(ms); idx=list(range(len(ms)))
    cert=set()
    if U(ms,k)==2*k+4: cert={i for i in idx if min(ms[i])==k and max(ms[i])==d and len(ms[i])==d-k+1}  # dying set
    def r(a,b):
        ZI=frozenset.intersection(*Z[a:b+1])
        if any(Z[q]<=ZI or Z[q+1]<=ZI for q in range(a,b)): return 4
        Om=[i for i in idx if min(ms[i])<=a and i not in ZI]
        u=sum(1 for i in Om if not (i in cert and k<a))
        return 4-min(2,u)
    return r
rows=[]
for c in (2,1):
  for k in (0,1):
    for d in range(max(k,1),nl-2):
      for je in range(0, d+1):
        for eend in (d, nl-1):
          if k==0 and je==0: continue
          ms=step1.dying([('L',k,d,c,0)]); ms.append(set(range(je,eend+1)))
          if killed(ms,c,k,d): continue
          rows.append((g(pr(ms,mkr(ms,k,d,c))),'c=%d k=%d d=%d slack %d..%d'%(c,k,d,je,eend)))
rows.sort(reverse=True)
print('survivors %d; proved-cap ceilings (top 12):'%len(rows))
for t in rows[:12]: print('  %+.2f  %s'%t)
print('count >= +0.5%%: %d'%sum(1 for t in rows if t[0]>=0.5))

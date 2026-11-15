"""GAPLEMMA dfloor.py [P-criterion + C-param]: Delta-Floor kill (PROOF.md here) on the SLACK run6 menu.
Kill if exists 1<=i<=d:  |Delta_{i-1}| < 2i+4 - |U_i minus Delta|   (Delta = left roles of U_d absent from Z_K, K=d+1)."""
import sys, io, contextlib
import os; _SLACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'slack'); os.chdir(_SLACK); sys.path.insert(0, _SLACK)
with contextlib.redirect_stdout(io.StringIO()):
    import run6
from run6 import *
def dkill(ms,d):
    K=d+1; lm=[m for m in left(ms)]
    Dl=[m for m in lm if min(m)<=d and K not in m]
    for i in range(0,d+1):
        Ui=[m for m in ms if min(m)<=i and min(m)<nl] ; UiD=[m for m in Ui if m not in Dl]
        Uim=sum(1 for m in ms if min(m)<=i)  # all roles entered by i (hubs incl.)
        Dim1=sum(1 for m in Dl if min(m)<=i-1)
        Dn=sum(1 for m in Dl if min(m)<=i)
        if Dim1 < 2*i+4-(Uim-Dn): return i
    return None
rows=[];nk=0
for c in (2,1):
  for k in (0,1):
    for d in range(max(k,1),nl-2):
      for je in range(0,d+1):
        for eend in (d,nl-1):
          if k==0 and je==0: continue
          ms=step1.dying([('L',k,d,c,0)]); ms.append(set(range(je,eend+1)))
          if killed(ms,c,k,d): continue
          lab='c=%d k=%d d=%d slack %d..%d'%(c,k,d,je,eend); p=g(pr(ms,mkr(ms,k,d,c)))
          i=dkill(ms,d)
          if i is None: rows.append((p,lab))
          else: nk+=1
rows.sort(reverse=True)
print('run6 survivors killed by Delta-Floor:',nk,'remaining',len(rows))
for t in rows[:15]: print('  %+.2f  %s'%t)
print('remaining >= +0.5%%: %d'%sum(1 for t in rows if t[0]>=0.5))

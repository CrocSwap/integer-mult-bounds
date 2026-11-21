"""DYADRELAY dr2: SUB-DYADIC rows (local CROSS averaged over random stage sets) added to INTCALLER's aggregated IP (ic4).
SUBDY_{d,J} [P from SK CROSS]: for every stage set M (|M|=d), the dyadic tree on M's rank order (levels 0..J) gives CROSS nodes
(X,Y) with c = floor(|Z|/2); sum over nodes: sum_r branch_r(M) >= R_J(d), branch_r <= (min(|M_r cap M|,2^{J+1})-1)^+.
Average over uniform M:  sum_r E_{i~HG(k,D_r,d)} (min(i,2^{J+1})-1)^+  >=  R_J(d).   d=k: DYADIC_J.
usage: dr2.py k...  env DS (comma d list; default dense), JM (max J), plus ic4 env (TUR)."""
import os,sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','intcaller'))
from fractions import Fraction as Fr
from math import comb,ceil,log2
import ic1
_orig=ic1.rowdefs
def dset(k):
    e=os.environ.get('DS')
    if e:return sorted(set(int(a) for a in e.split(',') if 2<=int(a)<=k))
    return list(range(2,k+1))
_cache={}
def coef(k,d,J,D):
    key=(k,d,J,D)
    if key not in _cache:
        tot=comb(k,d);cap=2**(J+1)
        _cache[key]=Fr(sum(comb(D,i)*comb(k-D,d-i)*max(0,min(i,cap)-1) for i in range(0,min(D,d)+1)),tot)
    return _cache[key]
def newrows(k):
    R=[]
    for d in dset(k):
        Jm=max(0,ceil(log2(d))-1)
        if os.environ.get('JM'):Jm=min(Jm,int(os.environ['JM']))
        for J in range(0,Jm+1):
            R.append(('SUBDY_%d_%d'%(d,J),lambda D,P,d=d,J=J:coef(k,d,J,D),0,'>=',Fr(ic1.RJ(d,J))))
    return R
def rowdefs(k):
    R=_orig(k);tail=R[-2:];return R[:-2]+(newrows(k) if os.environ.get('NEW','1')=='1' else [])+tail
ic1.rowdefs=rowdefs
import ic3,ic4
if __name__=='__main__':
    src=open(ic4.__file__).read().split("if __name__=='__main__':")[1]
    import textwrap;exec(textwrap.dedent(src),ic4.__dict__)

"""DYADRELAY dr4: ic4 aggregated exact IP + SUBDY (dr2, env NEW=1/0) + averaged SPARSE_u rows (MASKK13, env SP=1/0):
SPARSE [P, MK13]: #roles with mask inside U <= 2|U|-2 for every stage set U.  Averaged over uniform u-sets:
   sum_r C(k-D_r,u-D_r)/C(k,u) <= 2u-2   (u=2..k-1; u=k is the role count).  usage: dr4.py k..."""
import os,sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','intcaller'))
from fractions import Fraction as Fr
from math import comb
import ic1,dr2   # dr2 patches ic1.rowdefs with SUBDY (NEW=1 default)
_o=ic1.rowdefs
def rowdefs(k):
    R=_o(k);tail=R[-2:];add=[]
    if os.environ.get('SP','1')=='1':
        for u in range(2,k):
            add.append(('SPARSE_%d'%u,lambda D,P,u=u:-Fr(comb(k-D,u-D),comb(k,u)) if D<=u else Fr(0),0,'>=',Fr(-(2*u-2))))
    return R[:-2]+add+tail
ic1.rowdefs=rowdefs
import ic3,ic4
if __name__=='__main__':
    src=open(ic4.__file__).read().split("if __name__=='__main__':")[1]
    import textwrap;exec(textwrap.dedent(src),ic4.__dict__)

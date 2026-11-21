"""DYADRELAY dr1: add the SET-RELAY rows RC2Y_{l,y} to INTCALLER's exact aggregated IP (ic4) and re-solve.
RC2Y_{l,Y} pair form [P, see DR.md 1]: for every stage s, every nonempty Y in [k]-{s}, every l>=2:
   #{r in E_s : |P_r(s)|<l, P_r(s) cap Y = 0, (D_r>=l or (M_r-P_r(s)) cap Y != 0)} >= 2.
Averaged over Y uniform among y-subsets of [k]-{s}, summed over s:
   sum_r sum_{pieces L} L*g(L,D) >= 2k,  g = [D>=l][L<l] C(k-L,y)/C(k-1,y) + [D<l](C(k-L,y)-C(k-D,y))/C(k-1,y).
y=1 is RC2_l.  usage: dr1.py k...   env YS=comma list of y (default dense), LS=comma list of l (default all 3..k+1)."""
import os,sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','intcaller'))
from fractions import Fraction as Fr
from math import comb
import ic1
_orig=ic1.rowdefs
def yset(k):
    e=os.environ.get('YS')
    if e:return sorted(set(min(int(a),k-1) for a in e.split(',')))
    ys=set([1,2,3,4,5,6,8,10,12,16,20,24,32,40,48,64,k-1])|set(range(1,min(k,12)))
    return sorted(y for y in ys if 1<=y<=k-1)
def lset(k):
    e=os.environ.get('LS')
    if e:return [int(a) for a in e.split(',')]
    return list(range(3,k+2))
def g(k,l,y,D,L):
    den=comb(k-1,y)
    if D>=l:return Fr(comb(k-L,y),den) if L<l else Fr(0)
    return Fr(comb(k-L,y)-comb(k-D,y),den)
def newrows(k):
    R=[]
    for y in yset(k):
        if y==1:continue   # = RC2_l already present
        for l in lset(k):
            R.append(('RC2Y_%d_%d'%(l,y),lambda D,P,l=l,y=y:sum(L*g(k,l,y,D,L) for L in P),0,'>=',Fr(2*k)))
    return R
def rowdefs(k):
    R=_orig(k);tail=R[-2:];return R[:-2]+(newrows(k) if os.environ.get('NEW','1')=='1' else [])+tail
ic1.rowdefs=rowdefs
import ic3,ic4
if __name__=='__main__':
    sys.argv=[sys.argv[0]]+sys.argv[1:]
    src=open(ic4.__file__).read().split("if __name__=='__main__':")[1]
    import textwrap;exec(textwrap.dedent(src),ic4.__dict__)

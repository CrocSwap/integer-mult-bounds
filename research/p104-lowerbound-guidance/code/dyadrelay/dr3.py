"""DYADRELAY dr3: SUBDY with level weights (adds to dr2's SUBDY rows). For weight vector w (levels 0..J) the CROSS nodes of M's
dyadic tree give  sum_r credit_r^w(M) >= sum_l w_l RHS_l(d);  credit^w <= max over class profiles n_0=1<=n_1<=...,
n_{l+1}<=min(2n_l,2^{l+1},i) of sum_l w_l (n_{l+1}-n_l), i=|M_r cap M|.  Averaged over uniform M (i ~ HG(k,D,d)).
usage like dr2; env WS='1,2;2,1;...' (weight vectors), DS (d list)."""
import os,sys
for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[v]='1'
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','intcaller'))
from fractions import Fraction as Fr
from math import comb
from functools import lru_cache
import ic1,dr2
def rhs_level(d,l):return sum(2*(len(range(j,d,2**l))//2) for j in range(2**l))
@lru_cache(None)
def prof(i,w):
    if i<=1:return 0
    J=len(w)-1;best={1:0}
    for l in range(J+1):
        nb={}
        for n,v in best.items():
            for m in range(n,min(2*n,2**(l+1),i)+1):
                val=v+w[l]*(m-n)
                if nb.get(m,-1)<val:nb[m]=val
        best=nb
    return max(best.values())
_c={}
def coefw(k,d,w,D):
    key=(k,d,w,D)
    if key not in _c:_c[key]=Fr(sum(comb(D,i)*comb(k-D,d-i)*prof(i,w) for i in range(0,min(D,d)+1)),comb(k,d))
    return _c[key]
def wsets():
    e=os.environ.get('WS','1,2;2,1;1,1,2;1,2,2;1,2,3;1,1,1,2;1,2,2,2;1,1,2,2')
    return [tuple(int(a) for a in s.split(',')) for s in e.split(';')]
_o=ic1.rowdefs
def rowdefs(k):
    R=_o(k);tail=R[-2:];add=[]
    for d in dr2.dset(k):
        for w in wsets():
            J=len(w)-1
            if 2**J>=d:continue
            add.append(('SUBW_%d_%s'%(d,'-'.join(map(str,w))),lambda D,P,d=d,w=w:coefw(k,d,w,D),0,'>=',Fr(sum(w[l]*rhs_level(d,l) for l in range(J+1)))))
    return R[:-2]+add+tail
ic1.rowdefs=rowdefs
import ic3,ic4
assert all(rhs_level(d,0)+rhs_level(d,1)==ic1.RJ(d,1) for d in range(2,40))
assert all(prof(i,(1,1,1))==min(i,8)-1 for i in range(1,20))
if __name__=='__main__':
    src=open(ic4.__file__).read().split("if __name__=='__main__':")[1]
    import textwrap;exec(textwrap.dedent(src),ic4.__dict__)

import os as _os; ROOT=_os.path.abspath(_os.path.join(_os.path.dirname(__file__),'..','..'))
# B214 Q1: exact I-K structure on the E8^2 norm-4 shell (K=(t^3-4t)/48 kernel, compensation_rank.py:30-45).
import sys;sys.dont_write_bytecode=True
NM=ROOT+'/research/niemeier-lattices'
sys.path.insert(0,NM+'/code')
import numpy as np, e8_cubed as e
from collections import Counter
roots,fourth,ports,profiles=e.construct_shell()
P=ports[(profiles&4)==0,:16].astype(np.int64)     # same selection as compensation_rank.py:11
N=len(P);print('N',N,'doubled coords, norms',Counter((P*P).sum(1)))
blockA=(np.abs(P[:,8:]).sum(1)==0)|(np.abs(P[:,:8]).sum(1)==0)
print('class sizes: single-block(norm4 in one E8)',blockA.sum(),' root x root',(~blockA).sum())
# t = raw/4 ; K = (t^3-4t)/48 ; (compensation_rank.py:42-43) raw = P.P ; diag raw=16 -> t=4 -> K=1
def Kval(t): return (t**3-4*t)/48.0
hist={}
for cls,name in ((blockA,'single'),(~blockA,'rootroot')):
    idx=np.flatnonzero(cls)
    # all rows of class are equivalent under the symmetry group only if transitive; check 6 random rows per class
    rng=np.random.default_rng(1);rows=rng.choice(idx,6,replace=False)
    for r in rows:
        raw=P@P[r]; t=raw//4
        assert not (raw%4).any()
        c=Counter(t.tolist()); hist.setdefault(name,[]).append(tuple(sorted(c.items())))
    print(name,'distinct row t-histograms among 6 samples:',len(set(hist[name])));print('  ',hist[name][0])
# exact nnz of I-K : count entries with K != 0 off the diagonal over ALL rows (P@P.T in 1000-row chunks)
cnt=Counter();rowdeg=np.zeros(N,dtype=np.int64)
for s in range(0,N,1500):
    raw=P[s:s+1500]@P.T; t=raw//4
    for v in np.unique(t): cnt[int(v)]+=int((t==v).sum())
    nz=(np.abs(t)==1)|(np.abs(t)==3)|(np.abs(t)>=4)&(t!=4)
    rowdeg[s:s+1500]=nz.sum(1)
print('global t histogram (ordered pairs incl diag):',sorted(cnt.items()))
print('K value per t:',{t:Kval(t) for t in sorted(cnt)})
nnz=sum(c for t,c in cnt.items() if t!=4 and abs(Kval(t))>1e-12);print('nnz(offdiag K)=nnz(I-K)=',nnz,' per port',nnz/N,' diag of I-K is zero:',Kval(4)==1)
print('row degree min/max',rowdeg.min(),rowdeg.max())
np.save('b214_P.npy',P)

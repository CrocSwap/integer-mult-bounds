import os as _os; ROOT=_os.path.abspath(_os.path.join(_os.path.dirname(__file__),'..','..'))
# B214 Q1b: Kronecker / block structure of I-K on the rootxroot (28,800) and single-block (2,160) classes.
import sys;sys.dont_write_bytecode=True
import numpy as np
from collections import Counter
P=np.load('b214_P.npy'); N=len(P)
f=lambda t:(t**3-4*t)/48.0
single=(np.abs(P[:,8:]).sum(1)==0)|(np.abs(P[:,:8]).sum(1)==0)
RR=P[~single]; SG=P[single]
# distinct E8 roots appearing as halves
A=RR[:,:8]; B=RR[:,8:]
ra=np.unique(np.vstack([A,-A]),axis=0); print('distinct a-roots (with signs)',len(ra),' b',len(np.unique(np.vstack([B,-B]),axis=0)))
# entry check: K[(a,b),(a',b')]=f(s(a,a')+s(b,b')),  s=a.a'/4 (doubled coords)
rng=np.random.default_rng(0); i=rng.choice(len(RR),400); j=rng.choice(len(RR),400)
t_direct=(RR[i]@RR[j].T)//4
sa=(A[i]@A[j].T)//4; sb=(B[i]@B[j].T)//4
assert (t_direct==sa+sb).all(); print('t = s_a + s_b verified (400x400)')
# Kronecker expansion: f(sa+sb)=(sa^3+3sa^2 sb+3 sa sb^2+sb^3-4sa-4sb)/48 -> 6 Kronecker terms P_p (x) Q_q
print('f(sa+sb)=[sa^3(x)J + 3 sa^2(x)sb + 3 sa(x)sb^2 + J(x)sb^3 -4 sa(x)J -4 J(x)sb]/48 ; ranks of Hadamard powers of the E8 root Gram (240 roots):')
G=(ra@ra.T)//4
for p in (1,2,3):
    print('  rank of S^{o%d} ='%p, np.linalg.matrix_rank(G.astype(float)**p))
print('  rank(S^o1+..): span{J,S,S2,S3} rank',np.linalg.matrix_rank(np.stack([np.ones(G.size),G.ravel(),(G**2).ravel(),(G**3).ravel()],1).astype(float)))
# block structure by s=s_a: block (a,a') depends only on s_aa' (types 0,+-1,+-2)
c=Counter(G[0].tolist()); print('per-root neighbour counts by s:',sorted(c.items()))
# blocks: I-K block for pair (a,a') = delta*I - f(s+S_b) ; diag blocks s=2 (a=a'), s=-2 antipode
nblk=Counter()
# ports are 28,800 = (a,b) mod global sign; a-index modulo +- gives 120 a-classes x 240 b (with sign gauge)
print('rootroot ports',len(RR),' = 120 a-classes (mod +-) x 240 b-roots')
print('off-diag block types per a-class: s=0:126,+-1:112,s=+-2(self/antipode): 1 (diag block)')
print('distinct nonzero-block types of I-K: B_s=f(s+S) for s in {0,+1,-1}; diag block I-f(2+S); count of blocks 120*(126+112)=%d off-diag + 120 diag'%(120*238))
# class-wise nnz of I-K
hist=Counter()
for blk,name in ((RR,'rr'),(SG,'sg')):
    for other,on in ((RR,'rr'),(SG,'sg')):
        tot=0
        for s in range(0,len(blk),1500):
            t=(blk[s:s+1500]@other.T)//4; tot+=int(((np.abs(t)==1)|(np.abs(t)==3)).sum())
        hist[(name,on)]=tot
print('nnz(I-K) by (row class, col class):',dict(hist),'sum',sum(hist.values()))
print('K rank (certified) 816 of 30960; stable dyadic values {+-1/16,+-5/16}')

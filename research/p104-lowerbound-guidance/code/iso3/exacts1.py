"""ISO3 exacts1: RIGOROUS upper bound on max over ALL 2-power gauges of S1 = alpha+beta.
For fixed row shifts s: a port t can carry a-digits only for rows in argmin_k(VW(t,k)+s_k) (when c_t = its lower end) and
b-digits only for rows in argmin_k(VU(t,k)-s_k) (upper end). Rank is monotone in the set of nonzero rows (each port row is a fixed vector),
so S1(s,c,e) <= UB(s) := rank{a-rows, all t} + rank{b-rows, all t}. UB depends on s only via comparisons of s_k-s_j with
thresholds in [-R,R] (R = max spread of finite VW, VU values), so s may be taken with sorted gaps in {0,1,..,R+1} (gap compression).
Enumerate all ordered set partitions of rows x gap labels."""
import sys, pickle, itertools, numpy as np
from gmax import *
def ordered_partitions(items):
    if not items: yield []; return
    first=items[0]
    for p in ordered_partitions(items[1:]):
        for i in range(len(p)):            # put first into existing block i
            yield p[:i]+[p[i]+[first]]+p[i+1:]
        for i in range(len(p)+1):          # new singleton block at position i
            yield p[:i]+[[first]]+p[i:]
def run(rows,Q):
    n=len(Q); m=len(rows); VW,VU=vals(rows,n)
    D=[[t for t in range(n) if VW[t,k]<BIG] for k in range(m)]; S=[[t for t in range(n) if VU[t,k]<BIG] for k in range(m)]
    fin=lambda A: A[A<BIG]
    R=max(max(int(fin(VW[:,k]).max()-fin(VW[:,k]).min()) if len(fin(VW[:,k])) else 0 for k in range(m)),0)
    R=max(int(VW[VW<BIG].max()-VW[VW<BIG].min()), int(VU[VU<BIG].max()-VU[VU<BIG].min()))
    # port row-vectors per row k: a-side block = Q[t,S_k]; b-side: column t of Q[D_k,:] (as a vector of length |D_k|)
    widthA=[len(S[k]) for k in range(m)]; offA=np.cumsum([0]+widthA)
    widthB=[len(D[k]) for k in range(m)]; offB=np.cumsum([0]+widthB)
    blkA=[[int(''.join(map(str,Q[t,S[k]])),2)<<int(offA[k]) if S[k] else 0 for k in range(m)] for t in range(n)]
    blkB=[[int(''.join(map(str,Q[D[k],t])),2)<<int(offB[k]) if D[k] else 0 for k in range(m)] for t in range(n)]
    def rank(vs):
        piv={}; r=0
        for x in vs:
            while x:
                h=x.bit_length()-1
                if h in piv: x^=piv[h]
                else: piv[h]=x; r+=1; break
        return r
    cacheA={}; cacheB={}; best=-1; bests=None; cnt=0
    for part in ordered_partitions(list(range(m))):
        L=len(part)
        for gaps in itertools.product(range(1,R+2),repeat=L-1):
            s=np.zeros(m,dtype=np.int64); v=0
            for i,blk in enumerate(part):
                if i>0: v+=gaps[i-1]
                for k in blk: s[k]=v
            cnt+=1
            Aw=VW+s[None,:]; Bu=VU-s[None,:]
            ka=tuple((Aw==Aw.min(1,keepdims=True)).astype(np.int8).ravel()); kb=tuple((Bu==Bu.min(1,keepdims=True)).astype(np.int8).ravel())
            if ka not in cacheA:
                M=np.array(ka).reshape(n,m); cacheA[ka]=rank([sum(blkA[t][k] for k in range(m) if M[t,k] and VW[t,k]<BIG) for t in range(n)])
            if kb not in cacheB:
                M=np.array(kb).reshape(n,m); cacheB[kb]=rank([sum(blkB[t][k] for k in range(m) if M[t,k] and VU[t,k]<BIG) for t in range(n)])
            u=cacheA[ka]+cacheB[kb]
            if u>best: best=u; bests=s.copy()
    return dict(UB=best,s=bests.tolist(),R=R,points=cnt,uniqA=len(cacheA),uniqB=len(cacheB),C=sum(rk2(Q[np.ix_(D[k],S[k])]) for k in range(m) if D[k] and S[k]))
if __name__=='__main__':
    rows=pickle.load(open(sys.argv[1],'rb')); L=std_set(sys.argv[2]); Q=Q_std(L)
    assert check_decoder(rows,Q)==0
    print(sys.argv[1],run(rows,Q),flush=True)

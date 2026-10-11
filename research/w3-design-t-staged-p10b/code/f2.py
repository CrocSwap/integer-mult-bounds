"""Exact legality replay + formal F2 replay of a PR249 word; returns residual (t, q) pairs of target columns on sigma-0 helpers.
Own reimplementation of the checks of w3's verifyT (MOVE nesting via exact integer A.B == 0, ADD common frame, COPY window,
final frames, nondegeneracy under I - J/9 is checked separately in nondeg.py)."""
import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from snapio import Snap,H
def contains(S,cache,new,old):
    k=(new,old)
    if k in cache: return cache[k]
    if S.dim[old]==0: r=True
    elif S.dim[old]>S.dim[new]: r=False
    else:
        Bo=np.array(S.F[str(old)]['B'],dtype=object);An=np.array(S.F[str(new)]['A'],dtype=object)
        r=(len(An)==0) or not np.any(Bo.dot(An.T)!=0)
    cache[k]=r;return r
def replay(d,quiet=False):
    S=Snap(d);n,v=S.n,S.v;rec=S.rec;cache={}
    state=[S.init[r] for r in range(n)]+[S.ZERO];bad=[];copied=False;cs=-1;ncopy=0
    for k in range(len(rec)):
        o,a,b,c,f,z=map(int,rec[k])
        if o==0:
            if state[a]!=b: bad.append(('state',k))
            if not contains(S,cache,c,b): bad.append(('nest',k))
            if S.dim[c]-S.dim[b]!=f: bad.append(('rank',k))
            state[a]=c
        elif o==1:
            if state[a]!=f or state[b]!=f: bad.append(('addframe',k))
            if a==b: bad.append(('self',k))
            if copied and (a==cs or a==n): bad.append(('copywin',k))
        elif o==2:
            if copied or b!=n or state[a]!=c or z!=S.dim[c]: bad.append(('copy',k))
            copied=True;cs=a;state[n]=f;ncopy+=1
        elif o==3:
            if not copied or a!=cs or state[a]!=c or state[n]!=f: bad.append(('erase',k))
            copied=False
    badfin=[r for r in range(n) if state[r]!=S.fin[r]]
    # F2
    WD=(n+1+63)//64;val=np.zeros((n+1,WD),np.uint64)
    for r in range(n): val[r,r//64]|=np.uint64(1)<<np.uint64(r%64)
    for k in range(len(rec)):
        o=rec[k,0]
        if o==1:
            if rec[k,3]&1: val[rec[k,1]]^=val[rec[k,2]]
        elif o==2: val[n]=val[rec[k,1]]
        elif o==3: val[n]=0
    sig=[S.dim[S.init[r]] for r in range(n)]
    bits=np.unpackbits(val.view(np.uint8),axis=1,bitorder='little')[:, :n]
    badX=badH=0;resid=[];other=[]
    I=np.eye(n,dtype=np.uint8)
    for r in range(n):
        if r<v or r>=2*v:
            if not np.array_equal(bits[r],I[r]):
                if r<v: badX+=1
                elif sig[r]<H: badH+=1
        else:
            t=r-v;ex=I[r].copy();ex[t]^=1;dd=np.nonzero(bits[r]^ex)[0]
            for q in dd.tolist():
                if 2*v<=q<n and sig[q]==0: resid.append((t,q))
                else: other.append((t,q))
    res=dict(violations=len(bad),first_bad=bad[:5],final_mismatch=len(badfin),copies=ncopy,X_not_restored=badX,H_not_restored=badH,resid_sigma0=len(resid),resid_other=len(other))
    if not quiet: print(d,res)
    return res,resid
if __name__=='__main__':
    res,resid=replay(sys.argv[1])
    if len(sys.argv)>2: np.savetxt(sys.argv[2],np.array(resid,dtype=np.int64).reshape(-1,2),fmt='%d')

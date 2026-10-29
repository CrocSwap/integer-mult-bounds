# Same as flat7.py but ranks/kernels mod p = 2^61-1 (fast). Validated against exact flat7.py on instances 0,1 (cost 43).
import sys
from lib import *
p=(1<<61)-1
def rref(rows,ncol=8):
    M=[[x%p for x in r] for r in rows]; piv=[]; r=0
    for c in range(ncol):
        k=next((i for i in range(r,len(M)) if M[i][c]),None)
        if k is None: continue
        M[r],M[k]=M[k],M[r]; inv=pow(M[r][c],p-2,p); M[r]=[x*inv%p for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]:
                f=M[i][c]; M[i]=[(a-f*b)%p for a,b in zip(M[i],M[r])]
        piv.append(c); r+=1
    return M[:r],piv
def kernel(rows):
    R,piv=rref(rows); free=[c for c in range(8) if c not in piv]; K=[]
    for f in free:
        v=[0]*8; v[f]=1
        for i,c in enumerate(piv): v[c]=(-R[i][f])%p
        K.append(v)
    return K
def rank(rows): return len(rref(rows)[1]) if rows else 0
def flats(Y):
    def cl(lines):
        basis=[]
        for t in lines:
            v=LAB[t]
            for b in basis: v=min(v,v^b)
            if v: basis.append(v)
        def ins(x):
            for b in basis: x=min(x,x^b)
            return x==0
        return frozenset(t for t in Y if ins(LAB[t])),len(basis)
    f0=cl([]); seen={f0[0]}; allf=[f0]; fr=[f0]
    while fr:
        nf=[]
        for F,r in fr:
            for t in Y:
                if t in F: continue
                g=cl(list(F)+[t])
                if g[0] not in seen: seen.add(g[0]); nf.append(g); allf.append(g)
        fr=nf
    return allf
def run(Y):
    Y=list(Y); allf=flats(Y); allf.sort(key=lambda x:x[1])
    B=[]; cost=0; prof=[]
    for F,w in allf:
        K=kernel([C[t] for t in Y if t not in F])
        for v in K:
            if rank(B+[v])>len(B): B.append(v); cost+=w; prof.append(w)
        if len(B)==8: break
    return cost,prof
if __name__=='__main__':
    par=lambda x: bin(x).count('1')&1
    res=set()
    for a in range(1,512):
        for b in range(a+1,512):
            if (a^b)<b: continue
            Yl=frozenset(t for t in range(n) if not par(a&LAB[t]) and not par(b&LAB[t]))
            if len(Yl)>=36: res.add(Yl)
    res=sorted(res,key=lambda s:sorted(s))
    lo,hi=int(sys.argv[1]),int(sys.argv[2]); from collections import Counter; cnt=Counter()
    for i,Y in enumerate(res[lo:hi],lo):
        c,prof=run(Y); cnt[(c,tuple(prof))]+=1
        if c<len(Y): print('***',i,c,prof,sorted(Y)); sys.stdout.flush()
    print('range',lo,hi,'results',dict(cnt))

"""Frame replay of a raw gauge-forward word (A+B): recompute minimal monotone frames, check target hyperplanes,
return the raw paid profile exactly as cgx's climb() counts it."""
import pickle,json,gzip
from collections import Counter
from fractions import Fraction as Q
def basis(vectors):
    b={}
    for x in vectors:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
def inside(a,b):return basis(list(a)+list(b))==b
_hc={}
def hyper(p):
    if p not in _hc:_hc[p]=basis([x for x in range(1,512) if (x&p).bit_count()%2==0])
    return _hc[p]
FULL=basis([1<<i for i in range(9)])
def replay(W,P,nreg,v=120,keep_stored=True,check=True):
    cur=[(p,) for p in P]+[()]*(nreg-len(P))
    H=Counter();bad=[]
    def climb(r,F):
        assert inside(cur[r],F)
        dr=len(F)-len(cur[r])
        if dr:H[dr]+=1
        cur[r]=F
    out=[]
    for k,e in enumerate(W):
        if e[0]=='add':
            _,t,s,a,b,F=e;regs=(t,s)
        else:
            _,t,a,b,F=e;regs=(t,)
        G=basis((list(F) if keep_stored else [])+[x for r in regs for x in cur[r]])
        if check:
            for r in regs:
                if v<=r<2*v and not inside(G,hyper(P[r-v])):bad.append((k,r,G))
        for r in regs:climb(r,G)
        out.append(e[:-1]+[list(G)])
    for r in range(nreg):
        T=hyper(P[r-v]) if v<=r<2*v else FULL
        if not inside(cur[r],T):bad.append(('final',r))
        else:climb(r,T)
    H[8]+=8;H[1]+=8
    return H,bad,out
if __name__=='__main__':
    import sys
    d=pickle.load(open(sys.argv[1],'rb'))
    raw=json.load(gzip.open(sys.argv[2]))
    print(list(raw.keys())[:20])

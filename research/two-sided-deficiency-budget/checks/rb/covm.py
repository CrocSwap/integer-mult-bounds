# Implementation A (general): exact test "T is covered by label pieces of weights ws" (piece of weight w = subset of T whose labels span <= w dims).
import numpy as np, itertools, json, sys, time
from targ import H, off, LAB
from gT import kern_masks
GL={1:1,2:2,3:4,4:8,5:12,6:20,7:36}
_K={}
def K(w):
    if w not in _K: _K[w]=kern_masks(9-w)
    return _K[w]
def cnt(A): return np.bitwise_count(A[...,0]).astype(np.int32)+np.bitwise_count(A[...,1]).astype(np.int32)
def tomask(T):
    m=sum(1<<t for t in T); return np.array([m&((1<<64)-1), m>>64],dtype=np.uint64)
def toint(a): return int(a[0])|(int(a[1])<<64)
def rank(R):
    b=[]
    for t in range(112):
        if R>>t&1:
            x=LAB[t]
            for y in b: x=min(x,x^y)
            if x: b.append(x)
    return len(b)
def tail_ok(R,n3,n2):
    pts=[t for t in range(112) if R>>t&1]; n=len(pts)
    if n<=2*n2+3*n3: return True
    if n>2*n2+4*n3: return False
    need=n-2*n2-3*n3
    quads=[q for q in itertools.combinations(pts,4) if (LAB[q[0]]^LAB[q[1]]^LAB[q[2]]^LAB[q[3]])==0]
    def rec(av,k,s):
        if k==0: return True
        for i in range(s,len(quads)):
            if all(x in av for x in quads[i]) and rec(av-set(quads[i]),k-1,i+1): return True
        return False
    return rec(set(pts),need,0)
class Target:
    def __init__(s,T):
        s.T=T; s.Tm=tomask(T); s.P={}; s.cap=dict(GL)
        for w in (5,6,7): s.cap[w]=int(cnt(K(w)&s.Tm).max())
    def pieces(s,w):
        if w not in s.P:
            A=np.unique(K(w)&s.Tm,axis=0); A=A[np.argsort(-cnt(A))]; s.P[w]=A
        return s.P[w]
    def covers(s,ws):
        ws=sorted(ws,reverse=True); big=[w for w in ws if w>=4]
        n3=ws.count(3); n2=sum(1 for w in ws if w<=2); tcap=4*n3+2*n2
        if sum(s.cap[w] for w in ws)<len(s.T): return False
        def rec(R,i,start):
            r=bin(R).count('1')
            if i==len(big): return tail_ok(R,n3,n2)
            rest=sum(s.cap[w] for w in big[i+1:])+tcap
            need=r-rest
            if need>s.cap[big[i]]: return False
            if need<=0 and i==len(big)-1 and tail_ok(R,n3,n2): return True
            P=s.pieces(big[i]); Rm=np.array([R&((1<<64)-1),R>>64],dtype=np.uint64)
            I=cnt(P&Rm); ok=np.nonzero(I>=max(need,1))[0]
            if i>0 and big[i-1]==big[i]: ok=ok[ok>=start]
            if i==len(big)-1:
                Rr=Rm[None,:]&~P[ok]; c=cnt(Rr)
                for j in np.nonzero(c<=tcap)[0]:
                    if tail_ok(toint(Rr[j]),n3,n2): return True
                return False
            if i==len(big)-2 and tcap==0:
                w2=big[i+1]; P2=s.pieces(w2)
                for j in ok:
                    R2=Rm&~P[j]
                    if cnt(R2)>s.cap[w2]: continue
                    if (((R2[0]&~P2[:,0])|(R2[1]&~P2[:,1]))==0).any(): return True
                return False
            for j in ok:
                if rec(R&~toint(P[j]),i+1,j): return True
            return False
        return rec(toint(s.Tm),0,0)

# k=5 type multisets (n=8) with chat(.99) > 128.891, singletons >= 2k (mains), no D1
import sys; sys.path.insert(0,'.')
from rbcore import value
from decimal import Decimal as Dm
import itertools
def parts(n,m=None):
    m=m or n
    if n==0: yield (); return
    for i in range(min(n,m),0,-1):
        for r in parts(n-i,i): yield (i,)+r
def types(k):
    T=[]
    for D in range(2,k+1):
        for P in parts(D): T.append((D,tuple(sorted(P)),value(D,P)))
    return T
def multisets(k,bar=Dm('128.891')):
    n=2*k-2;T=sorted(types(k),key=lambda x:-x[2]);need=bar*k/104
    out=[]
    def rec(i,left,cur,val,ones):
        if left==0:
            if val>need and ones>=2*k: out.append((float(val*104/k),tuple(cur)))
            return
        if i==len(T): return
        if val+left*T[i][2]<=need: return
        for c in range(left,-1,-1):
            rec(i+1,left-c,cur+[T[i][:2]]*c,val+c*T[i][2],ones+c*T[i][1].count(1))
    rec(0,n,[],Dm(0),0);out.sort(reverse=True);return out
if __name__=='__main__':
    k=int(sys.argv[1]);M=multisets(k);print('k',k,'#multisets',len(M))
    for v,ms in M[:15]:print(round(v,3),ms)

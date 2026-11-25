"""E8 roots (doubled coords), lines, frame F0, P112, N(f) supports."""
import itertools, numpy as np
def roots():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for si in (2,-2):
            for sj in (2,-2):
                v=[0]*8; v[i]=si; v[j]=sj; R.append(tuple(v))
    for s in itertools.product((1,-1),repeat=8):
        if s.count(-1)%2==0: R.append(s)
    return R
def lines():
    L=[]
    for r in roots():
        if tuple(-x for x in r) not in L: L.append(r)
    return np.array(L)  # 120 x 8, norm^2 = 8 (doubled)
def ip(a,b): return int(np.dot(a,b))//4   # true inner product
L=lines()
F0=[]
for k in range(4):
    for s in (2,-2):
        v=[0]*8; v[2*k]=2; v[2*k+1]=s; F0.append(tuple(v))
def idx(v):
    for t,r in enumerate(L):
        if tuple(r)==tuple(v) or tuple(-r)==tuple(v): return t
F0i=[idx(v) for v in F0]
P112=[t for t in range(120) if t not in F0i]
G=(L@L.T)//4   # Gram, entries 0,±1,±2
def N(f,live=P112):
    return [t for t in live if G[t,f]%2!=0]
if __name__=='__main__':
    print(len(L),F0i,len(P112),[len(N(f)) for f in F0i])
    cnt=[sum(1 for f in F0i if t in N(f)) for t in P112]; print(set(cnt))

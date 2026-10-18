"""Exact rational checks of parity LU and displacement rank closure."""
from fractions import Fraction as F
from pathlib import Path
import json
import random


def zeros(n, m=None):
    return [[F(0) for _ in range(n if m is None else m)] for _ in range(n)]


def eye(n):
    a = zeros(n)
    for i in range(n):
        a[i][i] = F(1)
    return a


def mm(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def add(a,b,sgn=1):
    return [[x+sgn*y for x,y in zip(r,s)] for r,s in zip(a,b)]


def inv(a):
    n=len(a)
    q=[r[:] + s for r,s in zip(a,eye(n))]
    for j in range(n):
        k=next(k for k in range(j,n) if q[k][j])
        q[j],q[k]=q[k],q[j]
        v=q[j][j]
        q[j]=[x/v for x in q[j]]
        for i in range(n):
            if i!=j:
                v=q[i][j]
                q[i]=[x-v*y for x,y in zip(q[i],q[j])]
    return [r[n:] for r in q]


def rank(a):
    a=[r[:] for r in a]
    k=0
    for j in range(len(a[0])):
        p=next((i for i in range(k,len(a)) if a[i][j]),None)
        if p is None:
            continue
        a[k],a[p]=a[p],a[k]
        v=a[k][j]
        a[k]=[x/v for x in a[k]]
        for i in range(k+1,len(a)):
            v=a[i][j]
            a[i]=[x-v*y for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a):
            break
    return k


def block(a,b,c,d):
    return [r+s for r,s in zip(a,b)] + [r+s for r,s in zip(c,d)]


def lo(f):
    return [[f[i-j] if i>=j else F(0) for j in range(len(f))]
            for i in range(len(f))]


def shift(n):
    a=zeros(n)
    for i in range(1,n):
        a[i][i-1]=F(1)
    return a


def displacement(a):
    z=shift(len(a))
    return add(mm(z,a),mm(a,z),-1)


def series_inv(f):
    g=[1/f[0]]
    for i in range(1,len(f)):
        g.append(-sum(f[j]*g[i-j] for j in range(1,i+1))/f[0])
    return g


def conv(a,b,n):
    return [sum(a[j]*b[i-j] for j in range(i+1)
                if j<len(a) and i-j<len(b)) for i in range(n)]


def main():
    rng=random.Random(20261013)
    parity=[]
    for n in [2,4,8,16]:
        f=[F(rng.randrange(-8,9),256*n) for _ in range(n)]
        f[0]+=1
        m=n//2
        e,o=f[::2],f[1::2]
        k=conv(o,series_inv(e),m)
        zk=[F(0)]+k[:-1]
        s=[x-y for x,y in zip(e,[F(0)]+conv(o,k,m)[:-1])]
        L=block(eye(m),zeros(m),lo(k),eye(m))
        D=block(lo(e),zeros(m),zeros(m),lo(s))
        U=block(eye(m),lo(zk),zeros(m),eye(m))
        order=list(range(0,n,2))+list(range(1,n,2))
        wanted=[[lo(f)[i][j] for j in order] for i in order]
        assert mm(mm(L,D),U)==wanted
        parity.append({"n":n,"matrix_entries_checked":n*n})

    trace=[]
    def walk(M,depth=0):
        n=len(M)
        r=rank(displacement(M))
        assert r<=2+depth
        if n==1:
            return
        m=n//2
        A=[r[:m] for r in M[:m]]
        B=[r[m:] for r in M[:m]]
        C=[r[:m] for r in M[m:]]
        D=[r[m:] for r in M[m:]]
        ai=inv(A)
        K,L=mm(ai,B),mm(C,ai)
        S=add(D,mm(C,K),-1)
        E=zeros(m)
        E[0][-1]=1
        Um=[[-x for x in r]+s for r,s in zip(L,eye(m))]
        Vm=[[-x for x in r] for r in K]+eye(m)
        rhs=add(mm(mm(Um,displacement(M)),Vm),mm(mm(S,E),K),-1)
        assert displacement(S)==rhs
        assert rank(displacement(S))<=r+1
        assert rank(displacement(A))<=r+1
        trace.append({"n":n,"depth":depth,"rank":r,
                      "A_rank":rank(displacement(A)),"S_rank":rank(displacement(S)),
                      "K_rank":rank(displacement(K)),"L_rank":rank(displacement(L))})
        walk(A,depth+1)
        walk(S,depth+1)
    for n in [2,4,8,16]:
        c=[F(rng.randrange(-8,9),256*n) for _ in range(n)]
        r=[F(rng.randrange(-8,9),256*n) for _ in range(n)]
        c[0]+=1
        H=[[c[i-j] if i>=j else r[j-i] for j in range(n)] for i in range(n)]
        walk(H)
    receipt={"status":"pass","arithmetic":"exact rational",
             "parity_instances":parity,"schur_nodes":trace}
    Path(__file__).with_name('EXACT-ALGEBRA.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({"status":"pass","parity_instances":len(parity),
                      "parity_entries":sum(x['matrix_entries_checked'] for x in parity),
                      "schur_nodes":len(trace)},indent=2))


if __name__=='__main__':
    main()

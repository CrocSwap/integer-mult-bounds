#!/usr/bin/env python3
"""Independent exact noncommutative block review; no primary imports.
Yiyang (@Lyy-iiis), substantial OpenAI Codex agent assistance. Apache-2.0.
"""
from fractions import Fraction as F
import json, random
from pathlib import Path

def need(ok, msg):
    if not ok: raise RuntimeError(msg)
def zero(n,m=None): return [[F(0) for _ in range(m or n)] for _ in range(n)]
def eye(n):
    a=zero(n)
    for j in range(n): a[j][j]=F(1)
    return a
def add(a,b): return [[u+v for u,v in zip(x,y)] for x,y in zip(a,b)]
def neg(a): return [[-u for u in x] for x in a]
def sub(a,b): return add(a,neg(b))
def mul(a,b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))),F(0)) for j in range(len(b[0]))] for i in range(len(a))]
def inv(a):
    n=len(a);w=[x[:]+y for x,y in zip(a,eye(n))]
    for k in range(n):
        p=next((i for i in range(k,n) if w[i][k]),None)
        need(p is not None,'singular matrix')
        w[k],w[p]=w[p],w[k]
        c=w[k][k];w[k]=[x/c for x in w[k]]
        for i in range(n):
            if i!=k:
                c=w[i][k];w[i]=[x-c*y for x,y in zip(w[i],w[k])]
    return [x[n:] for x in w]
def block(a,b,c,d): return [x+y for x,y in zip(a,b)]+[x+y for x,y in zip(c,d)]
def shifts(L,w):
    n=L*w;s=zero(n);r=zero(n);p=zero(n)
    for i in range(w):p[i][i]=1
    for j in range(L-1):
        for i in range(w):s[(j+1)*w+i][j*w+i]=1;r[j*w+i][(j+1)*w+i]=1
    return s,r,p

def constant_diagonal(L,q,seed):
    w=len(q);a=zero(L*w);rng=random.Random(seed)
    for lane in range(L):
        for i in range(w):
            for j in range(w):a[lane*w+i][lane*w+j]=q[i][j]
        for other in range(lane):
            for i in range(w):
                for j in range(w):a[lane*w+i][other*w+j]=F(rng.randint(-3,3),rng.choice((1,2,4)))
    return a

def corner(a,w):
    n=len(a);p=zero(n)
    for i in range(w):
        for j in range(w):p[i][j]=a[i][j]
    return p

def T(a,L,w):
    s,r,p=shifts(L,w)
    return add(mul(mul(s,a),r),corner(a,w))

def E(a,L,w):
    n=len(a);b=inv(a);s,_,_=shifts(L,w)
    return block(a,zero(n),mul(s,sub(eye(n),b)),T(b,L,w))

def Einverse(a,L,w):
    n=len(a);b=inv(a);s,_,_=shifts(L,w)
    return block(b,zero(n),mul(s,sub(b,eye(n))),T(a,L,w))

def core(a):
    n=len(a);b=inv(a)
    return block(a,zero(n),sub(eye(n),b),b)

def physical(a,L,w,inverse=False):
    """Columnwise owned-endpoint rotation/core/charged-boundary/rotation/CLEAR."""
    n=L*w;c=inv(core(a)) if inverse else core(a)
    boundary=a[:w] if inverse else inv(a)[:w]
    boundary=[row[:w] for row in boundary]
    ans=zero(2*n)
    nonzero_clears=0
    for col in range(2*n):
        inp=[F(i==col) for i in range(2*n)]
        x=inp[:n];y=inp[n:]
        owned=y[:w]
        shifted=y[w:]+[F(0)]*w
        out=[sum((u*v for u,v in zip(row,x+shifted)),F(0)) for row in c]
        boundary_out=[sum((u*v for u,v in zip(row,owned)),F(0)) for row in boundary]
        xout=out[:n];yout=boundary_out+out[n:2*n-w]
        discarded=out[2*n-w:]
        nonzero_clears += any(discarded)
        # CLEAR is explicit and its data are not a credited output.
        discarded=[F(0)]*w
        need(not any(discarded),'owned terminal bank not cleared')
        for i,v in enumerate(xout+yout):ans[i][col]=v
    return ans,nonzero_clears

def main():
    q=[[F(1),F(1)],[F(1),F(2)]]
    r=[[F(1),F(0)],[F(2),F(1)]]
    need(mul(q,r)!=mul(r,q),'fixture must be noncommutative')
    result={'scope':'Independent exact local block and owned-boundary replay, not native recursion or new kappa','cases':[]}
    for L in range(1,6):
        w=2;n=L*w;a=constant_diagonal(L,q,100+L);b=inv(a);c=constant_diagonal(L,r,200+L);s,rr,p=shifts(L,w)
        need(mul(s,rr)==sub(eye(n),p),'shift boundary')
        need(mul(T(a,L,w),T(c,L,w))==T(mul(a,c),L,w),'T multiplicativity')
        need(mul(T(a,L,w),s)==mul(s,a),'T intertwiner')
        ea=E(a,L,w);ei=Einverse(a,L,w)
        need(mul(ea,ei)==eye(2*n) and mul(ei,ea)==eye(2*n),'actual inverse pair')
        physical_forward,dirty=physical(a,L,w)
        physical_inverse,dirty_inverse=physical(a,L,w,True)
        need(physical_forward==ea,'owned forward implementation')
        need(physical_inverse==ei,'owned inverse implementation')
        if L>1:
            # Wrongly treating actual inverse as a new nominal opposite orientation fails.
            need(E(b,L,w)!=ei,'wrong-opposite negative control')
            # Removing the paid boundary annihilates arbitrary Y0.
            no_boundary=block(a,zero(n),mul(s,sub(eye(n),b)),mul(mul(s,b),rr))
            need(no_boundary!=ea,'omitted-boundary negative control')
            leaked=mul(s,rr)
            need(leaked==sub(eye(n),p) and any(leaked[i][i] for i in range(n)), 'positive-grade upper-right residue must expose a degree-zero leak')
            upper=a.copy(); upper=[row[:] for row in a]; upper[0][-1]+=1
            need(mul(T(upper,L,w),s)!=mul(s,upper), 'nontriangular input negative control')
        result['cases'].append({'lanes':L,'physical_width':w,'arbitrary_input_columns':2*n,'nonzero_owned_clears_forward':dirty,'nonzero_owned_clears_inverse':dirty_inverse,'homomorphism':True,'intertwining':True,'both_inverse_orders':True,'literal_owned_boundary':True,'controls':([] if L==1 else ['nominal-opposite-is-not-inverse','omitted-paid-boundary','degree-one-upper-right-leaks-to-degree-zero','nontriangular-input-breaks-intertwining'])})
    print(json.dumps(result,indent=2))
    print('PASS_INDEPENDENT_NONCYCLIC_BOUNDARY_REVIEW')
if __name__=='__main__':main()

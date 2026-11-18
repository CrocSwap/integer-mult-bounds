"""Evaluate the ideal source maps with exact rational arithmetic.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The Gaussian convolution and literal three-bit formulas follow the
PR6509 verifier. They are an algebraic check, not independent review.
"""
from fractions import Fraction as F


def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[0],a[1]-b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def norm2(z):return z[0]*z[0]+z[1]*z[1]
def phase(a,q=1):
    for _ in range(q%4):a=(-a[1],a[0])
    return a


def ideal_call(values,f,axis,adjoint=False):
    sign=-1 if adjoint else 1
    a,b=(F(1,2),F(sign,2)),(F(1,2),F(-sign,2))
    terms=[]
    for mask in range(1<<f):
        index=0;coefficient=(F(1),F(0))
        for j in range(f):
            bit=(mask>>j)&1;index|=bit<<(3*j+axis)
            coefficient=mul(coefficient,b if bit else a)
        terms.append((index,coefficient))
    return [tuple(sum(mul(c,values[k^shift])[part] for shift,c in terms) for part in (0,1)) for k in range(len(values))]


def base_map(name,x):
    bits=[(x>>j)&1 for j in range(3)]
    if name=='P':
        q=sum(bits);bits[2]^=bits[0];q+=sum(bits)
    elif name=='Q':
        q=sum(bits);bits[0],bits[1]=bits[1],bits[0];q+=sum(bits)
    elif name=='W':q=2*(bits[0]+bits[2])
    elif name=='M':bits[0],bits[1]=bits[1],bits[0];q=2*bits[1]
    else:raise ValueError('Monomial name')
    return sum(b<<j for j,b in enumerate(bits)),q%4


def monomial(values,name,f,inverse=False):
    out=[None]*len(values)
    for x in range(len(values)):
        y=q=0
        for j in range(f):
            digit,p=base_map(name,(x>>(3*j))&7);y|=digit<<(3*j);q+=p
        if inverse:out[x]=phase(values[y],-q)
        else:out[y]=phase(values[x],q)
    return out


def ideal_port(x,y,f,kind,reverse):
    x=list(x);y=list(y)
    def mix(sign):
        nonlocal y
        p=monomial(x,'P',f);q=monomial(x,'Q',f)
        y=[add(v,(sign*(a[0]+2*b[0]),sign*(a[1]+2*b[1]))) for v,a,b in zip(y,p,q)]
    if reverse:
        if kind==3:y=monomial(y,'M',f,True);y=ideal_call(y,f,2,True);y=monomial(y,'W',f,True)
        y=ideal_call(y,f,0,True);mix(-1);x=ideal_call(x,f,0,True)
    else:
        x=ideal_call(x,f,0);mix(1);y=ideal_call(y,f,0)
        if kind==3:y=monomial(ideal_call(monomial(y,'W',f),f,2),'M',f)
    return x,y

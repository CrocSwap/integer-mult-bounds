"""Our previously authored pure rational chart helpers, copied for PR275.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as F
from math import gcd,lcm
def rref(A):
    A=[[F(x)for x in row]for row in A];piv=[]
    for j in range(len(A[0])if A else 0):
        q=next((i for i in range(len(piv),len(A))if A[i][j]),None)
        if q is None:continue
        i=len(piv);A[i],A[q]=A[q],A[i];v=A[i][j];A[i]=[x/v for x in A[i]]
        for k in range(len(A)):
            if k!=i and A[k][j]:
                v=A[k][j];A[k]=[a-v*b for a,b in zip(A[k],A[i])]
        piv.append(j)
        if len(piv)==len(A):break
    return A,piv


def primitive(v):
    d=lcm(*(F(x).denominator for x in v));v=[int(F(x)*d)for x in v];g=gcd(*v)
    assert g;return [x//g for x in v]


def nullspace(A,n=24):
    R,piv=rref(A);out=[]
    for free in range(n):
        if free in piv:continue
        v=[F(0)]*n;v[free]=1
        for i,j in enumerate(piv):v[j]=-R[i][free]
        out.append(primitive(v))
    return out


def factor(B):
    n=len(B);A=[[F(x)for x in row]for row in B];ops=[];det=F(1)
    for j in range(n):
        pivot=next(i for i in range(j,n)if A[i][j])
        if pivot!=j:A[pivot],A[j]=A[j],A[pivot];ops.append(('swap',j,pivot,F(1)));det=-det
        v=A[j][j];det*=v
        if v!=1:A[j]=[x/v for x in A[j]];ops.append(('scale',j,j,1/v))
        for i in range(n):
            if i!=j and A[i][j]:
                q=-A[i][j];A[i]=[x+q*y for x,y in zip(A[i],A[j])];ops.append(('add',i,j,q))
    assert A==[[int(i==j)for j in range(n)]for i in range(n)]
    # Independently replay inverse operations from I and recover B.
    C=[[F(i==j)for j in range(n)]for i in range(n)]
    for kind,i,j,q in reversed(ops):
        if kind=='swap':C[i],C[j]=C[j],C[i]
        elif kind=='scale':C[i]=[x/q for x in C[i]]
        else:C[i]=[x-q*y for x,y in zip(C[i],C[j])]
    assert C==B
    return dict(determinant=det,factors=ops,count=len(ops),
      max_numerator=max((abs(q.numerator)for kind,i,j,q in ops),default=1),
      max_denominator=max((q.denominator for kind,i,j,q in ops),default=1))


def serial(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [serial(v)for v in x]
    return x



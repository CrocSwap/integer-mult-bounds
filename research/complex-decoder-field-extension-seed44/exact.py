"""Exact Gaussian-rational arithmetic and independent E8 model.

Prepared for @woklerx with substantial OpenAI Codex assistance; Apache-2.0.
The E8 label model is credited to PR717/PR968.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from math import lcm


class G:
    def __init__(self,r=0,i=0):
        if isinstance(r,G):self.r,self.i=r.r,r.i
        else:self.r,self.i=Q(r),Q(i)
    def __add__(self,o):
        o=G(o);return G(self.r+o.r,self.i+o.i)
    __radd__=__add__
    def __neg__(self):return G(-self.r,-self.i)
    def __sub__(self,o):return self+-G(o)
    def __mul__(self,o):
        o=G(o);return G(self.r*o.r-self.i*o.i,self.r*o.i+self.i*o.r)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=G(o);d=o.r**2+o.i**2
        return self*G(o.r/d,-o.i/d)
    def __eq__(self,o):
        o=G(o);return self.r==o.r and self.i==o.i
    def __bool__(self):return bool(self.r or self.i)
    def conjugate(self):return G(self.r,-self.i)
    def record(self):return [str(self.r),str(self.i)]


def roots():
    result=set()
    for a,b in combinations(range(8),2):
        for x,y in product((-2,2),repeat=2):
            r=[0]*8;r[a],r[b]=x,y
            result.add(max(tuple(r),tuple(-z for z in r)))
    for r in product((-1,1),repeat=8):
        if sum(z<0 for z in r)%2==0:result.add(max(r,tuple(-z for z in r)))
    return sorted(result)


def rank2(rows):
    basis={}
    for row in rows:
        while row:
            p=row.bit_length()-1
            if p not in basis:basis[p]=row;break
            row^=basis[p]
    return len(basis)


def rankq(rows):
    a=[[Q(x) for x in row] for row in rows]
    if not a:return 0
    count=0
    for col in range(len(a[0])):
        p=next((j for j in range(count,len(a)) if a[j][col]),None)
        if p is None:continue
        a[p],a[count]=a[count],a[p]
        factor=a[count][col]
        a[count]=[x/factor for x in a[count]]
        for j in range(count+1,len(a)):
            factor=a[j][col]
            a[j]=[x-factor*y for x,y in zip(a[j],a[count])]
        count+=1
    return count


def eye(n=8):return [[G(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(row) for row in zip(*a)]
def multiply(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in transpose(b)] for row in a]


def inverse(a):
    n=len(a)
    a=[[G(x) for x in row]+eye(n)[i] for i,row in enumerate(a)]
    for col in range(n):
        p=next(i for i in range(col,n) if a[i][col])
        a[p],a[col]=a[col],a[p]
        scale=a[col][col]
        a[col]=[x/scale for x in a[col]]
        for i in range(n):
            if i!=col:
                factor=a[i][col]
                a[i]=[x-factor*y for x,y in zip(a[i],a[col])]
    return [row[n:] for row in a]


def dual(a):return [[2*x for x in row] for row in transpose(inverse(a))]


def encoded(a):return [[x.record() for x in row] for row in a]


def clear(a):
    den=1
    for row in a:
        for x in row:den=lcm(den,x.r.denominator,x.i.denominator)
    return den,[[(int(x.r*den),int(x.i*den)) for x in row] for row in a]


def root_products(rs,a):
    den,ints=clear(a)
    return den,[[tuple(sum(r[j]*ints[j][k][q] for j in range(8)) for q in range(2)) for k in range(8)] for r in rs]


def full_identity(rs,a,b):
    ad,d=root_products(rs,a);bd,t=root_products(rs,b)
    for i,r in enumerate(rs):
        for j,s in enumerate(rs):
            real=sum(x[0]*y[0]-x[1]*y[1] for x,y in zip(d[i],t[j]))
            imag=sum(x[0]*y[1]+x[1]*y[0] for x,y in zip(d[i],t[j]))
            if imag or real!=2*ad*bd*sum(x*y for x,y in zip(r,s)):return False
    return True


def supports(rs,a):
    _,d=root_products(rs,a)
    return [sum((d[i][k]!=(0,0))<<i for i in range(len(rs))) for k in range(8)]

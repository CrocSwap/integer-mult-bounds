"""Original exact weighted-frame linear algebra over rational numbers.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from math import gcd,lcm
def transpose(A):return list(map(list,zip(*A)))


def eye(n):return [[Q(i==j)for j in range(n)]for i in range(n)]


def add(A,B,c=1):return [[x+c*y for x,y in zip(a,b)]for a,b in zip(A,B)]


def mul(A,B):
    cols=transpose(B)
    return [[sum((x*y for x,y in zip(row,col)if x and y),Q(0))for col in cols]for row in A]


def echelon(A):
    A=[[Q(x)for x in row]for row in A];piv=[];n=len(A)
    if not n:return A,piv
    for j in range(len(A[0])):
        k=next((k for k in range(len(piv),n)if A[k][j]),None)
        if k is None:continue
        i=len(piv);A[i],A[k]=A[k],A[i];c=A[i][j];A[i]=[x/c for x in A[i]]
        for k in range(n):
            if k!=i and A[k][j]:
                c=A[k][j];A[k]=[x-c*y for x,y in zip(A[k],A[i])]
        piv.append(j)
        if len(piv)==n:break
    return A,piv


def inv(A):
    n=len(A);B,p=echelon([a+b for a,b in zip(A,eye(n))]);assert p[:n]==list(range(n))
    return [r[n:]for r in B]


def projector(ann):
    # G=I-J/9; its inverse is I-J/15 in dimension24.
    I=eye(24);Gi=[[I[i][j]-Q(1,15)for j in range(24)]for i in range(24)]
    A=[[Q(x)for x in row]for row in ann]
    gram=mul(mul(A,Gi),transpose(A));gram_inv=inv(gram)
    return add(I,mul(mul(mul(Gi,transpose(A)),gram_inv),A),-1)


def integer_columns(A,count):
    _,p=echelon(A);assert len(p)==count
    out=[]
    for j in p:
        col=[row[j]for row in A];den=lcm(*(x.denominator for x in col))
        col=[int(x*den)for x in col];g=0
        for x in col:g=gcd(g,abs(x))
        out.append([x//g for x in col])
    return out,p


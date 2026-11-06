"""Exact rational linear algebra. New work for @CubeJerry with OpenAI assistance. Apache-2.0."""
from fractions import Fraction as F
import itertools, json

def mat(a):return [[F(x) for x in r] for r in a]
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def tr(a):return list(map(list,zip(*a)))
def mm(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)]for r in a]
def add(a,b,c=1):return [[x+c*y for x,y in zip(r,s)]for r,s in zip(a,b)]
def rr(a):
 a=[[F(x) for x in r]for r in a];p=[];k=0
 for j in range(len(a[0]) if a else 0):
  l=next((l for l in range(k,len(a))if a[l][j]),None)
  if l is None:continue
  a[k],a[l]=a[l],a[k];z=a[k][j];a[k]=[x/z for x in a[k]]
  for l in range(len(a)):
   if l!=k and a[l][j]:
    z=a[l][j];a[l]=[x-z*y for x,y in zip(a[l],a[k])]
  p.append(j);k+=1
  if k==len(a):break
 return a,p

def rank(a):return len(rr(a)[1])
def span(rows):
 a,_=rr(rows);return [r for r in a if any(r)]
def inv(a):
 n=len(a);r,p=rr([x+y for x,y in zip(a,eye(n))]);assert p[:n]==list(range(n));return [x[n:]for x in r]
def canonical(n):
 I=eye(n);us=[r for r in I]+[[F((-1)**(i+1))for i in range(n)]]
 vs=[[F((i>j)-(i<j))for j in range(n)]for i in range(n)]+[[F(1)]*n]
 Rs=[mm(tr([u]),[v])for u,v in zip(us,vs)]
 Bs=[];B=I
 for R in Rs:B=mm(add(I,R,-2),B);Bs.append(B)
 assert B==[[-x for x in r]for r in I]
 return us,vs,Rs,Bs

def closure(us,vs,mats):
 A=span(us);C=span(vs)
 while True:
  A1=span(A+[tr(mm(M,tr([u])))[0]for M in mats for u in A]);C1=span(C+[mm([v],M)[0]for M in mats for v in C])
  if len(A1)==len(A) and len(C1)==len(C):break
  A,C=A1,C1
 return tr(A),C
def flat(a):return sum(a,[])
def unflat(a,n):return [a[i*n:(i+1)*n]for i in range(n)]
def lin_solve(eq,b):
 n=len(eq[0]);r,p=rr([a+[v]for a,v in zip(eq,b)])
 if n in p:return None
 fs=[i for i in range(n)if i not in p];x=[F(0)]*n
 for i,j in enumerate(p):x[j]=r[i][-1]
 null=[]
 for f in fs:
  z=[F(0)]*n;z[f]=1
  for i,j in enumerate(p):z[j]=-r[i][f]
  null.append(z)
 return x,null

def proj_linear(n,Us,Vs,commutes):
 eq=[];rhs=[]
 for u in Us:
  for i in range(n):
   r=[F(0)]*(n*n);r[i*n:(i+1)*n]=u;eq.append(r);rhs.append(u[i])
 for v in Vs:
  for j in range(n):
   r=[F(0)]*(n*n)
   for i in range(n):r[i*n+j]=v[i]
   eq.append(r);rhs.append(v[j])
 for M in commutes:
  for i in range(n):
   for j in range(n):
    r=[F(0)]*(n*n)
    for k in range(n):r[i*n+k]+=M[k][j];r[k*n+j]-=M[i][k]
    eq.append(r);rhs.append(F(0))
 sol=lin_solve(eq,rhs)
 return None if sol is None else (unflat(sol[0],n),[unflat(x,n)for x in sol[1]])

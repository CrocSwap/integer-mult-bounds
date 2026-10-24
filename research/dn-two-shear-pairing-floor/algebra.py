"""Exact rational factors and binary common-pairing invoices."""
from fractions import Fraction as F
from itertools import product

def need(ok,message):
 if not ok:raise ValueError(message)
def eye(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return list(map(list,zip(*a)))
def multiply(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def shear(n,a,b,t):
 need(type(a)is int and type(b)is int and 0<=a<n and 0<=b<n and a!=b,'shear indices')
 m=eye(n);m[a][b]=F(t);return m
def roots(n,edges):
 need(type(n)is int and n>=2,'dimension')
 need(len(set(edges))==len(edges) and all(type(a)is int and type(b)is int and 0<=a<b<n for a,b in edges),'simple paired graph')
 out=[]
 for a,b in edges:
  for sign in (1,-1):
   row=[F(0)]*n;row[a]=1;row[b]=sign;out.append(row)
 return out
def factors(n,edges,a,b,c,d,t,s):
 r=roots(n,edges);m=multiply(shear(n,a,b,t),shear(n,c,d,s))
 inv=multiply(shear(n,c,d,-s),shear(n,a,b,-t))
 need(multiply(m,inv)==eye(n),'two-sided factor inverse')
 p=multiply(r,m) if r else [];q=multiply(r,transpose(inv)) if r else []
 need(multiply(p,transpose(q))==multiply(r,transpose(r)),'complete Gram equality')
 supports=[([i for i in range(len(r)) if p[i][j]],[i for i in range(len(r)) if q[i][j]]) for j in range(n)]
 return r,p,q,supports

def rank(rows):
 basis={}
 for value in rows:
  while value:
   pivot=value.bit_length()-1
   if pivot in basis:value^=basis[pivot]
   else:basis[pivot]=value;break
 return len(basis)
def rank_by_span(rows):
 span={0}
 for row in rows:span|={x^row for x in tuple(span)}
 return len(span).bit_length()-1

def gram(r):return multiply(r,transpose(r))
def fitting(r,rows):
 n=len(r);need(len(rows)==n and all(type(x)is int and 0<=x<1<<n for x in rows),'binary pairing shape')
 g=gram(r)
 need(all((rows[i]>>i)&1 for i in range(n)),'fitting diagonal')
 need(all(not((rows[i]>>j)&1) for i in range(n) for j in range(n) if i!=j and g[i][j]),'fitting forbidden entry')
def all_pairings(r):
 n=len(r);g=gram(r);free=[(i,j) for i in range(n) for j in range(n) if i!=j and not g[i][j]]
 for mask in range(1<<len(free)):
  rows=[1<<i for i in range(n)]
  for k,(i,j) in enumerate(free):
   if mask>>k&1:rows[i]|=1<<j
  yield rows
def edge_pairing(edges):return [3<<(2*e) for e in range(len(edges)) for _ in (0,1)]
def bill(rows,supports,ranker=rank):
 return [ranker([sum(((rows[i]>>j)&1)<<k for k,j in enumerate(cols)) for i in inds]) for inds,cols in supports]
def degree_certificate(n,edges,supports):
 """Search finite incident-root identity minors; never optimize pairing entries."""
 total=0;witness=[]
 for inds,cols in supports:
  common=set(inds)&set(cols);best=[]
  for vertex in range(n):
   incident=[e for e,edge in enumerate(edges) if vertex in edge];chosen=[]
   for e in incident:
    options=[2*e+z for z in (0,1) if 2*e+z in common]
    if not options:break
    chosen.append(options[0])
   else:
    if len(chosen)>len(best):best=chosen
  total+=len(best);witness.append(best)
 return total,witness

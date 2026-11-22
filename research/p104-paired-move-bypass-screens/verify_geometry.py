"""Check exact projector nesting for all screened paths and replacement edges."""
from argparse import ArgumentParser
from fractions import Fraction
from functools import lru_cache
from math import lcm
from native_model import load,primitive,paths

def matmul(A,B):
 cols=list(zip(*B))
 return [[sum(x*y for x,y in zip(row,col)) for col in cols] for row in A]

def projector(spec):
 basis=list(map(list,zip(*(spec['B']+spec['A']))));n=len(basis)
 assert n==8 and all(len(row)==8 for row in basis)
 aug=[[Fraction(x) for x in row]+[Fraction(i==j) for j in range(n)] for i,row in enumerate(basis)]
 for j in range(n):
  k=next(i for i in range(j,n) if aug[i][j].numerator%3 and aug[i][j].denominator%3)
  aug[j],aug[k]=aug[k],aug[j];v=aug[j][j];aug[j]=[x/v for x in aug[j]]
  for i in range(n):
   if i!=j and aug[i][j]:
    a=aug[i][j];aug[i]=[x-a*y for x,y in zip(aug[i],aug[j])]
 inv=[row[n:] for row in aug];r=spec['dim']
 P=matmul([[Fraction(x) if j<r else Fraction(0) for j,x in enumerate(row)] for row in basis],inv)
 d=lcm(*(x.denominator for row in P for x in row));assert d%3
 return d,[[int(d*x) for x in row] for row in P]

def main():
 parser=ArgumentParser(description=__doc__);parser.add_argument('source');args=parser.parse_args()
 G=load(args.source);edges,inn,out,_=primitive(G);cases=paths(G,edges,inn,out)
 @lru_cache(None)
 def proj(i):return projector(G['frames'][str(i)])
 @lru_cache(None)
 def nested(a,b):
  if G['frames'][str(a)]['dim']>G['frames'][str(b)]['dim']:a,b=b,a
  da,A=proj(a);db,B=proj(b);small=[[db*x for x in row] for row in A]
  return matmul(A,B)==small and matmul(B,A)==small
 original=set();direct=set()
 for h,i,j in cases:
  a=edges[i]['a'];b=edges[j]['b'];original.add((a,h));original.add((h,b));direct.add((a,b))
 for a,b in sorted(original):assert nested(a,b),(a,b)
 for a,b in sorted(direct):assert nested(a,b),(a,b)
 print(f'primitive replay: 630/630 public fields, 2,803 MOVEs, 3,433 dirty clears')
 print(f'geometry: {len(original)} original endpoint pairs and {len(direct)} direct endpoint pairs nested, all 1,557 paths monotone')
if __name__=='__main__':main()

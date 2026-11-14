"""Independent Cartesian-necklace construction and exact rational support."""
from itertools import product
from math import prod
from fractions import Fraction as Q
from collections import Counter
import json

def cycles(n,p):
 out=[]
 for x in product(range(n),repeat=p):
  rs=[x[i:]+x[:i] for i in range(p)]
  if x==min(rs):out.append(list(dict.fromkeys(rs)))
 return out

def order(n,ps):
 xs=[];S=[];ls=[]
 for cs in product(*(cycles(n,p) for p in ps)):
  L=prod(map(len,cs));S.append(len(xs));ls.append(L)
  xs.extend(sum((c[t%len(c)] for c in cs),()) for t in range(L))
 if len(set(xs))!=len(xs):raise ValueError('noncoprime periods')
 return xs,S,ls
rows=[]
for n,ps,v in [(2,[3,5],Q(1)),(2,[3,5],Q(3,2)),(3,[3],Q(2))]:
 xs,S,ls=order(n,ps);N=len(xs);C=prod((n**p+(p-1)*n)//p for p in ps)
 if C!=len(S):raise ValueError('count')
 def entry(x,y):return Q(1,2)**sum((a-b)**2 for a,b in zip(x,y))*v**(sum(x)-sum(y))
 for i in range(N):
  for j in range(N):
   if i not in S and j not in S and entry(xs[i],xs[j])!=entry(xs[i-1],xs[j-1]):raise ValueError('support')
 rows.append(dict(n=n,primes=ps,v=str(v),size=N,cycles=C,periods=dict(Counter(ls)),upper=2*C))
correction=prod(1+Q(p-1,2**(p-1)) for p in [3,5,7])
if not 2<correction<3:raise ValueError('correction')
try:order(2,[3,3])
except ValueError:rejected=True
else:raise ValueError('repeat control')
print(json.dumps(dict(status='PASS_ROOT_PRIME_ORBIT_WITNESSES',cases=rows,correction=str(correction),repeated_prime_rejected=rejected),indent=2))

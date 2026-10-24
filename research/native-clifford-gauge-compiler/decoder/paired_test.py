#!/usr/bin/env python3
"""Exact complete paired-transvection neighbor tests; standard library only."""
import argparse,json,random
from pathlib import Path


def need(ok,label):
 if not ok:raise ValueError(label)


def omega(a,b,n):
 m=(1<<n)-1
 return (((a&m)&(b>>n)).bit_count()+((a>>n)&(b&m)).bit_count())&1


def span(rows):
 s={0}
 for x in rows:s|={y^x for y in tuple(s)}
 return frozenset(s)


def basis(rows):
 p={}
 for x in rows:
  while x:
   j=x.bit_length()-1
   if j not in p:p[j]=x;break
   x^=p[j]
 for j in sorted(p):
  for k in p:
   if k>j and p[k]>>j&1:p[k]^=p[j]
 return [p[j]for j in sorted(p)]


def lagrangians(n):
 spaces={frozenset({0})}
 for d in range(n):
  nxt=set()
  for s in spaces:
   for a in range(1,1<<(2*n)):
    if a not in s and all(not omega(a,x,n)for x in s):nxt.add(s|frozenset(x^a for x in s))
  spaces=nxt
 return sorted(spaces,key=lambda s:tuple(sorted(s)))


def representatives(U,V,n):
 I=basis(U&V);p={x.bit_length()-1:x for x in I};free=[1<<j for j in range(2*n)if j not in p];a=[0]*(1<<len(free));out=[]
 for q in range(1,len(a)):
  j=(q&-q).bit_length()-1;a[q]=a[q&(q-1)]^free[j];out.append(a[q])
  i=next((i for i in I if omega(a[q],i,n)),None)
  if i is not None:out.append(a[q]^i)
 return out


def moved(U,a,n):
 return sum(1<<(x^(a if omega(x,a,n)else 0))for x in U)


def small():
 out=[]
 for n in (1,2,3):
  ls=lagrangians(n);cases=0
  for U in ls:
   um={a:moved(U,a,n)for a in range(1,1<<(2*n))};oldU=sum(1<<x for x in U)
   for V in ls:
    old=(oldU,sum(1<<x for x in V));full={(um[a],moved(V,a,n))for a in um};full.discard(old)
    reps=representatives(U,V,n);reduced={(um[a],moved(V,a,n))for a in reps}
    k=(len(U&V)).bit_length()-1;r=n-k;expected=(1<<(n+r+1))-(1<<(2*r))-1
    need(len(reps)==expected,'Exact paired neighbor count')
    need(len(reduced)==len(reps)and reduced==full,'Exhaustive paired neighbor set')
    cases+=len(um)
  out.append({'n':n,'lagrangians':len(ls),'axis_cases':cases})
 # Additional width-four mixed pairs.
 n=4;ls=lagrangians(n);rng=random.Random(20261022);count=0
 for _ in range(128):
  U=rng.choice(ls);V=rng.choice(ls);old=(sum(1<<x for x in U),sum(1<<x for x in V));full={(moved(U,a,n),moved(V,a,n))for a in range(1,1<<(2*n))};full.discard(old);reps=representatives(U,V,n);reduced={(moved(U,a,n),moved(V,a,n))for a in reps}
  need(len(reduced)==len(reps)and reduced==full,'Width-four paired set');count+=255
 return {'exhaustive':out,'width_four_pairs':128,'width_four_axis_cases':count}


def main():
 p=argparse.ArgumentParser();p.add_argument('--write',type=Path);p.add_argument('--expected',type=Path);args=p.parse_args();out={'status':'PASS_COMPLETE_PAIRED_TRANSVECTION_NEIGHBORS','checks':small(),'new_kappa':False}
 if args.expected:need(out==json.loads(args.expected.read_text(encoding='utf-8')),'Expected mismatch')
 if args.write:args.write.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print(json.dumps(out,sort_keys=True))


if __name__=='__main__':main()

"""Signed intersection-parity sum DAG: scalar saving with frame obstructions.

The specified circuit is a failed candidate for nested nondegenerate binary
frames. Its obstruction does not exclude other circuits or transfer models.
"""
from functools import cache
from math import comb
from itertools import combinations
from certify import require
from experiments.mixed_point_circuit import plan as oldplan
from experiments.mixed_point_circuit import build as oldbuild
from experiments.disjoint_tensor import plan as disjointplan
from experiments.disjoint_tensor import DisjointTensor,subsets,plan as dp
from binary_phase_frames import basis,classify

def choose(n,k):return comb(n,k) if 0<=k<=n else 0
@cache
def feasible(n,k,l,p):
 return 0<=k<=n and 0<=l<=n and any(j%2==p for j in range(max(0,k+l-n),min(k,l)+1))
@cache
def exact(n,k,l,r):
 if not (0<=r<=min(k,l) and k+l-r<=n):return None
 out=oldplan(n,k,l,r)[0]
 if r:
  c=comb(n,r)*disjointplan(n-r,k-r,l-r)[0]+(comb(l,r)-1)*comb(n,l)
  out=min(out,c)
 return out
@cache
def plan(n,k,l,p):
 if not feasible(n,k,l,p):return (0,'empty')
 roots=[r for r in range(p,min(k,l)+1,2) if k+l-r<=n]
 best=(sum(exact(n,k,l,r) for r in roots)+(len(roots)-1)*comb(n,l),'separate')
 for nl in range(1,n//2+1):
  nr=n-nl;total=0
  for b in range(max(0,l-nr),min(l,nl)+1):
   pieces=0
   for a in range(max(0,k-nr),min(k,nl)+1):
    for u in (0,1):
     if not feasible(nl,a,b,u) or not feasible(nr,k-a,l-b,p^u):continue
     pieces+=1
     A=plan(nl,a,b,u)[0];B=plan(nr,k-a,l-b,p^u)[0]
     total+=min(comb(nr,k-a)*A+comb(nl,b)*B,comb(nl,a)*B+comb(nr,l-b)*A)
   total+=comb(nl,b)*comb(nr,l-b)*(pieces-1)
  if total<best[0]:best=(total,nl)
 return best

@cache
def sets(n,k):return tuple(sum(1<<i for i in s) for s in combinations(range(n),k))
class ParitySide:
 def __init__(self,h):
  require(type(h) is int and 8<=h<=40 and h%2==0,'Bounded experiment: even h=8,...,40')
  self.h=h;self.inputs=sets(h,3);self.support=[(0,0)]+[(1<<i,0) for i in range(len(self.inputs))]
  self.args=[None]*len(self.support);self.lookup={s:i for i,s in enumerate(self.support)}
  self.outputs=self.transform(tuple(range(h)),3,3,0,{s:i+1 for i,s in enumerate(self.inputs)})
  self.active=set();todo=[abs(x) for x in self.outputs.values()]
  while todo:
   x=todo.pop()
   if not x or x in self.active:continue
   self.active.add(x)
   if self.args[x]:todo.extend(abs(y) for y in self.args[x])
 def add(self,a,b):
  if not a:return b
  if not b:return a
  pa,na=self.support[abs(a)];pb,nb=self.support[abs(b)]
  if a<0:pa,na=na,pa
  if b<0:pb,nb=nb,pb
  assert not (pa|na)&(pb|nb)
  p,n=pa|pb,na|nb;sign=1
  if (p|n)&-(p|n)&n:p,n=n,p;a,b=-a,-b;sign=-1
  key=p,n
  if key not in self.lookup:
   self.lookup[key]=len(self.args);self.args.append((a,b));self.support.append(key)
  return sign*self.lookup[key]
 def total(self,vals):
  if not vals:return 0
  if len(vals)==1:return vals[0]
  mid=len(vals)//2;return self.add(self.total(vals[:mid]),self.total(vals[mid:]))
 def import_old(self,n,k,l,r,values,points):
  old=oldbuild(n,k,l,r);nodes=[0]*len(old.args)
  for i,s in enumerate(old.inputs):nodes[i+1]=values[sum(1<<points[j] for j in s)]
  for node in old.active:
   if old.args[node]:a,b=old.args[node];nodes[node]=self.add(nodes[a],nodes[b])
  return {sum(1<<points[j] for j in t):nodes[x] for t,x in zip(old.targets,old.outputs)}
 def disjoint(self,points,a,b,values):
  parent=self
  class Adapter:
   add=parent.add
   total=parent.total
   def transform(self,*args):return DisjointTensor.transform(self,*args)
  return Adapter().transform(points,a,b,values)
 def exact(self,points,k,l,r,values):
  n=len(points)
  old=oldbuild(n,k,l,r)
  common=comb(n,r)*dp(n-r,k-r,l-r)[0]+(comb(l,r)-1)*comb(n,l) if r else 10**100
  if old.additions<=common:return self.import_old(n,k,l,r,values,points)
  out={t:[] for t in subsets(points,l)}
  for center in subsets(points,r):
   rest=tuple(i for i in points if not center>>i&1)
   row=self.disjoint(rest,k-r,l-r,{s:values[s|center] for s in subsets(rest,k-r)})
   for t,v in row.items():out[t|center].append(v)
  return {t:self.total(v) for t,v in out.items()}
 def transform(self,points,k,l,p,values):
  n=len(points);_,method=plan(n,k,l,p)
  if method=='empty':return {t:0 for t in subsets(points,l)}
  terms={t:[] for t in subsets(points,l)}
  if method=='separate':
   for r in range(p,min(k,l)+1,2):
    if k+l-r>n:continue
    row=self.exact(points,k,l,r,values);sign=(-1)**(r//2)
    for t,v in row.items():terms[t].append(sign*v)
  else:
   left,right=points[:method],points[method:];nl,nr=len(left),len(right)
   for b in range(max(0,l-nr),min(l,nl)+1):
    for a in range(max(0,k-nr),min(k,nl)+1):
     for u in (0,1):
      v=p^u
      if not feasible(nl,a,b,u) or not feasible(nr,k-a,l-b,v):continue
      A=plan(nl,a,b,u)[0];B=plan(nr,k-a,l-b,v)[0];sign=-1 if u and v else 1
      if comb(nr,k-a)*A+comb(nl,b)*B<=comb(nl,a)*B+comb(nr,l-b)*A:
       middle={s:self.transform(left,a,b,u,{r:values[r|s] for r in subsets(left,a)}) for s in subsets(right,k-a)}
       for t in subsets(left,b):
        row=self.transform(right,k-a,l-b,v,{s:m[t] for s,m in middle.items()})
        for w,x in row.items():terms[t|w].append(sign*x)
      else:
       middle={s:self.transform(right,k-a,l-b,v,{r:values[r|s] for r in subsets(right,k-a)}) for s in subsets(left,a)}
       for t in subsets(right,l-b):
        row=self.transform(left,a,b,u,{s:m[t] for s,m in middle.items()})
        for w,x in row.items():terms[t|w].append(sign*x)
  return {t:self.total(v) for t,v in terms.items()}
 def verify(self):
  for t,node in self.outputs.items():
   p,n=self.support[abs(node)]
   if node<0:p,n=n,p
   assert p==sum(1<<i for i,s in enumerate(self.inputs) if (s&t).bit_count()==0)
   assert n==sum(1<<i for i,s in enumerate(self.inputs) if (s&t).bit_count()==2)
  S={};T={x:() for x in self.active}
  for x in sorted(self.active):
   if self.args[x]:a,b=self.args[x];S[x]=basis(S[abs(a)]+S[abs(b)])
   else:S[x]=(self.inputs[x-1],)
  for t,x in self.outputs.items():T[abs(x)]=basis(T[abs(x)]+(t,))
  for x in sorted(self.active,reverse=True):
   if self.args[x]:
    for a in self.args[x]:T[abs(a)]=basis(T[abs(a)]+T[x])
  bad=[x for x in self.active if len(S[x])+len(T[x])>len(basis(S[x]+T[x]))]
  return dict(h=self.h,n=len(self.inputs),roles=sum(bool(self.args[x]) for x in self.active)+len(self.outputs),
    local_obstructions=len(bad),first_obstruction=dict(node=bad[0],S=S[bad[0]],T=T[bad[0]]) if bad else None,
    degenerate_sources=sum(not classify(S[x])['nondegenerate'] for x in self.active))

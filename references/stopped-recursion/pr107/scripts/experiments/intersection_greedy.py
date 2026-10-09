#!/usr/bin/env python3
"""Bounded exploratory global greedy factoring; no frame certificate.

Default sizes 12,16,20 intentionally stop before a costly full-size search.
"""
import sys,heapq,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from exclusion_circuit import ExclusionCircuit
from itertools import combinations
class Greedy(ExclusionCircuit):
 def __init__(self,n):
  self.n=n;self.inputs=list(combinations(range(n),3));p=len(self.inputs)
  bits=[sum(1<<x for x in t) for t in self.inputs]
  self.support=[0]+[1<<i for i in range(p)];self.args=[None]*(p+1)
  self.lookup={s:i for i,s in enumerate(self.support)};self.variables={v:i+1 for i,v in enumerate(self.inputs)}
  usage=[0]+[sum(1<<i for i,t in enumerate(bits) if (t&s).bit_count()==1) for s in bits]
  active=set(range(1,p+1));heap=[]
  for a in range(1,p+1):
   for b in range(a+1,p+1):
    score=(usage[a]&usage[b]).bit_count()
    if score>=2:heap.append((-score,a,b))
  heapq.heapify(heap);steps=0;start=time.time()
  while heap:
   neg,a,b=heapq.heappop(heap);mask=usage[a]&usage[b];score=mask.bit_count()
   if score<2:continue
   if score!=-neg:heapq.heappush(heap,(-score,a,b));continue
   new=self.add(a,b);assert new==len(usage)
   usage.append(mask);usage[a]^=mask;usage[b]^=mask
   for x in (a,b):
    if usage[x].bit_count()<2:active.discard(x)
   for x in active:
    score=(mask&usage[x]).bit_count()
    if score>=2:heapq.heappush(heap,(-score,x,new))
   active.add(new);steps+=1
   if steps%5000==0:print(n,steps,'active',len(active),'heap',len(heap),'secs',round(time.time()-start,1),flush=True)
  self.outputs={}
  for i,t in enumerate(self.inputs):self.outputs[t]=self.total([j for j,u in enumerate(usage) if u&(1<<i)])
  self.active=set();stack=list(self.outputs.values())
  while stack:
   x=stack.pop()
   if not x or x in self.active:continue
   self.active.add(x)
   if self.args[x]:stack.extend(self.args[x])
  self.additions=sum(self.args[x] is not None for x in self.active)
  for i,t in enumerate(self.outputs):assert self.support[self.outputs[t]]==sum(1<<j for j,s in enumerate(bits) if (bits[i]&s).bit_count()==1)
if __name__=='__main__':
 for n in map(int,sys.argv[1:] or ['12','16','20']):
  start=time.time();c=Greedy(n);print('RESULT',n,c.additions,len(c.outputs),c.additions/len(c.outputs),'time',time.time()-start,flush=True)

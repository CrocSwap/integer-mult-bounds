#!/usr/bin/env python3
"""Exploratory most-frequent-pair factoring; not the certified network.

Every output is still checked exactly. Greedy failure is not a lower bound.
"""
import sys,heapq,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from exclusion_circuit import ExclusionCircuit
from itertools import combinations
class Greedy(ExclusionCircuit):
 def __init__(self,n,limit=100000):
  self.n=n;self.inputs=list(combinations(range(n),2));p=len(self.inputs)
  self.support=[0]+[1<<i for i in range(p)];self.args=[None]*(p+1)
  self.lookup={s:i for i,s in enumerate(self.support)};self.variables={v:i+1 for i,v in enumerate(self.inputs)}
  usage=[0]+[sum(1<<i for i,t in enumerate(self.inputs) if not set(t)&set(s)) for s in self.inputs]
  active=set(range(1,p+1));heap=[]
  for a in range(1,p+1):
   for b in range(a+1,p+1):
    score=(usage[a]&usage[b]).bit_count()
    if score>=2:heap.append((-score,a,b))
  heapq.heapify(heap);steps=0;start=time.time()
  while heap and steps<limit:
   neg,a,b=heapq.heappop(heap);mask=usage[a]&usage[b];score=mask.bit_count()
   if score<2:continue
   if score!=-neg:heapq.heappush(heap,(-score,a,b));continue
   new=self.add(a,b)
   assert new==len(usage)
   usage.append(mask);usage[a]^=mask;usage[b]^=mask
   for x in (a,b):
    if usage[x].bit_count()<2:active.discard(x)
   for x in active:
    s=(mask&usage[x]).bit_count()
    if s>=2:heapq.heappush(heap,(-s,x,new))
   active.add(new);steps+=1
   if steps%1000==0:print(n,'step',steps,'score',score,'active',len(active),'heap',len(heap),'secs',round(time.time()-start,2),flush=True)
  self.outputs={}
  for i,t in enumerate(self.inputs):
   self.outputs[t]=self.total([j for j,u in enumerate(usage) if u&(1<<i)])
  self.active=set();stack=list(self.outputs.values())
  while stack:
   x=stack.pop()
   if not x or x in self.active:continue
   self.active.add(x)
   if self.args[x]:stack.extend(self.args[x])
  self.additions=sum(self.args[x] is not None for x in self.active)
if __name__=='__main__':
 for n in (15,25,45):
  c=Greedy(n);print('RESULT',c.verify(),flush=True)

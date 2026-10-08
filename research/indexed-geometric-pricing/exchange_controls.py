"""Small adversarial exchange graphs; these do not certify global optimality."""
from collections import Counter,defaultdict
from pathlib import Path
import json,sys

def basis(rows):
 out=[]
 for x in rows:
  for y in out:x=min(x,x^y)
  if x:out.append(x)
 return out

def independent(rows,x):
 for y in rows:x=min(x,x^y)
 return bool(x)

def run(depth,n,blocked=False):
 # Each region can retain exactly one unit. The alternative permutation is a cycle.
 edges=[(g,g,0) for g in range(n)]+[(g,(g+1)%n,0) for g in range(n)]
 chosen=set(range(n));right={g:g for g in range(n)}
 blocks=[{'selected':{g},'outbasis':[1] if blocked else []} for g in range(n)]
 # Blocked case uses a new input inside the existing output span, hence ineligible.
 if blocked:
  edges[:n]=[(g,g,1) for g in range(n)]
 prices=[10]*n+[1]*n;priority=sorted(range(2*n),key=lambda e:(prices[e],edges[e]));stats=Counter()
 def carry_can(e,drop=None):
  g,u,i=edges[e]
  return independent(basis(blocks[g]['outbasis']+[1<<edges[z][2] for z in blocks[g]['selected'] if z!=drop]),1<<i)
 ctx=dict(sys=sys,edges=edges,chosen=chosen,right=right,blocks=blocks,prices=prices,priority=priority,stats=stats,carry_can=carry_can,defaultdict=defaultdict,MAX_CYCLE=depth)
 code=Path('exchanges.txt').read_text();exec('if True:\n'+code,ctx)
 assert len(chosen)==len(right)==n
 for b in blocks:assert len(basis(b['outbasis']+[1<<edges[z][2] for z in b['selected']]))==len(b['outbasis'])+len(b['selected'])
 return {'depth':depth,'n':n,'blocked':blocked,'cost':sum(prices[e] for e in chosen),'stats':dict(stats)}
results=[run(2,2),run(2,3),run(3,3),run(3,3,True)]
assert [r['cost'] for r in results]==[2,30,3,30]

print('PASS two-cycle escape, three-cycle escape, depth restriction, output-span rejection')

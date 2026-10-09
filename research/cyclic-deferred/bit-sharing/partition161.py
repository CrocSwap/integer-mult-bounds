"""Exact cyclic partition into 161 orthogonal 11-triple sunflower classes.

Paley-tournament orientation selects one center in each translation orbit.
The remaining degree-two choice problem is solved by finite exact search;
seven perfect matchings of the resulting 7-regular bipartite graph give the
seven base classes. Every exported triple and Gram entry is checked.
"""
from itertools import combinations
from collections import Counter
from pathlib import Path
import json,time
p=23;QR={i*i%p for i in range(1,p)};NR=set(range(1,p))-QR

def pairs(T):return sorted({tuple(sorted((a-c)%p for a in T if a!=c))for c in T})
orbits={min(pairs(T)):pairs(T)for T in combinations(range(p),3)};assert len(orbits)==77
choices=[];forced=[]
for key,opts in sorted(orbits.items()):
 good=[e if e[0]in QR else(e[1],e[0])for e in opts if(e[0]in QR)!=(e[1]in QR)]
 assert len(good)in(1,3)
 if len(good)==1:forced.append(good[0])
 else:choices.append(tuple(good))
degree=Counter(x for e in forced for x in e);assert len(forced)==55 and len(choices)==22 and set(degree.values())=={5}
visits=0
def solve(todo,selected):
 global visits
 visits+=1
 if not todo:return selected if all(degree[x]==7 for x in range(1,p))else None
 valid={i:[e for e in choices[i]if all(degree[x]<7 for x in e)]for i in todo}
 if any(not es for es in valid.values()):return None
 for x in range(1,p):
  if degree[x]+sum(any(x in e for e in valid[i])for i in todo)<7:return None
 i=min(todo,key=lambda j:(len(valid[j]),j));rest=todo-{i}
 for e in sorted(valid[i],key=lambda e:(sum(degree[x]for x in e),e)):
  for x in e:degree[x]+=1
  r=solve(rest,selected+[e])
  if r is not None:return r
  for x in e:degree[x]-=1
 return None
started=time.time();selected=solve(set(range(len(choices))),[]);assert selected is not None
edges=set(forced+selected);assert len(edges)==77 and all(sum(x in e for e in edges)==7 for x in range(1,p))
base=[]
for _ in range(7):
 match={}
 def augment(a,seen):
  for b in sorted(y for x,y in edges if x==a):
   if b in seen:continue
   seen.add(b)
   if b not in match or augment(match[b],seen):match[b]=a;return True
  return False
 for a in sorted(QR):assert augment(a,set())
 M=sorted((a,b)for b,a in match.items());assert len(M)==11;edges-=set(M);base.append([(0,)+tuple(sorted(e))for e in M])
assert not edges
groups=[[tuple(sorted((x+c)%p for x in T))for T in G]for c in range(p)for G in base]
flat=[T for G in groups for T in G];assert len(groups)==161 and len(flat)==1771 and len(set(flat))==1771 and set(flat)==set(combinations(range(p),3))
for G in groups:assert all(len(set(A)&set(B))==1 for A,B in combinations(G,2))
D=Path(__file__).resolve().parent;(D/'groups161.json').write_text(json.dumps(groups)+'\n');(D/'partition161-receipt.json').write_text(json.dumps(dict(groups=161,size=11,translation_orbits=77,forced_choices=55,ternary_choices=22,search_visits=visits,seconds=time.time()-started,base_classes=base,exact_coverage=True,exact_rational_orthogonality=True),indent=2)+'\n');print('PASS',len(groups),'groups of11',visits,'search visits',time.time()-started,flush=True)

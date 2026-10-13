"""Exact finite tests of the projection/cut identity; standard library only."""
from pathlib import Path
from itertools import combinations,product
from collections import Counter
from random import Random
import json,argparse

def span(b):
 s={0}
 for v in b:s|={x^v for x in s}
 return frozenset(s)
spaces=sorted({span(b)for k in range(4)for b in combinations(range(1,8),k)},key=lambda s:(len(s),tuple(sorted(s))))
dim=lambda s:len(s).bit_length()-1
cost=lambda r:100*r-r*r
pairs=[(u,v)for u in spaces for v in spaces if u<=v]
projections=[(v,l)for v in range(1,8)for l in range(1,8)if(v&l).bit_count()%2]
def image(s,v,l):return frozenset(x^(v if(x&l).bit_count()%2 else 0)for x in s)
checked=0
for v,l in projections:
 for U,V in pairs:
  PU,PV=image(U,v,l),image(V,v,l);au,av=PU!=U,PV!=V;lu,lv=v in U,v in V;r=dim(V)-dim(U)
  assert dim(PU)==dim(U)-lu and dim(PV)==dim(V)-lv
  assert not lu or lv
  for x,y in product(range(2),repeat=2):
   if(x and not au)or(y and not av):continue
   X,Y=(PU if x else U),(PV if y else V)
   expected=not(au and av and((y and not x)or(x and not y and not lv)))
   assert (X<=Y)==expected
   if not expected:continue
   delta=cost(dim(Y)-dim(X))-cost(r)
   cut=(cost(r+1)-cost(r))*(x and not y)if lu and lv else -(cost(r)-cost(r-1))*y if lv else 0
   assert delta==cut,(U,V,v,l,x,y,delta,cut)
   checked+=1
rng=Random(1808);graph_cases=0;assignments=0
for case in range(36):
 F=sorted([rng.choice(spaces)for _ in range(8)],key=dim)
 edges=[(i,j)for i in range(8)for j in range(i+1,8)if F[i]<=F[j]and rng.random()<.48]
 if edges:edges.append(edges[0]) # parallel register edges must count twice
 fixed={i for i in range(8)if rng.random()<.2}
 for v,l in projections:
  P=[image(s,v,l)for s in F];a=[P[i]!=F[i]for i in range(8)];loss=[v in s for s in F];finite=[];hard=[];reward=0
  for i in fixed:
   if a[i]:hard.append((i,9))
  for u,w in edges:
   r=dim(F[w])-dim(F[u])
   if a[u]and a[w]:
    hard.append((w,u))
    if not loss[w]:hard.append((u,w))
   else:assert not a[u]
   if loss[u]and loss[w]:finite.append((u,w,cost(r+1)-cost(r)))
   elif loss[w]:
    c=cost(r)-cost(r-1);finite.append((8,w,c));reward+=c
  inf=1+sum(c for _,_,c in finite)
  base=sum(cost(dim(F[w])-dim(F[u]))for u,w in edges)
  best_actual=10**9;best_cut=10**9
  for bits in product(range(2),repeat=sum(a)):
   x=[0]*10;x[8]=1;k=0
   for i in range(8):
    if a[i]:x[i]=bits[k];k+=1
   Y=[P[i]if x[i]else F[i]for i in range(8)]
   legal=all(not x[i]for i in fixed)and all(Y[u]<=Y[w]for u,w in edges)
   cap=sum(c for u,w,c in finite if x[u]and not x[w])+inf*sum(x[u]and not x[w]for u,w in hard)
   if legal:
    delta=sum(cost(dim(Y[w])-dim(Y[u]))for u,w in edges)-base
    assert cap-reward==delta
    best_actual=min(best_actual,delta)
   best_cut=min(best_cut,cap-reward);assignments+=1
  assert best_cut==best_actual
  graph_cases+=1
result=dict(status='PASS',subspaces=len(spaces),projections=len(projections),legal_edge_assignments=checked,graph_cases=graph_cases,labelings=assignments,scope='Exact finite tests; universal proof is in PROJECTION-CUT-THEOREM.md. No Lean certification and no kappa gain asserted.')
ap=argparse.ArgumentParser();ap.add_argument('--output',type=str);args=ap.parse_args()
if args.output:Path(args.output).write_text(json.dumps(result,indent=2)+'\n',encoding='ascii')
print(json.dumps(result))


"""Independent finite corroboration; no author/predecessor imports.
Jerry Chen / @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
Universal conclusions rely on the separately reviewed written argument.
"""
from collections import defaultdict, Counter
from itertools import combinations
from pathlib import Path
import json,sys

def need(ok,msg):
 if not ok:raise ValueError(msg)
def off(x,y,w):return sum((y&~(1<<r))<<(w*r)for r in range(w)if x>>r&1)
def catalog(w):
 d=defaultdict(list)
 for x in range(1,1<<w):
  for y in range(1,1<<w):
   if(x&y).bit_count()%2:d[off(x,y,w)].append((x,y))
 return d
def span(vectors):
 s={0}
 for v in vectors:
  if v not in s:s|={x^v for x in s}
 return frozenset(s)
def irreducible(pool,V):
 for v in V-{0}:
  U={0,v};changed=True
  while changed and U!=V:
   changed=False
   for z in tuple(U):
    for x,y in pool:
     if(z&y).bit_count()%2 and x not in U:U|={u^x for u in U};changed=True
  if U!=V:return False
 return True
def columns(pair,basis):
 x,y=pair;coordinates={}
 for mask in range(1<<len(basis)):
  v=0
  for i,b in enumerate(basis):
   if mask>>i&1:v^=b
  need(v not in coordinates,'Independent basis');coordinates[v]=mask
 return tuple(coordinates[x]if(b&y).bit_count()%2 else 0 for b in basis)
def subspaces(w):
 levels=[{frozenset({0})}]
 for k in range(w):
  levels.append({frozenset(U|{x^v for x in U})for U in levels[-1]for v in range(1,1<<w)if v not in U})
 return levels
def explicit():
 d=catalog(5);P=span((1<<1,1<<13,off(26,21,5)));pool={n for p in P-{0}for n in d.get(p,[])}
 expected={(1,3),(3,2),(4,12),(12,8),(26,21)}
 need(sum(map(len,d.values()))==496 and pool==expected,'Complete width-five pool')
 need(sum(p.bit_count()==1 for p in P)==2,'Exactly two edges')
 normal={tuple(1<<i if i==j else 0 for j in range(5))for i in range(4)}|{(31,)*5}
 need({columns(n,[1,3,4,12,16])for n in pool}==normal,'Exact normal-form conjugation')
 levels=subspaces(5);need(list(map(len,levels))==[1,31,155,155,31,1],'Complete subspace lattice')
 proper=[U for level in levels[1:-1]for U in level]
 need(not any(all((x if(v&y).bit_count()%2 else 0)in U for v in U for x,y in pool)for U in proper),'No proper nonzero invariant')
 need(irreducible(pool,frozenset(range(32))),'Orbit-closure irreducibility')
 need(not irreducible(pool-{(26,21)},frozenset(range(32))),'Reducibility negative control')
 return dict(idempotents=496,pool_size=5,proper_subspaces=len(proper),conjugation=True)
def quotient(w):
 d=catalog(w);items=[(x,y,p)for p,ns in d.items()if p for x,y in ns];tests=0
 for p,ns in d.items():
  if p:need(len(ns)==(2 if p.bit_count()==1 else 1),'Finite fiber control')
 for U in range(1<<w):
  inside=sum(1<<(w*r+c)for r in range(w)for c in range(w)if r!=c and U>>r&1 and U>>c&1);outside=((1<<w)-1)^U
  for (x,y,p),(u,v,q)in combinations(items,2):
   if(p^q)&~inside:continue
   xx,uu=x&outside,u&outside
   if not xx or not uu or xx==uu:continue
   need(p==q and p.bit_count()==1,'Quotient observation common edge')
   a,b=divmod(p.bit_length()-1,w);need(not(U>>a&1)and not(U>>b&1),'Endpoints outside U');tests+=1
 return dict(width=w,nonvacuous_independent_image_pairs=tests)
def two_edges(w):
 d=catalog(w);normal={tuple(1<<i if i==j else 0 for j in range(5))for i in range(4)}|{(31,)*5};result={}
 for name,(a,b),(c,e)in [('disjoint',(0,1),(2,3)),('same_source',(0,1),(0,2)),('same_target',(1,0),(2,0)),('path',(0,1),(1,2)),('opposite',(0,1),(1,0))]:
  p,q=1<<(w*a+b),1<<(w*c+e);E=(1<<a)|(1<<b)|(1<<c)|(1<<e);spaces={span((p,q,z))for z in d if z not in(0,p,q,p^q)};count=irred=0;dims=Counter()
  for P in spaces:
   if sum(z.bit_count()==1 for z in P)!=2:continue
   pool={n for z in P-{0}for n in d.get(z,[])};V=span(x for x,y in pool);outside={x&~E for x in V};dim=len(V).bit_length()-1
   need(len(outside)<=2,'One-dimensional quotient');need(dim<=E.bit_count()+1,'All generated joint-image bounds');count+=1;dims[dim]+=1
   if dim==5 and irreducible(pool,V):
    need(name=='disjoint','Only disjoint endpoints give five dimensions');z=next(v for v in outside if v)
    need({columns(n,[1,3,4,12,z])for n in pool}==normal,'Unique irreducible five-dimensional form');irred+=1
  result[name]=dict(spaces=count,image_dimensions=dict(dims),irreducible_five_dimensional=irred)
 return dict(width=w,classes=result)
def three_edges(w):
 d=catalog(w);units=[1<<(w*a+b)for a in range(w)for b in range(w)if a!=b];count=checks=maxdim=0
 for edges in combinations(units,3):
  P=span(edges);pool={n for p in P-{0}for n in d.get(p,[])};adj=[{i}for i in range(w)]
  for p in edges:a,b=divmod(p.bit_length()-1,w);adj[a].add(b);adj[b].add(a)
  unseen=set(range(w));components=[]
  while unseen:
   U={next(iter(unseen))};old=set()
   while old!=U:old=U.copy();U|={v for u in old for v in adj[u]}
   unseen-=U;components.append(sum(1<<i for i in U))
  for x,y in pool:
   need(any((x|y)&~U==0 for U in components),'Single component support');need((x|y).bit_count()<=4,'At most four vertices');checks+=1
  maxdim=max(maxdim,len(span(x for x,y in pool)).bit_length()-1);count+=1
 return dict(width=w,spaces=count,projector_support_checks=checks,max_total_image_dimension=maxdim)
def main():
 result=dict(explicit=explicit(),quotient=[quotient(w)for w in(3,4,5)],two_edge_generated_spaces=[two_edges(w)for w in(5,6)],three_edges=three_edges(6),scope='Independent finite corroboration; no primary/predecessor imports; universal claims require the written proof.')
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('PASS_INDEPENDENT_THREE_PATTERN_REVIEW',json.dumps(result,sort_keys=True))
if __name__=='__main__':main()

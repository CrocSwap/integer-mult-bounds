"""Verify the coset facts in independent standard E8 coordinates."""
from standard_e8 import *

def exact_rank(rows):
 piv={}
 for raw in rows:
  z=list(map(Fraction,raw))
  for k,u in sorted(piv.items()):
   f=z[k];z=[x-f*y for x,y in zip(z,u)]
  if any(z):
   k=next(k for k,x in enumerate(z) if x);f=z[k];piv[k]=[x/f for x in z]
 return len(piv)

def certified_rank(rows):
 r=rank_mod(rows)
 return 8 if r==8 else exact_rank(rows)

def support(x):return [j for j in range(120) if x>>j&1]
assert all(certified_rank([roots[j] for j in support(c)])==8 for c in C[1:])
report=[]
for d in range(8):
 n=nullvec([r for j,r in enumerate(a) if j!=d]);H=[j for j,r in enumerate(roots) if not dot(r,n)]; O=[j for j in range(120) if j not in H]
 good={c for c in C if certified_rank([roots[j] for j in O if c>>j&1])<8}
 if len(H)==63:
  nq=[j for j in O if all(dot(roots[j],roots[k])==0 for k in H)];assert len(nq)==1
  t=K[nq[0]];assert set(support(t))==set(H+nq)
  expected={0,t}|{K[q]^s for q in H for s in (0,t)}
  shifts=(0,t)
  neigh={q:{r for r in H if q!=r and dot(roots[q],roots[r])!=0} for q in H}
  assert all(exact_rank([roots[r] for r in neigh[q]])==7 for q in H)
  common=[len(neigh[q]&neigh[r]) for q,r in combinations(H,2)]
  assert min(common)>0
 else:
  expected={0}|{K[q] for q in H};shifts=(0,);common=[]
 assert good==expected
 for q in H:
  for s in shifts:
   rs=[roots[j] for j in O if (K[q]^s)>>j&1]
   assert exact_rank(rs)==7 and all(dot(roots[q],r)==0 for r in rs)
 report.append({'deleted':d,'flat_roots':len(H),'good_count':len(good),'common_neighbor_counts':sorted(set(common))})
print(json.dumps(report,indent=2))
Path(__file__).with_name('independent-structure-result.json').write_text(json.dumps({'verified':True,'hyperplanes':report},indent=2)+'\n')

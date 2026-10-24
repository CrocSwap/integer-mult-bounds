"""Check an exact similarity between both coordinate systems."""
from standard_e8 import *
from itertools import permutations
import gzip
p=Path(__file__).resolve().parents[1]/'inputs/bit-word.json.gz'
ham=json.load(gzip.open(p,'rt'))['lines']
def normalize(r):
 r=tuple(r)
 return tuple(-x for x in r) if next(x for x in r if x)<0 else r
positive={normalize(r) for r in ham}
simple=sorted(q for q in positive if not any(tuple(x-y for x,y in zip(q,r)) in positive for r in positive))
assert len(simple)==8
perm=next(p for p in permutations(range(8)) if all(dot(a[i],a[j])==2*dot(simple[p[i]],simple[p[j]]) for i in range(8) for j in range(8)))
rows=[[Fraction(x) for x in a[i]+simple[perm[i]]] for i in range(8)]
for j in range(8):
 k=next(k for k in range(j,8) if rows[k][j]);rows[k],rows[j]=rows[j],rows[k]
 z=rows[j][j];rows[j]=[x/z for x in rows[j]]
 for k in range(8):
  if k!=j:
   z=rows[k][j];rows[k]=[x-z*y for x,y in zip(rows[k],rows[j])]
T=[r[8:] for r in rows]
image={normalize([sum(Fraction(r[j])*T[j][k] for j in range(8)) for k in range(8)]) for r in roots}
assert image==positive
assert all(dot(T[i],T[j])==Fraction(int(i==j),2) for i in range(8) for j in range(8))
out={'verified':True,'root_lines':120,'rational_similarity_factor':'1/2','simple_root_permutation':perm,'matrix':[[str(x) for x in r] for r in T]}
Path(__file__).with_name('independent-coordinate-map.json').write_text(json.dumps(out,indent=2)+'\n')
print('Verified all 120 root lines under an exact rational similarity.')

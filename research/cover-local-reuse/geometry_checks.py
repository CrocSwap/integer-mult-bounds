"""Independent finite checks of PR130's written Clifford and cover identities.
Not an all-size streaming proof or replacement for source verification.
"""
from pathlib import Path
from itertools import combinations
from functools import lru_cache
import json,time,hashlib,sys
if sys.flags.optimize:raise ValueError('Exact geometry requires assertions')
D=Path(__file__).parent

def basis(rows):
 p={}
 for x in rows:
  for j in sorted(p,reverse=True):
   if x>>j&1:x^=p[j]
  if x:
   j=x.bit_length()-1
   for k in p:
    if p[k]>>j&1:p[k]^=x
   p[j]=x
 return tuple(p[j]for j in sorted(p,reverse=True))

def perp(U,h):
 U=basis(U);p={x.bit_length()-1:x for x in U};out=[]
 for j in range(h):
  if j not in p:
   x=1<<j
   for k,row in p.items():
    if row>>j&1:x|=1<<k
   out.append(x)
 return basis(out)

def app(C,x):
 y=0
 while x:
  z=x&-x;x-=z;y^=C[z.bit_length()-1]
 return y

def mul(A,B):return tuple(app(A,b)for b in B)

def inverse(C):
 n=len(C);rows=[sum(((C[j]>>i)&1)<<j for j in range(n))|(1<<(n+i))for i in range(n)]
 for i in range(n):
  j=next(j for j in range(i,n)if rows[j]>>i&1);rows[i],rows[j]=rows[j],rows[i]
  for j in range(n):
   if j!=i and rows[j]>>i&1:rows[j]^=rows[i]
 assert all(rows[i]&((1<<n)-1)==1<<i for i in range(n))
 return tuple(sum(((rows[i]>>(n+j))&1)<<i for i in range(n))for j in range(n))

def trans(C):return tuple(sum(((C[i]>>j)&1)<<i for i in range(len(C)))for j in range(len(C)))
def image(C,U):return basis(app(C,x)for x in U)
def contains(U,V):return len(basis(U+V))==len(V)
def lag(U,h):return basis(tuple(u|(u<<h)for u in U)+tuple(v<<h for v in perp(U,h)))
def intersectdim(U,V):return len(U)+len(V)-len(basis(U+V))
def sympair(x,y,h):
 mask=(1<<h)-1
 return (((x&mask)&(y>>h)).bit_count()+((y&mask)&(x>>h)).bit_count())&1

def subspaces(h):
 spaces={()};todo=[()]
 for U in todo:
  for x in range(1,1<<h):
   V=basis(U+(x,))
   if V not in spaces:spaces.add(V);todo.append(V)
 return sorted(spaces,key=lambda U:(len(U),U))

records=[]
for h in (1,2,3,4):
 mask=(1<<h)-1;L0=tuple(1<<(h+i)for i in range(h));LF=tuple((1<<i)|(1<<(h+i))for i in range(h))
 F=tuple(1<<i for i in range(h))+LF
 spaces=subspaces(h);T={};labels={};complements={};degenerate=0
 for U in spaces:
  r=len(U);cols=list(U)
  for i in range(h):
   if not contains((1<<i,),basis(cols)):cols.append(1<<i)
  assert len(cols)==h
  G=tuple(cols);GiT=trans(inverse(G))
  K=tuple(G[i]|((G[i]^GiT[i])<<h)for i in range(h))+tuple(c<<h for c in GiT)
  assert all(sympair(K[i],K[j],h)==int((i<h and j==i+h)or(j<h and i==j+h))for i in range(2*h)for j in range(2*h))
  assert image(K,L0)==basis(L0) and image(K,LF)==basis(LF)
  CE=tuple(1<<i for i in range(h))+tuple((1<<(h+i))|((1<<i)if i<r else 0)for i in range(h))
  TU=mul(mul(K,CE),inverse(K));T[U]=TU;labels[U]=lag(U,h);complements[U]=basis(G[r:])
  assert image(inverse(TU),L0)==labels[U]
  assert len(basis(c&mask for c in TU[h:]))==r
  assert image(F,labels[U])==lag(perp(U,h),h)
  assert image(inverse(TU),LF)==lag(complements[U],h)
  assert mul(TU,TU)==tuple(1<<i for i in range(2*h))
  degenerate+=len(basis(sum(((x&y).bit_count()&1)<<j for j,y in enumerate(U))for x in U))<r
 nested=0
 for U in spaces:
  for V in spaces:
   distance=h-intersectdim(labels[U],labels[V]);expected=len(U)+len(V)-2*intersectdim(U,V)
   assert distance==expected
   assert len(basis(c&mask for c in mul(T[V],inverse(T[U]))[h:]))==expected
   if contains(U,V):
    nested+=1
    tail=mul(mul(F,T[U]),inverse(T[V]))
    assert len(basis(c&mask for c in tail[h:]))==h-len(V)+len(U)
   DU=mul(T[U],F);DV=mul(T[V],F)
   assert mul(DU,inverse(DV))==mul(T[U],inverse(T[V]))
 records.append(dict(h=h,all_subspaces=len(spaces),degenerate_subspaces=degenerate,all_ordered_pairs=len(spaces)**2,nested_tail_pairs=nested))
 print('Clifford',records[-1],flush=True)

h=22;m=3*h-2;A=tuple(1<<i for i in range(h));B=tuple(1<<i for i in range(h,2*h-1));C=tuple(1<<i for i in range(2*h-1,m));E=basis(A+B+C)
checks=0
for triple in combinations(range(h),3):
 q=sum(1<<i for i in triple);d=next(i for i in range(h)if i not in triple);w=q^(1<<d)
 Aq=tuple((1<<i)^(w if w>>i&1 else 0)for i in range(h)if i!=d)
 assert all(((x&y).bit_count()&1)==int(i==j)for i,x in enumerate(Aq)for j,y in enumerate(Aq))
 assert all(not((x&q).bit_count()&1)for x in Aq)
 def swap(other,fixed):
  cols=[(q if q>>j&1 else 0)^sum((other[i] if u>>j&1 else 0)for i,u in enumerate(Aq))for j in range(h)]
  for axis in (B,C):cols.extend(Aq if axis==other else axis)
  R=tuple(cols)
  assert app(R,q)==q and mul(R,R)==tuple(1<<i for i in range(m))
  assert all(((x&y).bit_count()&1)==int(i==j)for i,x in enumerate(R)for j,y in enumerate(R))
  return R
 R12=swap(B,C);R23=swap(C,B)
 assert image(R12,A)==basis(B+(q,)) and image(R12,Aq)==basis(B)
 assert image(R23,A)==basis(C+(q,)) and image(R23,B+C)==basis(B+Aq)
 # All six data segments telescope without a positive-rank connector.
 stages=[((q,),basis(B+(q,)),(),basis(B)),(basis(B+(q,)),basis(A+B),basis(B),basis(Aq+B)),(basis(A+B),E,basis(Aq+B),basis(Aq+B+C))]
 for xs,xe,ys,ye in stages:assert contains(xs,xe)and contains(ys,ye)
 assert stages[-1][3]==perp((q,),m)
 checks+=1
print('Cayley actual h22 triples',checks,flush=True)
P=D.resolve().parents[1]
files=['notes/general-clifford-frames.tex','notes/three-stage-cover-complex.tex','notes/three-stage-cover-note.tex']
out=dict(status='PASS independent exact binary symplectic and actual h22 port geometry',clifford_checks=records,actual_port_triples_checked=checks,
 source_sha256={f:hashlib.sha256((P/f).read_bytes()).hexdigest()for f in files},
 scope='Finite checks substantiate the written all-subspace algebra and all selected port identities. They do not verify exact operator phases or all-size fixed-tape/weighted-bit interfaces.',
 source_review_findings=['K_G fixes L0 and LF, transports L_U, and has rank-zero adapters; arbitrary degenerate subspaces are allowed.', 'Dirty-tail Fourier rank holds for direct complement V_sigma, without claiming V_sigma=sigma_perp.', 'Reverse D_U=T_U F_inverse transitions cancel exactly at operator level.', 'The three Cayley port maps preserve source line and make every adjacent data frame equal.', 'Rank-zero adapters reconcile exact representatives; full finite router bound must remain paid.'],publication_blocker_in_reviewed_scope=None)
(D/'geometry-audit.json').write_text(json.dumps(out,indent=2)+'\n')
